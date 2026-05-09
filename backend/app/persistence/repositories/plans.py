"""Plan repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.persistence.models.plans import TradePlan, TradePlanStep


class PlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_plan(
        self,
        user_id: UUID,
        origin_session_id: UUID | None,
        origin_message_id: UUID | None,
        steps_data: list[dict[str, Any]],
        expires_at: datetime,
        total_estimated_usd: float | None = None,
    ) -> TradePlan:
        plan = TradePlan(
            user_id=user_id,
            origin_session_id=origin_session_id,
            origin_message_id=origin_message_id,
            expires_at=expires_at,
            total_estimated_usd=total_estimated_usd,
        )
        self.session.add(plan)
        await self.session.flush()
        for idx, sd in enumerate(steps_data):
            step = TradePlanStep(
                plan_id=plan.id,
                user_id=user_id,
                ordinal=sd.get("ordinal", idx + 1),
                tool_name=sd["tool_name"],
                args=sd.get("args", {}),
                human_description_es=sd["human_description_es"],
                human_description_en=sd.get("human_description_en"),
                category=sd.get("category", "write"),
                provider_capability=sd.get("provider_capability"),
                connection_id=sd.get("connection_id"),
                estimated_usd=sd.get("estimated_usd"),
            )
            self.session.add(step)
        await self.session.flush()
        # Reload with steps eager-loaded.
        result = await self.session.execute(
            select(TradePlan).options(selectinload(TradePlan.steps)).where(TradePlan.id == plan.id)
        )
        return result.scalar_one()

    async def get_plan(self, plan_id: UUID, user_id: UUID) -> TradePlan | None:
        stmt = (
            select(TradePlan)
            .options(selectinload(TradePlan.steps))
            .where(TradePlan.id == plan_id, TradePlan.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_plan_by_id(self, plan_id: UUID) -> TradePlan | None:
        stmt = (
            select(TradePlan).options(selectinload(TradePlan.steps)).where(TradePlan.id == plan_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def set_plan_state(
        self,
        plan_id: UUID,
        state: str,
        **fields: Any,
    ) -> None:
        await self.session.execute(
            update(TradePlan).where(TradePlan.id == plan_id).values(state=state, **fields)
        )

    async def update_step_state(
        self,
        step_id: UUID,
        state: str,
        **fields: Any,
    ) -> None:
        await self.session.execute(
            update(TradePlanStep).where(TradePlanStep.id == step_id).values(state=state, **fields)
        )
