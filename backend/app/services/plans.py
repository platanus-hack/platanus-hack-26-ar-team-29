"""PlanService — approve / reject + spawn PlanExecutor."""

from __future__ import annotations

import datetime as _dt
from typing import TYPE_CHECKING, Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.agents.events import format_tool_name
from app.common.errors import NOT_FOUND, PLAN_STALE, APIError
from app.persistence.repositories.plans import PlanRepository
from app.persistence.session import session_factory

if TYPE_CHECKING:
    from app.agents.chat_agent import ChatAgent
    from app.api.ws.manager import ConnectionManager

log = structlog.get_logger(__name__)


def _utcnow() -> _dt.datetime:
    return _dt.datetime.now(_dt.UTC)


class PlanService:
    def __init__(
        self,
        session: AsyncSession,
        manager: ConnectionManager,
        agent: ChatAgent,
        sessionmaker: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self.session = session
        self.manager = manager
        self.agent = agent
        self.sessionmaker = sessionmaker or session_factory
        self.repo = PlanRepository(session)

    async def get_plan(self, plan_id: UUID, user_id: UUID) -> dict[str, Any]:
        plan = await self.repo.get_plan(plan_id, user_id)
        if plan is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="No encontramos ese plan.",
                message_en="Plan not found.",
            )
        return _plan_to_dict(plan)

    async def approve(
        self,
        plan_id: UUID,
        user_id: UUID,
    ) -> dict[str, Any]:
        plan = await self.repo.get_plan(plan_id, user_id)
        if plan is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="No encontramos ese plan.",
                message_en="Plan not found.",
            )
        if plan.state != "pending_approval":
            raise APIError(
                PLAN_STALE,
                http_status=412,
                message_es="Este plan ya no está pendiente.",
                message_en="Plan is no longer pending approval.",
            )
        if plan.expires_at < _utcnow():
            await self.repo.set_plan_state(plan_id, "expired")
            await self.session.commit()
            raise APIError(
                PLAN_STALE,
                http_status=412,
                message_es="Este plan venció. Pedile al agente que lo proponga de nuevo.",
                message_en="Plan expired.",
            )

        await self.repo.set_plan_state(plan_id, "approved", approved_at=_utcnow())
        await self.session.commit()

        # Resolve approval in the agent
        self.agent.resolve_plan_approval(plan_id, "confirm")

        return {"ok": True, "plan_state": "approved", "plan_id": str(plan_id)}

    async def reject(
        self,
        plan_id: UUID,
        user_id: UUID,
        reason: str | None,
    ) -> dict[str, Any]:
        plan = await self.repo.get_plan(plan_id, user_id)
        if plan is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="No encontramos ese plan.",
                message_en="Plan not found.",
            )
        if plan.state != "pending_approval":
            raise APIError(
                PLAN_STALE,
                http_status=412,
                message_es="Este plan ya no está pendiente.",
                message_en="Plan is no longer pending approval.",
            )
        await self.repo.set_plan_state(
            plan_id,
            "rejected",
            rejected_at=_utcnow(),
            rejected_reason=reason,
        )
        await self.session.commit()

        self.agent.resolve_plan_approval(plan_id, "reject")

        if plan.origin_session_id is not None:
            await self.manager.broadcast_to_session(
                plan.origin_session_id,
                {
                    "type": "plan_update",
                    "session_id": str(plan.origin_session_id),
                    "plan_id": str(plan_id),
                    "step_id": None,
                    "state": "rejected",
                    "reason": reason,
                    "ts": _utcnow().isoformat().replace("+00:00", "Z"),
                },
            )
        return {"ok": True, "plan_state": "rejected", "plan_id": str(plan_id)}


def _plan_to_dict(plan: Any) -> dict[str, Any]:
    return {
        "id": str(plan.id),
        "state": plan.state,
        "total_estimated_usd": (
            float(plan.total_estimated_usd) if plan.total_estimated_usd is not None else None
        ),
        "expires_at": plan.expires_at.isoformat().replace("+00:00", "Z"),
        "created_at": plan.created_at.isoformat().replace("+00:00", "Z"),
        "steps": [
            {
                "id": str(s.id),
                "ordinal": s.ordinal,
                "tool_name": s.tool_name,
                "tool_label": format_tool_name(s.tool_name),
                "args": s.args,
                "human_description_es": s.human_description_es,
                "human_description_en": s.human_description_en,
                "category": s.category,
                "estimated_usd": (float(s.estimated_usd) if s.estimated_usd is not None else None),
                "state": s.state,
                "result_summary": s.result_summary,
            }
            for s in plan.steps
        ],
    }
