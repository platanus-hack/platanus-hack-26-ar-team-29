"""ChatAgent — runs a single user turn.

Uses non-streaming `messages.create` (more robust with tool use), then
synthesizes chat_token frames so the frontend still gets a streamed feel.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import json
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

import structlog
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.agents.tool_dispatcher import ToolContext, ToolDispatcher
from app.ai.anthropic import AnthropicClient
from app.ai.prompts.chat_system import chat_system_prompt
from app.persistence.repositories.chat import ChatRepository

if TYPE_CHECKING:
    from app.api.ws.manager import ConnectionManager

log = structlog.get_logger(__name__)


_FALLBACK_BUY_PHRASES = ("compr", "buy", "comprate", "adquir")
_FALLBACK_SELL_PHRASES = ("vend", "sell", "liquid")


def _content_to_text(blocks: list[Any]) -> str:
    parts: list[str] = []
    for b in blocks or []:
        if isinstance(b, str):
            parts.append(b)
        elif isinstance(b, dict):
            t = b.get("text")
            if t:
                parts.append(str(t))
    return "".join(parts)


def _msg_to_anthropic(msg: Any) -> dict[str, Any] | None:
    """Map a stored ChatMessage to an Anthropic messages payload entry.

    Skip plan_proposal / tool / system kinds; we only forward user/agent text.
    """
    if msg.kind != "text":
        return None
    if msg.author == "user":
        role = "user"
    elif msg.author == "agent":
        role = "assistant"
    else:
        return None
    text = _content_to_text(msg.content_blocks)
    if not text:
        return None
    return {"role": role, "content": [{"type": "text", "text": text}]}


def _heuristic_plan_steps(user_text: str) -> list[dict[str, Any]] | None:
    """Last-resort rule-based fallback when no LLM is configured.

    Detects "compr<a|á|ar> <amount> usd de <symbol>" or sell variants.
    Returns plan steps or None.
    """
    text = user_text.lower()
    side: str | None = None
    if any(p in text for p in _FALLBACK_BUY_PHRASES):
        side = "buy"
    elif any(p in text for p in _FALLBACK_SELL_PHRASES):
        side = "sell"
    if side is None:
        return None
    # Crude: pull first numeric and last word as symbol candidate.
    import re

    amount_match = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not amount_match:
        return None
    amount = float(amount_match.group(1).replace(",", "."))
    # Symbol heuristic: last token after "de" / "of" if present, else last
    # alpha token.
    tokens = re.findall(r"[a-záéíóúñ]+", text)
    symbol_token: str | None = None
    if "de" in tokens:
        idx = tokens.index("de")
        if idx + 1 < len(tokens):
            symbol_token = tokens[idx + 1]
    if symbol_token is None and tokens:
        symbol_token = tokens[-1]
    if symbol_token is None:
        return None
    # Map common Spanish names to tickers.
    name_to_ticker = {
        "apple": "AAPL",
        "microsoft": "MSFT",
        "google": "GOOGL",
        "amazon": "AMZN",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "meta": "META",
        "facebook": "META",
        "spy": "SPY",
        "voo": "VOO",
    }
    symbol = name_to_ticker.get(symbol_token, symbol_token.upper())
    return [
        {
            "tool_name": "place_trade",
            "ordinal": 1,
            "args": {"symbol": symbol, "side": side, "amount_usd": amount},
            "human_description_es": (
                f"{'Comprar' if side == 'buy' else 'Vender'} ${amount:.2f} USD de {symbol}"
            ),
            "human_description_en": (
                f"{'Buy' if side == 'buy' else 'Sell'} {amount:.2f} USD of {symbol}"
            ),
            "category": "write",
            "provider_capability": "place_trade",
            "estimated_usd": amount,
        }
    ]


class ChatAgent:
    def __init__(
        self,
        anthropic: AnthropicClient,
        dispatcher: ToolDispatcher,
        manager: ConnectionManager,
        agent_tasks: set[asyncio.Task],
    ) -> None:
        self.anthropic = anthropic
        self.dispatcher = dispatcher
        self.manager = manager
        self.agent_tasks = agent_tasks

    async def run_turn(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        user_content: str,
        sessionmaker: async_sessionmaker,
        wallbit_base_url: str | None = None,
    ) -> None:
        # Tiny delay to let the WS subscription land before we broadcast.
        await asyncio.sleep(0.05)
        try:
            from app.config import get_settings

            base_url = wallbit_base_url or get_settings().wallbit_base_url
            ctx = ToolContext(
                user_id=user_id,
                session_id=session_id,
                sessionmaker=sessionmaker,
                wallbit_base_url=base_url,
            )

            await self._run_turn_inner(
                session_id=session_id,
                user_id=user_id,
                turn_id=turn_id,
                user_content=user_content,
                sessionmaker=sessionmaker,
                ctx=ctx,
            )
        except Exception as exc:
            log.exception("chat_agent_turn_failed", error=str(exc))
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "error",
                    "code": "INTERNAL_ERROR",
                    "message_es": "El agente tuvo un error procesando tu mensaje.",
                    "message_en": str(exc),
                },
            )
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "turn_complete",
                    "session_id": str(session_id),
                    "turn_id": str(turn_id),
                },
            )

    async def _run_turn_inner(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        user_content: str,
        sessionmaker: async_sessionmaker,
        ctx: ToolContext,
    ) -> None:
        # Load the recent message history for context.
        async with sessionmaker() as db:
            repo = ChatRepository(db)
            recent = await repo.list_messages_recent(
                session_id=session_id, user_id=user_id, limit=20
            )

        history: list[dict[str, Any]] = []
        for m in recent:
            ent = _msg_to_anthropic(m)
            if ent is not None:
                history.append(ent)
        # The current user message is already persisted; ensure it's present.
        if not history or history[-1].get("role") != "user":
            history.append({"role": "user", "content": [{"type": "text", "text": user_content}]})

        if not self.anthropic.available:
            await self._handle_no_llm_fallback(
                session_id=session_id,
                user_id=user_id,
                turn_id=turn_id,
                user_content=user_content,
                sessionmaker=sessionmaker,
            )
            return

        system = chat_system_prompt(user_display_name="Tomás")
        tools = self.dispatcher.as_anthropic_tools()
        messages: list[dict[str, Any]] = list(history)
        draft_steps: list[dict[str, Any]] = []
        final_text_parts: list[str] = []

        for _hop in range(4):
            resp = await self.anthropic.messages_create(
                system=system, messages=messages, tools=tools
            )

            assistant_blocks: list[dict[str, Any]] = []
            tool_use_blocks: list[Any] = []
            for block in resp.content:
                btype = getattr(block, "type", None)
                if btype == "text":
                    text = getattr(block, "text", "")
                    final_text_parts.append(text)
                    assistant_blocks.append({"type": "text", "text": text})
                elif btype == "tool_use":
                    tool_use_blocks.append(block)
                    assistant_blocks.append(
                        {
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        }
                    )

            if assistant_blocks:
                messages.append({"role": "assistant", "content": assistant_blocks})

            stop_reason = getattr(resp, "stop_reason", None)
            if stop_reason != "tool_use" or not tool_use_blocks:
                break

            tool_results: list[dict[str, Any]] = []
            for tu in tool_use_blocks:
                tool_def = self.dispatcher.get(tu.name)
                if tool_def is None:
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tu.id,
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps({"error": f"unknown tool {tu.name}"}),
                                }
                            ],
                            "is_error": True,
                        }
                    )
                    continue
                if tool_def.category == "read":
                    try:
                        result = await self.dispatcher.dispatch(tu.name, dict(tu.input or {}), ctx)
                    except Exception as exc:
                        log.warning("tool_dispatch_failed", tool=tu.name, err=str(exc))
                        result = {"error": str(exc)}
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tu.id,
                            "content": [{"type": "text", "text": json.dumps(result, default=str)}],
                        }
                    )
                else:
                    # write: queue as plan step; tell the model it's queued.
                    args = dict(tu.input or {})
                    if tu.name == "propose_trade":
                        symbol = str(args.get("symbol", "")).upper()
                        side = str(args.get("side", "buy")).lower()
                        amount_usd = args.get("amount_usd")
                        shares = args.get("shares")
                        rationale = (
                            args.get("rationale_es")
                            or f"{'Comprar' if side == 'buy' else 'Vender'} {symbol}"
                        )
                        desc_es = rationale
                        if amount_usd is not None:
                            desc_es += f" por USD {amount_usd}"
                        elif shares is not None:
                            desc_es += f" ({shares} acciones)"
                        draft_steps.append(
                            {
                                "tool_name": "place_trade",
                                "ordinal": len(draft_steps) + 1,
                                "args": {
                                    "symbol": symbol,
                                    "side": side,
                                    **(
                                        {"amount_usd": float(amount_usd)}
                                        if amount_usd is not None
                                        else {}
                                    ),
                                    **({"shares": float(shares)} if shares is not None else {}),
                                },
                                "human_description_es": desc_es,
                                "human_description_en": None,
                                "category": "write",
                                "provider_capability": "place_trade",
                                "estimated_usd": (
                                    float(amount_usd) if amount_usd is not None else None
                                ),
                            }
                        )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tu.id,
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(
                                        {
                                            "queued": True,
                                            "note": "Step added to draft plan; awaiting user approval.",
                                        }
                                    ),
                                }
                            ],
                        }
                    )

            messages.append({"role": "user", "content": tool_results})

        final_text = "".join(final_text_parts).strip()

        if draft_steps:
            await self._emit_plan_proposal(
                session_id=session_id,
                user_id=user_id,
                turn_id=turn_id,
                draft_steps=draft_steps,
                preface_text=final_text,
                sessionmaker=sessionmaker,
            )
            return

        if not final_text:
            final_text = "No pude generar una respuesta. Intentá de nuevo o reformulá la pregunta."

        await self._stream_text_and_persist(
            session_id=session_id,
            user_id=user_id,
            turn_id=turn_id,
            text=final_text,
            sessionmaker=sessionmaker,
        )

    async def _handle_no_llm_fallback(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        user_content: str,
        sessionmaker: async_sessionmaker,
    ) -> None:
        """Without an Anthropic key, try the heuristic plan path."""
        steps = _heuristic_plan_steps(user_content)
        if steps:
            preface = "Te propongo este plan de operaciones. Revisalo y aprobalo si te parece."
            await self._emit_plan_proposal(
                session_id=session_id,
                user_id=user_id,
                turn_id=turn_id,
                draft_steps=steps,
                preface_text=preface,
                sessionmaker=sessionmaker,
            )
            return
        text = (
            "El agente IA no está configurado todavía (falta ANTHROPIC_API_KEY). "
            "Cuando lo configures, voy a poder responderte y proponer operaciones."
        )
        await self._stream_text_and_persist(
            session_id=session_id,
            user_id=user_id,
            turn_id=turn_id,
            text=text,
            sessionmaker=sessionmaker,
        )

    async def _stream_text_and_persist(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        text: str,
        sessionmaker: async_sessionmaker,
    ) -> None:
        # Stream the text in small chunks for streaming UX.
        chunk_size = 24
        for i in range(0, len(text), chunk_size):
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "chat_token",
                    "session_id": str(session_id),
                    "turn_id": str(turn_id),
                    "delta": text[i : i + chunk_size],
                },
            )
            await asyncio.sleep(0.02)

        async with sessionmaker() as db:
            repo = ChatRepository(db)
            msg = await repo.create_message(
                session_id=session_id,
                user_id=user_id,
                author="agent",
                kind="text",
                content_blocks=[{"type": "text", "text": text}],
                turn_id=turn_id,
            )
            await repo.touch_session(session_id)
            await db.commit()

        await self.manager.broadcast_to_session(
            session_id,
            {
                "type": "chat_message",
                "session_id": str(session_id),
                "message": {
                    "id": str(msg.id),
                    "role": "assistant",
                    "content": text,
                    "kind": "text",
                    "created_at": msg.created_at.isoformat().replace("+00:00", "Z"),
                },
            },
        )
        await self.manager.broadcast_to_session(
            session_id,
            {
                "type": "turn_complete",
                "session_id": str(session_id),
                "turn_id": str(turn_id),
            },
        )

    async def _emit_plan_proposal(
        self,
        session_id: UUID,
        user_id: UUID,
        turn_id: UUID,
        draft_steps: list[dict[str, Any]],
        preface_text: str,
        sessionmaker: async_sessionmaker,
    ) -> None:
        # Stream preface text first (if any).
        preface = preface_text or "Te propongo este plan, aprobalo si te parece."
        chunk_size = 24
        for i in range(0, len(preface), chunk_size):
            await self.manager.broadcast_to_session(
                session_id,
                {
                    "type": "chat_token",
                    "session_id": str(session_id),
                    "turn_id": str(turn_id),
                    "delta": preface[i : i + chunk_size],
                },
            )
            await asyncio.sleep(0.02)

        from app.persistence.repositories.connections import ConnectionRepository
        from app.persistence.repositories.plans import PlanRepository

        async with sessionmaker() as db:
            repo = ChatRepository(db)
            plan_repo = PlanRepository(db)
            conn_repo = ConnectionRepository(db)
            wallbit_conn = await conn_repo.get_active_wallbit(user_id)
            if wallbit_conn is not None:
                for s in draft_steps:
                    s.setdefault("connection_id", wallbit_conn.id)

            expires_at = _dt.datetime.now(_dt.UTC) + _dt.timedelta(minutes=5)
            total = sum(float(s.get("estimated_usd") or 0) for s in draft_steps) or None
            plan = await plan_repo.create_plan(
                user_id=user_id,
                origin_session_id=session_id,
                origin_message_id=None,
                steps_data=draft_steps,
                expires_at=expires_at,
                total_estimated_usd=total,
            )

            preface_msg = await repo.create_message(
                session_id=session_id,
                user_id=user_id,
                author="agent",
                kind="text",
                content_blocks=[{"type": "text", "text": preface}],
                turn_id=turn_id,
            )
            proposal_msg = await repo.create_message(
                session_id=session_id,
                user_id=user_id,
                author="agent",
                kind="plan_proposal",
                content_blocks=[
                    {
                        "type": "plan_proposal",
                        "plan_id": str(plan.id),
                    }
                ],
                turn_id=turn_id,
                plan_id=plan.id,
            )
            await plan_repo.set_plan_state(
                plan.id,
                "pending_approval",
                origin_message_id=proposal_msg.id,
            )
            await repo.touch_session(session_id)
            await db.commit()

            steps_payload = [
                {
                    "id": str(s.id),
                    "ordinal": s.ordinal,
                    "tool_name": s.tool_name,
                    "args": s.args,
                    "human_description_es": s.human_description_es,
                    "human_description_en": s.human_description_en,
                    "category": s.category,
                    "estimated_usd": (
                        float(s.estimated_usd) if s.estimated_usd is not None else None
                    ),
                    "state": s.state,
                }
                for s in plan.steps
            ]

        # Broadcast text message for the preface, then plan_proposed.
        await self.manager.broadcast_to_session(
            session_id,
            {
                "type": "chat_message",
                "session_id": str(session_id),
                "message": {
                    "id": str(preface_msg.id),
                    "role": "assistant",
                    "content": preface,
                    "kind": "text",
                    "created_at": preface_msg.created_at.isoformat().replace("+00:00", "Z"),
                },
            },
        )
        await self.manager.broadcast_to_session(
            session_id,
            {
                "type": "plan_proposed",
                "session_id": str(session_id),
                "plan_id": str(plan.id),
                "plan": {
                    "id": str(plan.id),
                    "state": "pending_approval",
                    "total_estimated_usd": (
                        float(plan.total_estimated_usd)
                        if plan.total_estimated_usd is not None
                        else None
                    ),
                    "expires_at": plan.expires_at.isoformat().replace("+00:00", "Z"),
                    "steps": steps_payload,
                },
            },
        )
        await self.manager.broadcast_to_session(
            session_id,
            {
                "type": "turn_complete",
                "session_id": str(session_id),
                "turn_id": str(turn_id),
            },
        )

    async def continue_after_plan(
        self,
        session_id: UUID,
        user_id: UUID,
        plan_id: UUID,
        outcome: str,
        steps_summary: list[dict[str, Any]],
        sessionmaker: async_sessionmaker,
    ) -> None:
        """Emit a brief summary turn after plan execution."""
        turn_id = uuid4()
        # Quick deterministic summary; no second LLM round-trip needed.
        successes = sum(1 for s in steps_summary if s.get("state") == "ok")
        failures = sum(1 for s in steps_summary if s.get("state") == "failed")
        if outcome == "completed":
            text = f"Listo, ejecuté las {successes} operaciones aprobadas. ¿Querés ver el balance actualizado?"
        elif outcome == "partially_failed":
            text = (
                f"Ejecuté {successes} operación/es y falló {failures}. "
                "Revisalo y decime si querés que reintente."
            )
        else:
            text = "El plan terminó con un estado inesperado."
        await self._stream_text_and_persist(
            session_id=session_id,
            user_id=user_id,
            turn_id=turn_id,
            text=text,
            sessionmaker=sessionmaker,
        )
