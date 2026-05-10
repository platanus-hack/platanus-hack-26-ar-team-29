"""REST routes for user profile."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user_id, get_profiler_service
from app.services.profiler import ProfilerService

router = APIRouter()


@router.get("/")
async def get_profile(
    user_id: UUID = Depends(get_current_user_id),
    svc: ProfilerService = Depends(get_profiler_service),
) -> dict:
    profile = await svc.get_profile(user_id=user_id)
    if not profile:
        return {}
    return {
        "is_dirty": profile.is_dirty,
        "last_recomputed_at": profile.last_recomputed_at.isoformat()
        if profile.last_recomputed_at
        else None,
        "summaries": profile.summaries,
        "risk_profile": profile.risk_profile,
        "portfolio_metrics": profile.portfolio_metrics,
    }


@router.post("/generate")
async def generate_profile(
    user_id: UUID = Depends(get_current_user_id),
    svc: ProfilerService = Depends(get_profiler_service),
) -> dict:
    profile = await svc.generate_profile(user_id=user_id)
    return {
        "is_dirty": profile.is_dirty,
        "last_recomputed_at": profile.last_recomputed_at.isoformat()
        if profile.last_recomputed_at
        else None,
        "summaries": profile.summaries,
        "risk_profile": profile.risk_profile,
        "portfolio_metrics": profile.portfolio_metrics,
    }
