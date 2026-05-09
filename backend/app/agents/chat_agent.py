from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from app.agents.approval import ApprovalBridge
from app.agents.events import AgentEvent, error_event, summarize_value
from app.config import get_settings

try:  # pragma: no cover - exercised only when the SDK is installed.
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher
except ImportError:  # pragma: no cover - gives callers a clear runtime error.
    ClaudeAgentOptions = None  # type: ignore[assignment]
    ClaudeSDKClient = None  # type: ignore[assignment]
    HookMatcher = None  # type: ignore[assignment]


SYSTEM_PROMPT = """
Sos Pampa, un agente financiero conversacional para usuarios de Argentina.
Hablas en espanol natural, con tono claro y directo.

Reglas de seguridad:
- Podes usar herramientas de lectura para entender balances, activos e historial.
- Antes de cualquier operacion que mueva dinero o ejecute una trade, explica que vas a hacer.
- Nunca digas que una operacion fue ejecutada hasta que el resultado de la herramienta lo confirme.
- Si el usuario rechaza una accion, respetalo y ofrece ajustar el plan.
- Si falta informacion critica para una operacion financiera, pregunta antes de actuar.
""".strip()


WALLBIT_MCP_URL = "https://api.dev.wallbit.io"
WALLBIT_READ_TOOLS = [
    "mcp__wallbit__get_checking_balance",
    "mcp__wallbit__get_stocks_balance",
    "mcp__wallbit__list_transactions",
    "mcp__wallbit__get_asset",
]
WALLBIT_WRITE_TOOLS = [
    "mcp__wallbit__create_trade",
]
WALLBIT_TOOLS = WALLBIT_READ_TOOLS + WALLBIT_WRITE_TOOLS


async def _allow_pre_tool_use_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, bool]:
    del input_data, tool_use_id, context
    return {"continue_": True}


class ChatAgentSession:
    def __init__(
        self,
        *,
        system_prompt: str = SYSTEM_PROMPT,
        wallbit_mcp_url: str | None = None,
        approval_bridge: ApprovalBridge | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._wallbit_mcp_url = wallbit_mcp_url or get_settings().wallbit_mcp_url
        self._approval_bridge = approval_bridge or ApprovalBridge()
        self._client: Any | None = None
        self._connected = False
        self._turn_lock = asyncio.Lock()

    @property
    def connected(self) -> bool:
        return self._connected

    async def connect(self) -> None:
        if self._connected:
            return

        if ClaudeSDKClient is None or ClaudeAgentOptions is None:
            raise RuntimeError(
                "claude-agent-sdk is not installed. Install backend dependencies "
                "before starting the live chat."
            )

        pre_tool_use_hook = (
            HookMatcher(hooks=[_allow_pre_tool_use_hook])
            if HookMatcher is not None
            else {"matcher": {}, "hooks": [_allow_pre_tool_use_hook]}
        )
        wallbit_headers = self._wallbit_headers()
        options = ClaudeAgentOptions(
            system_prompt=self._system_prompt,
            include_partial_messages=True,
            mcp_servers={
                "wallbit": {
                    "type": "http",
                    "url": self._wallbit_mcp_url,
                    **({"headers": wallbit_headers} if wallbit_headers else {}),
                }
            },
            strict_mcp_config=True,
            permission_mode="default",
            allowed_tools=WALLBIT_TOOLS,
            can_use_tool=self._approval_bridge.can_use_tool,
            hooks={
                "PreToolUse": [pre_tool_use_hook]
            },
        )
        self._client = ClaudeSDKClient(options=options)
        await self._client.connect()
        self._connected = True

    def _wallbit_headers(self) -> dict[str, str]:
        api_key = get_settings().wallbit_api_key
        if not api_key:
            return {}
        return {"X-API-Key": api_key}

    async def disconnect(self) -> None:
        if self._client is not None:
            await self._client.disconnect()
        self._client = None
        self._connected = False

    async def get_status(self) -> AgentEvent:
        if self._client is None:
            return AgentEvent(
                "session_status",
                {"status": "disconnected", "mcp": None},
            )

        mcp_status = None
        get_mcp_status = getattr(self._client, "get_mcp_status", None)
        if get_mcp_status is not None:
            mcp_status = await get_mcp_status()

        return AgentEvent(
            "session_status",
            {"status": "connected" if self._connected else "disconnected", "mcp": mcp_status},
        )

    def resolve_approval(self, approval_id: str, decision: str) -> bool:
        return self._approval_bridge.resolve(approval_id, decision)

    async def interrupt(self) -> AgentEvent:
        if self._client is None:
            return AgentEvent("session_status", {"status": "disconnected"})

        interrupt = getattr(self._client, "interrupt", None)
        if interrupt is None:
            return AgentEvent(
                "session_status",
                {"status": "interrupt_unavailable"},
            )

        await interrupt()
        return AgentEvent("session_status", {"status": "interrupted"})

    async def send_user_message(self, text: str) -> AsyncIterator[AgentEvent]:
        if not text.strip():
            return

        await self.connect()

        async with self._turn_lock:
            queue: asyncio.Queue[AgentEvent | None] = asyncio.Queue()

            async def emit(event: AgentEvent) -> None:
                await queue.put(event)

            self._approval_bridge.set_event_sink(emit)
            task = asyncio.create_task(self._pump_turn(text, queue))

            try:
                while True:
                    event = await queue.get()
                    if event is None:
                        break
                    yield event
                await task
            finally:
                self._approval_bridge.clear_event_sink()

    async def _pump_turn(
        self,
        text: str,
        queue: asyncio.Queue[AgentEvent | None],
    ) -> None:
        try:
            if self._client is None:
                raise RuntimeError("Agent client is not connected.")

            await self._client.query(text)
            async for message in self._client.receive_response():
                for event in normalize_sdk_message(message):
                    await queue.put(event)
        except Exception as exc:  # noqa: BLE001 - bridge all runtime failures to chat.
            await queue.put(error_event(str(exc), details=exc.__class__.__name__))
        finally:
            await queue.put(None)


def normalize_sdk_message(message: Any) -> list[AgentEvent]:
    events: list[AgentEvent] = []
    message_type = message.__class__.__name__

    if message_type == "StreamEvent":
        events.extend(_normalize_stream_event(message))
        return events

    content = getattr(message, "content", None)
    if isinstance(content, list):
        text_parts: list[str] = []
        for block in content:
            block_type = block.__class__.__name__
            text = getattr(block, "text", None)
            if block_type == "TextBlock" and isinstance(text, str):
                text_parts.append(text)
            elif block_type == "ToolUseBlock":
                events.append(
                    AgentEvent(
                        "tool_call_started",
                        {
                            "tool_use_id": getattr(block, "id", None),
                            "tool_name": getattr(block, "name", None),
                            "input_summary": summarize_value(getattr(block, "input", None)),
                        },
                    )
                )
            elif block_type == "ToolResultBlock":
                events.append(
                    AgentEvent(
                        "tool_call_finished",
                        {
                            "tool_use_id": getattr(block, "tool_use_id", None),
                            "is_error": bool(getattr(block, "is_error", False)),
                            "result_summary": summarize_value(getattr(block, "content", None)),
                        },
                    )
                )

        if text_parts:
            events.append(AgentEvent("agent_message", {"text": "".join(text_parts)}))

    subtype = getattr(message, "subtype", None)
    if message_type == "ResultMessage" and subtype not in {None, "success"}:
        events.append(
            AgentEvent(
                "error",
                {
                    "message": f"Claude SDK result: {subtype}",
                    "details": getattr(message, "error", None),
                },
            )
        )

    return events


def _normalize_stream_event(event: Any) -> list[AgentEvent]:
    event_type = getattr(event, "type", None)
    delta = getattr(event, "delta", None)
    content_block = getattr(event, "content_block", None)

    if event_type == "content_block_delta" and delta is not None:
        text = getattr(delta, "text", None)
        if isinstance(text, str) and text:
            return [AgentEvent("agent_token", {"text": text})]

    if event_type == "content_block_start" and content_block is not None:
        if content_block.__class__.__name__ == "ToolUseBlock":
            return [
                AgentEvent(
                    "tool_call_started",
                    {
                        "tool_use_id": getattr(content_block, "id", None),
                        "tool_name": getattr(content_block, "name", None),
                        "input_summary": summarize_value(
                            getattr(content_block, "input", None)
                        ),
                    },
                )
            ]

    return []
