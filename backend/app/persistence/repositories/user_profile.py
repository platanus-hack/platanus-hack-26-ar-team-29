"""User Profile repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models.users import UserProfile


class UserProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> UserProfile | None:
        result = await self.session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self,
        user_id: UUID,
        summaries: dict,
        risk_profile: dict,
        portfolio_metrics: dict,
        is_dirty: bool = False,
    ) -> UserProfile:
        from sqlalchemy.sql import func

        stmt = insert(UserProfile).values(
            user_id=user_id,
            summaries=summaries,
            risk_profile=risk_profile,
            portfolio_metrics=portfolio_metrics,
            is_dirty=is_dirty,
            last_recomputed_at=func.now() if not is_dirty else None,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["user_id"],
            set_={
                "summaries": stmt.excluded.summaries,
                "risk_profile": stmt.excluded.risk_profile,
                "portfolio_metrics": stmt.excluded.portfolio_metrics,
                "is_dirty": stmt.excluded.is_dirty,
                "last_recomputed_at": stmt.excluded.last_recomputed_at,
                "updated_at": func.now(),
            },
        ).returning(UserProfile)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def mark_dirty(self, user_id: UUID) -> None:
        from sqlalchemy import update

        stmt = update(UserProfile).where(UserProfile.user_id == user_id).values(is_dirty=True)
        await self.session.execute(stmt)
