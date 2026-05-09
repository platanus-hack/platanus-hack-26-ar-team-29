"""REST routes for plan approval / rejection."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_id, get_plan_service
from app.services.plans import PlanService

router = APIRouter()


class ApprovePlanRequest(BaseModel):
    approved: bool | None = Field(default=True)


class RejectPlanRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=500)


@router.get("/{plan_id}")
async def get_plan(
    plan_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    svc: PlanService = Depends(get_plan_service),
) -> dict:
    return await svc.get_plan(plan_id=plan_id, user_id=user_id)


@router.post("/{plan_id}/approve")
async def approve_plan(
    plan_id: UUID,
    body: ApprovePlanRequest | None = None,
    user_id: UUID = Depends(get_current_user_id),
    svc: PlanService = Depends(get_plan_service),
) -> dict:
    return await svc.approve(plan_id=plan_id, user_id=user_id)


@router.post("/{plan_id}/reject")
async def reject_plan(
    plan_id: UUID,
    body: RejectPlanRequest | None = None,
    user_id: UUID = Depends(get_current_user_id),
    svc: PlanService = Depends(get_plan_service),
) -> dict:
    reason = body.reason if body else None
    return await svc.reject(plan_id=plan_id, user_id=user_id, reason=reason)
