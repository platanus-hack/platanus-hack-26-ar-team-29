from __future__ import annotations

import asyncio
import json
import datetime as _dt
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

from app.agents.defi_tools import defi_mcp_server
from app.agents.ethereum_tools import ethereum_mcp_server
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

Reglas de presentación (CRÍTICO):
- Cuando vayas a mostrar una tabla (usando show_table), SIEMPRE debes escribir el texto explicativo o de introducción ANTES de invocar a la tool. Esto asegura que visualmente el texto quede arriba de la tabla. NUNCA llames a show_table primero y luego escribas el texto.

Reglas de seguridad:
- Podes usar herramientas de lectura libremente para entender balances, activos
  e historial.
- Si falta informacion critica (símbolo, cantidad/monto, moneda, tipo de orden),
  usa AskUserQuestion con 2 a 4 opciones cortas en vez de preguntar con texto
  largo. Despues de recibir la respuesta, continua el flujo sin repetir la
  pregunta y sin terminar el turno.

- Cuando el usuario pida ver un gráfico, historial de precios, o visualizar datos de forma gráfica, debes responder con los datos en formato CSV dentro de un bloque de código markdown.
  El lenguaje del bloque debe especificar el tipo de gráfico a mostrar, usando una de estas tres opciones:
  1. `csv-bar` : Gráfico de barras (Ideal para comparaciones de valores discretos o meses).
  2. `csv-line` : Gráfico de líneas (Ideal para tendencias, historial de precios a lo largo del tiempo).
  3. `csv-pie` : Gráfico de torta/circular (Ideal para distribuciones de portafolio o porcentajes).
  
  La primera fila debe ser el encabezado `label,value`.
  Ejemplo de gráfico de torta:
  ```csv-pie
  label,value
  AAPL,500
  TSLA,300
  AMZN,200
  ```
  El frontend interceptará este bloque y dibujará el gráfico correspondiente automáticamente.

Flujo de trade (CRITICO — leelo y seguilo al pie de la letra):
- Cuando tengas todos los datos necesarios para una compra/venta, **llama
  directamente** a la tool `mcp__wallbit__create_trade`. NO escribas en texto
  "¿confirmás?", "¿querés que compre X?", ni preguntas similares antes de
  llamar al tool. Llamar al tool es lo que dispara la confirmacion oficial.
- NUNCA describas el mecanismo de confirmacion al usuario. No menciones
  "modal", "botones", "Aprobar / Rechazar", "ventana", "popup" ni nada
  parecido. La UI ya muestra esos controles por su cuenta — si los nombras
  en texto, suena raro y rompe la experiencia.
- Antes de la llamada al tool podes (y deberias) explicar en una o dos frases
  cortas qué vas a hacer (símbolo, cantidad, precio estimado, costo total).
  El turno tiene que terminar con la **invocacion del tool**, no con una
  pregunta y no con una explicacion del flujo de confirmacion.
- Si el usuario rechaza la operacion, respetalo y ofrece ajustar el plan.
- Nunca digas que una operacion fue ejecutada hasta que el resultado del tool
  lo confirme.
- El backend intercepta la llamada al tool y pausa la herramienta hasta que la
  UI resuelva la decisión. No describas ese mecanismo en texto. Si en lugar de
  llamar al tool preguntas "¿confirmás?" en texto, el usuario queda colgado:
  eso es un bug grave.
- ANTES de llamar al tool, NO des por hecho que la operacion se va a ejecutar. Usa frases como "Acá te preparé la orden para que la revises:" o "Te dejo los detalles de la operación para que confirmes:". NUNCA digas "Voy a comprar..." ni "Ejecutando compra...", presentalo siempre como una propuesta.
- El turno tiene que terminar con la **invocacion del tool**, no con una pregunta al usuario.
- NUNCA digas que una operacion fue ejecutada hasta que el resultado del tool lo confirme.
- Si el tool devuelve que el usuario rechazó la operación, respondé de forma natural (ej. "Entendido, operación cancelada.") y ofrece ajustar los parámetros.

La herramienta de trading se llama `mcp__wallbit__create_trade`. Esta
disponible y conectada — nunca digas lo contrario.

Para crear una billetera de Ethereum, usa la herramienta `mcp__ethereum__create_ethereum_wallet`. Preguntale siempre al usuario en que red la quiere crear si no lo especifico (opciones: sepolia, holesky, polygon-amoy, arbitrum-sepolia, base-sepolia, base).
Al finalizar la creacion de la cuenta, pasale al usuario la direccion y la frase semilla usando comillas simples invertidas (`backticks`) para que el formato se renderice bien con boton de copia.
Ejemplo:
Direccion: `0x...`
Frase semilla: `palabra1 palabra2...`

Para iniciar sesion o importar una billetera de Ethereum existente, usa la herramienta `mcp__ethereum__import_ethereum_wallet`. Pidele siempre al usuario su clave privada o frase semilla y la red en la que desea importar.
Al finalizar la importacion, pasale al usuario la direccion importada.

DeFi / Aave V3 (generar yield depositando en pools):
- `mcp__defi__list_markets` lista los mercados de Aave disponibles con su APY
  actual. Usalo cuando el usuario pregunte por opciones de inversion en DeFi,
  yield pasivo, "donde puedo poner mis dolares", etc. Hoy esta soportado USDC
  en la red `base`.
- `mcp__defi__list_positions` muestra las posiciones DeFi del usuario (lo que
  ya tiene depositado en Aave). Usalo para reportes de portfolio o cuando el
  usuario pregunte cuanto tiene invertido en DeFi.
- `mcp__defi__supply` deposita un asset en Aave. ESTA ES UNA OPERACION QUE
  MUEVE DINERO, asi que se aplica la misma regla que con trades: llama
  directamente a la tool, no preguntes "¿confirmás?" en texto. El backend
  intercepta y pide confirmacion al usuario por su cuenta.
- `mcp__defi__withdraw` retira un asset previamente depositado en Aave. Misma
  regla: llamala directamente. Para retirar todo lo depositado pasa
  amount="max".
- Antes de un supply/withdraw podes (y deberias) explicar en una o dos frases
  qué vas a hacer (asset, monto, mercado, APY estimado). Despues llamas a la
  tool sin pedir mas confirmacion.
- Para obtener un market_id correcto, primero llama a list_markets si no lo
  tenes; el formato es `aave-v3-<network>-<asset>` (e.g. `aave-v3-base-USDC`).
""".strip()

ETHEREUM_WRITE_TOOLS = [
    "create_ethereum_wallet",
    "mcp__ethereum__create_ethereum_wallet",
    "import_ethereum_wallet",
    "mcp__ethereum__import_ethereum_wallet",
]

WALLBIT_READ_TOOLS = [
    "get_checking_balance",
    "get_stocks_balance",
    "list_transactions",
    "get_asset",
    "mcp__wallbit__get_checking_balance",
    "mcp__wallbit__get_stocks_balance",
    "mcp__wallbit__list_transactions",
    "mcp__wallbit__get_asset",
    "mcp__wallbit__show_table",
]
WALLBIT_WRITE_TOOLS = [
    "create_trade",
    "mcp__wallbit__create_trade",
]
WALLBIT_TOOLS = WALLBIT_READ_TOOLS + WALLBIT_WRITE_TOOLS

DEFI_READ_TOOLS = [
    "list_markets",
    "get_market",
    "list_positions",
    "mcp__defi__list_markets",
    "mcp__defi__get_market",
    "mcp__defi__list_positions",
]
DEFI_WRITE_TOOLS = [
    "supply",
    "withdraw",
    "mcp__defi__supply",
    "mcp__defi__withdraw",
]
DEFI_TOOLS = DEFI_READ_TOOLS + DEFI_WRITE_TOOLS

AGENT_UI_TOOLS = ["AskUserQuestion"]
AUTO_ALLOWED_TOOLS = WALLBIT_READ_TOOLS + ETHEREUM_WRITE_TOOLS + DEFI_READ_TOOLS
AGENT_MODEL = "haiku"
AGENT_FALLBACK_MODEL = "sonnet"


async def _allow_pre_tool_use_hook(
    input_data: dict[str, Any],
    tool_use_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, bool]:
    del input_data, tool_use_id, context
    return {"continue_": True}


async def _fetch_unit_price_usd(args: dict[str, Any]) -> float | None:
    """Best-effort fetch of an asset's current unit price for plan-card display.

    Returns None on any failure — the approval flow must not block on it.
    """
    symbol = str(args.get("symbol") or "").upper()
    if not symbol:
        return None
    try:
        from app.agents.wallbit_tools import _request

        resp = await _request("GET", f"/api/public/v1/assets/{symbol}")
        outer = resp.get("data") if isinstance(resp, dict) else None
        # Wallbit returns {"data": {"symbol": ..., "price": ...}} so we unwrap once.
        body = (
            outer.get("data")
            if isinstance(outer, dict) and isinstance(outer.get("data"), dict)
            else outer
        )
        price = body.get("price") if isinstance(body, dict) else None
        return float(price) if isinstance(price, int | float) else None
    except Exception:  # noqa: BLE001 — price fetch is best-effort.
        return None


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
            mcp_servers={
                "wallbit": wallbit_mcp_server(),
                "ethereum": ethereum_mcp_server(),
                "defi": defi_mcp_server(),
            },
            strict_mcp_config=True,
            permission_mode="default",
            tools=AGENT_UI_TOOLS,
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
                            "input_summary": json.dumps(getattr(block, "input", None)) if getattr(block, "input", None) is not None else None,
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
                            "result_summary": json.dumps(getattr(block, "content", None)) if getattr(block, "content", None) is not None else None,
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
                        "input_summary": json.dumps(getattr(content_block, "input", None)) if getattr(content_block, "input", None) is not None else None,
                    },
                )
            ]

    return []


def _is_redundant_approval_message(text: str) -> bool:
    normalized = text.lower()
    return any(
        phrase in normalized
        for phrase in (
            "para que confirmes",
            "para que apruebes",
            "ventana de confirmación",
            "ventana de confirmacion",
            "orden está lista",
            "orden esta lista",
            "esperando tu aprobación",
            "esperando aprobación",
            "esperando tu aprobacion",
            "esperando aprobacion",
            "panel",
            "aprobar o rechazar",
            "aprobar/rechazar",
            "confirmación para que",
            "confirmacion para que",
            "botón",
            "botones",
            "revisar transacción",
            "revisar transaccion",
        )
    )


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

        turn_has_approval_card = False

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
                if not text:
                    continue
                if turn_has_approval_card and _is_redundant_approval_message(text):
                    continue
                async with sessionmaker() as db:
                    from app.persistence.repositories.chat import ChatRepository

                    chat_repo = ChatRepository(db)
                    msg = await chat_repo.create_message(
                        session_id=session_id,
                        user_id=user_id,
                        author="agent",
                        kind="text",
                        content_blocks=[{"type": "text", "text": text}],
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
                turn_has_approval_card = True
                tool_name = event.payload["tool_name"]
                args = event.payload.get("input") or {}

                # For trade plans, fetch the live unit price so the plan card
                # can show "Precio actual" + estimated cost before the user
                # decides. Failure here must not block the approval flow.
                estimated_unit_price: float | None = None
                estimated_total: float | None = None
                human_description_es = "Aprobar " + tool_name
                if tool_name in ("create_trade", "mcp__wallbit__create_trade"):
                    estimated_unit_price = await _fetch_unit_price_usd(args)
                    if estimated_unit_price is not None:
                        shares = args.get("shares")
                        amount = args.get("amount")
                        if isinstance(shares, (int, float)) and shares > 0:
                            estimated_total = estimated_unit_price * float(shares)
                        elif isinstance(amount, (int, float)) and amount > 0:
                            estimated_total = float(amount)
                elif tool_name in ("supply", "mcp__defi__supply", "withdraw", "mcp__defi__withdraw"):
                    is_supply = tool_name in ("supply", "mcp__defi__supply")
                    asset = str(args.get("asset") or "").upper()
                    raw_amount = args.get("amount")
                    # Stablecoin assumption: 1 USDC ≈ 1 USD (matches services/defi.py).
                    if isinstance(raw_amount, (int, float)):
                        estimated_total = float(raw_amount)
                    elif isinstance(raw_amount, str) and raw_amount.strip().lower() != "max":
                        try:
                            estimated_total = float(raw_amount)
                        except ValueError:
                            estimated_total = None
                    amount_label = (
                        "todo lo depositado"
                        if isinstance(raw_amount, str) and raw_amount.strip().lower() == "max"
                        else f"{raw_amount} {asset}".strip()
                    )
                    human_description_es = (
                        f"Depositar {amount_label} en Aave"
                        if is_supply
                        else f"Retirar {amount_label} de Aave"
                    )

                async with sessionmaker() as db:
                    from app.persistence.repositories.plans import PlanRepository

                    repo = PlanRepository(db)
                    plan = await repo.create_plan(
                        user_id=user_id,
                        origin_session_id=session_id,
                        origin_message_id=None,
                        steps_data=[
                            {
                                "tool_name": tool_name,
                                "args": args,
                                "human_description_es": human_description_es,
                                "estimated_usd": estimated_total,
                            }
                        ],
                        expires_at=_dt.datetime.now(_dt.UTC) + _dt.timedelta(minutes=15),
                        total_estimated_usd=estimated_total,
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

                plan_dict = _plan_to_dict(plan)
                if estimated_unit_price is not None:
                    plan_dict["estimated_unit_price_usd"] = estimated_unit_price

                await self.manager.broadcast_to_session(
                    session_id,
                    {
                        "type": "plan_proposed",
                        "session_id": str(session_id),
                        "turn_id": str(turn_id),
                        "plan_id": str(plan.id),
                        "plan": plan_dict,
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
