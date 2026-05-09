"""REST routes for provider connections."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response
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


# ----------------- Custodial Ethereum (02-3 §5.13.1) -----------------


class EthereumImportRequest(BaseModel):
    network: str = Field(min_length=1, max_length=64)
    # Accepts a 0x-prefixed 32-byte hex string OR a 12/24-word BIP-39 mnemonic.
    private_key: str = Field(min_length=1)
    label: str | None = Field(default=None, max_length=120)
    primary_asset_hint: str | None = Field(default=None, max_length=32)


class EthereumCreateRequest(BaseModel):
    network: str = Field(min_length=1, max_length=64)
    label: str | None = Field(default=None, max_length=120)
    primary_asset_hint: str | None = Field(default=None, max_length=32)


class ExportPrivateKeyRequest(BaseModel):
    confirm: bool = Field(default=False)


@router.post("/ethereum-custodial/import")
async def import_ethereum_custodial(
    body: EthereumImportRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: ConnectionService = Depends(get_connection_service),
) -> dict:
    return {
        "data": await svc.import_ethereum_custodial(
            user_id=user_id,
            network=body.network,
            private_key_or_mnemonic=body.private_key,
            label=body.label,
            primary_asset_hint=body.primary_asset_hint,
        )
    }


@router.post("/ethereum-custodial/create")
async def create_ethereum_custodial(
    body: EthereumCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    svc: ConnectionService = Depends(get_connection_service),
) -> dict:
    return {
        "data": await svc.create_ethereum_custodial(
            user_id=user_id,
            network=body.network,
            label=body.label,
            primary_asset_hint=body.primary_asset_hint,
        )
    }


@router.post("/{connection_id}/export-private-key")
async def export_private_key(
    connection_id: UUID,
    body: ExportPrivateKeyRequest,
    response: Response,
    user_id: UUID = Depends(get_current_user_id),
    svc: ConnectionService = Depends(get_connection_service),
) -> dict:
    # 02-3 §5.13.5: Cache-Control: no-store, private. Never set as a downloadable file.
    # The response body is a plain JSON envelope; the client renders the key.
    response.headers["Cache-Control"] = "no-store, private"
    # NOTE(rate-limit): 02-3 §5.13.5 specifies max 5 exports per connection per
    # hour. The middleware lands in the auth pass; for now we trust the bearer.
    # TODO(phase-1.1): wire a rate-limiter and return 429 RATE_LIMITED on overflow.
    # NOTE(chat-excluded): this endpoint is intentionally NOT registered as a
    # Claude tool — see 02-3 §14 row 31.
    data = await svc.export_private_key(user_id=user_id, connection_id=connection_id)
    return {"data": data}
