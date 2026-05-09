"""REST routes for /connections/{id}/onchain/* (02-3 §5.13.2)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_current_user_id, get_onchain_service
from app.services.onchain import OnchainService

router = APIRouter()


class OnchainSimulateRequest(BaseModel):
    asset: str = Field(min_length=1, max_length=32)
    to: str = Field(min_length=1, max_length=128)
    amount: str = Field(min_length=1, max_length=64)


class OnchainTransferRequest(BaseModel):
    asset: str = Field(min_length=1, max_length=32)
    to: str = Field(min_length=1, max_length=128)
    amount: str = Field(min_length=1, max_length=64)
    gas_speed: str | None = Field(default="standard", max_length=32)


@router.get("/{connection_id}/onchain/gas")
async def get_onchain_gas(
    connection_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    svc: OnchainService = Depends(get_onchain_service),
) -> dict:
    return {"data": await svc.get_gas(user_id=user_id, connection_id=connection_id)}


@router.post("/{connection_id}/onchain/simulate")
async def simulate_onchain_transfer(
    connection_id: UUID,
    body: OnchainSimulateRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: OnchainService = Depends(get_onchain_service),
) -> dict:
    return {
        "data": await svc.simulate(
            user_id=user_id,
            connection_id=connection_id,
            asset=body.asset,
            to=body.to,
            amount=body.amount,
        )
    }


@router.post("/{connection_id}/onchain/transfer")
async def send_onchain_transfer(
    connection_id: UUID,
    body: OnchainTransferRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: OnchainService = Depends(get_onchain_service),
) -> dict:
    return {
        "data": await svc.transfer(
            user_id=user_id,
            connection_id=connection_id,
            asset=body.asset,
            to=body.to,
            amount=body.amount,
            gas_speed=body.gas_speed,
        )
    }
