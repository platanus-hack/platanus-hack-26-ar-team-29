from __future__ import annotations

import asyncio
import datetime as _dt
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.agents.events import AgentEvent, error_event, format_tool_name, summarize_value
from app.agents.interactions import UserInteractionBridge
from app.agents.wallbit_tools import wallbit_mcp_server

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.api.ws.manager import ConnectionManager


try:  # pragma: no cover - exercised only when the SDK is installed.
    from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, HookMatcher
except ImportError:  # pragma: no cover - gives callers a clear runtime error.
    ClaudeAgentOptions = None  # type: ignore[assignment]
    ClaudeSDKClient = None  # type: ignore[assignment]
    HookMatcher = None  # type: ignore[assignment]


SYSTEM_PROMPT = """
Sos OpenFi, un agente financiero conversacional para usuarios de Argentina.
Hablas en castellano rioplatense natural, con tono claro y directo.

Reglas de seguridad:
- Podes usar herramientas de lectura libremente para entender balances, activos
  e historial.
- Si falta informacion critica (símbolo, cantidad/monto, moneda, tipo de orden),
  usa AskUserQuestion con 2 a 4 opciones cortas en vez de preguntar con texto
  largo. Despues de recibir la respuesta, continua el flujo sin repetir la
  pregunta y sin terminar el turno.

Flujo de trade (CRITICO — leelo y seguilo al pie de la letra):
- Cuando tengas todos los datos necesarios para una compra/venta, **llama
  directamente** a la tool `mcp__wallbit__create_trade`. NO escribas en texto
  "¿confirmás?" o "¿querés que compre X?" antes de llamar al tool.
- El backend intercepta la llamada al tool y le muestra al usuario un modal con
  botones **Aprobar / Rechazar**. Esa es la confirmacion oficial. Si en lugar
  de llamar al tool preguntas "¿confirmás?" en texto, el modal NUNCA aparece y
  el usuario queda colgado: eso es un bug grave.
- ANTES de llamar al tool, NO des por hecho que la operacion se va a ejecutar. Usa frases como "Acá te preparé la orden para que la revises:" o "Te dejo los detalles de la operación para que confirmes:". NUNCA digas "Voy a comprar..." ni "Ejecutando compra...", presentalo siempre como una propuesta.
- El turno tiene que terminar con la **invocacion del tool**, no con una pregunta al usuario.
- NUNCA digas que una operacion fue ejecutada hasta que el resultado del tool lo confirme.
- Si el tool devuelve que el usuario rechazó la operación en el modal, respondé de forma natural (ej. "Entendido, operación cancelada.") y ofrece ajustar los parámetros.

La herramienta de trading se llama `mcp__wallbit__create_trade`. Esta
disponible y conectada — nunca digas lo contrario.
""".strip()


WALLBIT_READ_TOOLS = [
    "get_checking_balance",
    "get_stocks_balance",
    "list_transactions",
    "get_asset",
    "mcp__wallbit__get_checking_balance",
    "mcp__wallbit__get_stocks_balance",
    "mcp__wallbit__list_transactions",
    "mcp__wallbit__get_asset",
]
WALLBIT_WRITE_TOOLS = [
    "create_trade",
    "mcp__wallbit__create_trade",
]
WALLBIT_TOOLS = WALLBIT_READ_TOOLS + WALLBIT_WRITE_TOOLS
AGENT_UI_TOOLS = ["AskUserQuestion"]
AUTO_ALLOWED_TOOLS = WALLBIT_READ_TOOLS
AGENT_MODEL = "haiku"
AGENT_FALLBACK_MODEL = "sonnet"


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
        approval_bridge: UserInteractionBridge | None = None,
    ) -> None:
        self._system_prompt = system_prompt
        self._approval_bridge = approval_bridge or UserInteractionBridge()
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
        options = ClaudeAgentOptions(
            model=AGENT_MODEL,
            fallback_model=AGENT_FALLBACK_MODEL,
            system_prompt=self._system_prompt,
            include_partial_messages=True,
            mcp_servers={"wallbit": wallbit_mcp_server()},
            strict_mcp_config=True,
            permission_mode="default",
            allowed_tools=AUTO_ALLOWED_TOOLS,
            can_use_tool=self._approval_bridge.can_use_tool,
            hooks={"PreToolUse": [pre_tool_use_hook]},
        )
        self._client = ClaudeSDKClient(options=options)
        await self._client.connect()
        self._connected = True

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

    def resolve_input(self, input_id: str, selected_options: list[str] | str) -> bool:
        return self._approval_bridge.resolve_input(input_id, selected_options)

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
                tool_name = getattr(block, "name", None)
                events.append(
                    AgentEvent(
                        "tool_call_started",
                        {
                            "tool_use_id": getattr(block, "id", None),
                            "tool_name": tool_name,
                            "tool_label": format_tool_name(tool_name),
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
            tool_name = getattr(content_block, "name", None)
            return [
                AgentEvent(
                    "tool_call_started",
                    {
                        "tool_use_id": getattr(content_block, "id", None),
                        "tool_name": tool_name,
                        "tool_label": format_tool_name(tool_name),
                        "input_summary": summarize_value(getattr(content_block, "input", None)),
                    },
                )
            ]

    return []


class ChatAgent:
    def __init__(self, manager: ConnectionManager, agent_tasks: set[asyncio.Task]) -> None:
        self.manager = manager
        self.agent_tasks = agent_tasks
        self._sessions: dict[UUID, ChatAgentSession] = {}
        self._plan_to_approval: dict[UUID, tuple[UUID, str]] = {}

    def get_session(self, session_id: UUID) -> ChatAgentSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ChatAgentSession()
        return self._sessions[session_id]

    def resolve_plan_approval(self, plan_id: UUID, decision: str) -> bool:
        if plan_id not in self._plan_to_approval:
            return False
        session_id, approval_id = self._plan_to_approval[plan_id]
        agent_session = self.get_session(session_id)
        return agent_session.resolve_approval(approval_id, decision)

    async def run_turn(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        user_content: str,
        sessionmaker: async_sessionmaker[AsyncSession],
        generate_title: bool = False,
    ) -> None:
        agent_session = self.get_session(session_id)

        if generate_title:
            task = asyncio.create_task(self._generate_title(session_id, user_content, sessionmaker))
            self.agent_tasks.add(task)
            task.add_done_callback(self.agent_tasks.discard)

        full_text = []

        async for event in agent_session.send_user_message(user_content):
            if event.type == "agent_token":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "chat_token",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "delta": event.payload["text"],
                    },
                )
            elif event.type == "tool_call_started":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "tool_call_started",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "tool_use_id": event.payload.get("tool_use_id"),
                        "tool_name": event.payload.get("tool_name"),
                        "tool_label": event.payload.get("tool_label"),
                        "input_summary": event.payload.get("input_summary"),
                    },
                )
            elif event.type == "tool_call_finished":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "tool_call_finished",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "tool_use_id": event.payload.get("tool_use_id"),
                        "is_error": event.payload.get("is_error"),
                        "result_summary": event.payload.get("result_summary"),
                    },
                )
            elif event.type == "agent_message":
                text = event.payload.get("text", "")
                full_text.append(text)
                await self.manager.broadcast_to_session(
                    session_id, {"type": "agent_message", "text": text}
                )
            elif event.type == "input_requested":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "input_requested",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "input_id": event.payload.get("input_id"),
                        "title": event.payload.get("title"),
                        "question": event.payload.get("question"),
                        "options": event.payload.get("options"),
                        "multi_select": event.payload.get("multi_select"),
                    },
                )
            elif event.type == "input_resolved":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "input_resolved",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "input_id": event.payload.get("input_id"),
                        "selected_options": event.payload.get("selected_options"),
                    },
                )
            elif event.type == "approval_requested":
                async with sessionmaker() as db:
                    from app.persistence.repositories.plans import PlanRepository

                    repo = PlanRepository(db)
                    plan = await repo.create_plan(
                        user_id=user_id,
                        origin_session_id=session_id,
                        origin_message_id=None,
                        steps_data=[
                            {
                                "tool_name": event.payload["tool_name"],
                                "args": event.payload["input"],
                                "human_description_es": "Aprobar " + event.payload["tool_name"],
                            }
                        ],
                        expires_at=_dt.datetime.now(_dt.UTC) + _dt.timedelta(minutes=15),
                    )

                    self._plan_to_approval[plan.id] = (session_id, event.payload["approval_id"])

                    from app.persistence.repositories.chat import ChatRepository

                    chat_repo = ChatRepository(db)
                    await chat_repo.create_message(
                        session_id=session_id,
                        user_id=user_id,
                        author="agent",
                        kind="plan_proposal",
                        content_blocks=[],
                        turn_id=turn_id,
                        plan_id=plan.id,
                    )
                    await db.commit()

                from app.services.plans import _plan_to_dict

                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "plan_proposed",
                        "session_id": str(session_id),
                        "plan_id": str(plan.id),
                        "plan": _plan_to_dict(plan),
                    },
                )
            elif event.type == "error":
                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "error",
                        "message_en": event.payload.get("message"),
                        "code": "AGENT_ERROR",
                    },
                )

        final_text = "".join(full_text)
        if final_text:
            async with sessionmaker() as db:
                from app.persistence.repositories.chat import ChatRepository

                chat_repo = ChatRepository(db)
                msg = await chat_repo.create_message(
                    session_id=session_id,
                    user_id=user_id,
                    author="agent",
                    kind="text",
                    content_blocks=[{"type": "text", "text": final_text}],
                    turn_id=turn_id,
                )
                await db.commit()

                from app.services.chat import _message_to_api

                api_msg = _message_to_api(msg)

            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "chat_message",
                    "session_id": str(session_id),
                    "turn_id": str(turn_id),
                    "message": api_msg,
                },
            )

        await self.manager.broadcast_to_session(
            session_id,
            {"type": "turn_complete", "session_id": str(session_id), "turn_id": str(turn_id)},
        )

    async def _generate_title(
        self,
        session_id: UUID,
        user_content: str,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        try:
            from anthropic import AsyncAnthropic

            from app.config import get_settings

            settings = get_settings()
            client = AsyncAnthropic(api_key=settings.anthropic_api_key)

            prompt = f"Genera un titulo muy corto de maximo 4 palabras para esta conversacion de un usuario con un agente financiero. Solo responde con el titulo, sin comillas ni puntos finales. El mensaje del usuario es: '{user_content}'"

            response = await client.messages.create(
                model=settings.anthropic_model,
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}],
            )

            if response.content and hasattr(response.content[0], "text"):
                title = response.content[0].text.strip()

                async with sessionmaker() as db:
                    from app.persistence.repositories.chat import ChatRepository

                    chat_repo = ChatRepository(db)
                    await chat_repo.update_session_title(session_id, title)
                    await db.commit()

                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "chat_title_updated",
                        "session_id": str(session_id),
                        "title": title,
                    },
                )
        except Exception as exc:
            import structlog

            log = structlog.get_logger(__name__)
            log.warning("title_generation_failed", error=str(exc))
