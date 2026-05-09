"""REST routes for provider connections."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_connection_service, get_current_user_id
from app.services.connections import ConnectionService

router = APIRouter()


class WallbitConnectRequest(BaseModel):
    label: str | None = Field(default=None, max_length=120)
    api_key: str = Field(min_length=1)


@router.post("/wallbit")
async def connect_wallbit(
    body: WallbitConnectRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: ConnectionService = Depends(get_connection_service),
) -> dict:
    return await svc.create_wallbit(user_id=user_id, label=body.label, api_key=body.api_key)


@router.get("")
async def list_connections(
    user_id: UUID = Depends(get_current_user_id),
    svc: ConnectionService = Depends(get_connection_service),
) -> list[dict]:
    return await svc.list_for_user(user_id=user_id)
