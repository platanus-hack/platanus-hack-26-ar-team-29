"""REST routes for DeFi (02-3 §5.13.3) — Aave V3 only in v1.

Five endpoints:
- GET  /api/v1/defi/markets
- GET  /api/v1/defi/markets/{protocol}/{market_id}
- GET  /api/v1/connections/{id}/defi/positions
- POST /api/v1/connections/{id}/defi/supply
- POST /api/v1/connections/{id}/defi/withdraw

The first two mount under `/defi`; the last three mount under `/connections`
because they require a connection scope.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_id, get_defi_service
from app.services.defi import DefiService

# Routers split by URL prefix so api/__init__.py can mount them under the
# right base paths without rewriting Strict prefixes here.
markets_router = APIRouter()
connection_scoped_router = APIRouter()


class DefiSupplyRequest(BaseModel):
    protocol: str = Field(min_length=1, max_length=32)
    market_id: str = Field(min_length=1, max_length=128)
    asset: str = Field(min_length=1, max_length=32)
    amount: str = Field(min_length=1, max_length=64)


class DefiWithdrawRequest(BaseModel):
    protocol: str = Field(min_length=1, max_length=32)
    market_id: str = Field(min_length=1, max_length=128)
    asset: str = Field(min_length=1, max_length=32)
    amount: str = Field(min_length=1, max_length=64)  # Decimal string OR "max".


@markets_router.get("/markets")
async def list_defi_markets(
    protocol: str | None = Query(default=None, max_length=32),
    network: str | None = Query(default=None, max_length=64),
    asset: str | None = Query(default=None, max_length=32),
    min_apy: float | None = Query(default=None, ge=0, le=10),
    svc: DefiService = Depends(get_defi_service),
) -> dict:
    return {
        "data": await svc.list_markets(
            protocol=protocol, network=network, asset=asset, min_apy=min_apy
        )
    }


@markets_router.get("/markets/{protocol}/{market_id}")
async def get_defi_market(
    protocol: str,
    market_id: str,
    svc: DefiService = Depends(get_defi_service),
) -> dict:
    return {"data": await svc.get_market(protocol=protocol, market_id=market_id)}


@connection_scoped_router.get("/{connection_id}/defi/positions")
async def list_defi_positions(
    connection_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    svc: DefiService = Depends(get_defi_service),
) -> dict:
    return {"data": await svc.list_positions(user_id=user_id, connection_id=connection_id)}


@connection_scoped_router.post("/{connection_id}/defi/supply")
async def supply_to_defi(
    connection_id: UUID,
    body: DefiSupplyRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: DefiService = Depends(get_defi_service),
) -> dict:
    return {
        "data": await svc.supply(
            user_id=user_id,
            connection_id=connection_id,
            protocol=body.protocol,
            market_id=body.market_id,
            asset=body.asset,
            amount=body.amount,
        )
    }


@connection_scoped_router.post("/{connection_id}/defi/withdraw")
async def withdraw_from_defi(
    connection_id: UUID,
    body: DefiWithdrawRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: DefiService = Depends(get_defi_service),
) -> dict:
    return {
        "data": await svc.withdraw(
            user_id=user_id,
            connection_id=connection_id,
            protocol=body.protocol,
            market_id=body.market_id,
            asset=body.asset,
            amount=body.amount,
        )
    }
