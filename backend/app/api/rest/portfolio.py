"""REST routes for balances + transactions (direct Wallbit fetch)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user_id, get_portfolio_service
from app.services.portfolio import PortfolioService

router = APIRouter()


@router.get("/balances")
async def get_balances(
    user_id: UUID = Depends(get_current_user_id),
    svc: PortfolioService = Depends(get_portfolio_service),
) -> list[dict]:
    return await svc.read_balances(user_id=user_id)


@router.get("/transactions")
async def get_transactions(
    limit: int = Query(default=50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    svc: PortfolioService = Depends(get_portfolio_service),
) -> list[dict]:
    return await svc.read_transactions(user_id=user_id, limit=limit)
