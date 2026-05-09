"""ConnectionService — Wallbit-only in MVP."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import PROVIDER_UNAVAILABLE, VALIDATION_FAILED, APIError
from app.persistence.repositories.connections import ConnectionRepository
from app.providers.wallbit.auth import WallbitCredentials
from app.providers.wallbit.client import WallbitAPIError, WallbitClient

log = structlog.get_logger(__name__)


class ConnectionService:
    def __init__(self, session: AsyncSession, wallbit_base_url: str) -> None:
        self.session = session
        self.wallbit_base_url = wallbit_base_url
        self.repo = ConnectionRepository(session)

    async def create_wallbit(
        self, user_id: UUID, label: str | None, api_key: str
    ) -> dict[str, Any]:
        api_key = (api_key or "").strip()
        if not api_key:
            raise APIError(
                VALIDATION_FAILED,
                http_status=422,
                message_es="La clave API de Wallbit no puede estar vacía.",
                message_en="Wallbit API key cannot be empty.",
            )

        # Probe call to validate the key.
        async with WallbitClient(api_key=api_key, base_url=self.wallbit_base_url) as wc:
            try:
                await wc.get_checking_balance()
            except WallbitAPIError as exc:
                log.warning("wallbit_probe_failed", status=exc.status, body=str(exc.body))
                raise APIError(
                    PROVIDER_UNAVAILABLE,
                    http_status=400,
                    message_es=(
                        "No pudimos validar la clave de Wallbit. "
                        "Verificá que sea correcta y que tenga permisos de lectura."
                    ),
                    message_en="Wallbit API key validation failed.",
                    details={"status": exc.status, "body": exc.body},
                ) from exc

        creds = WallbitCredentials(api_key=api_key)
        blob = creds.to_blob()
        conn = await self.repo.create_wallbit(
            user_id=user_id,
            label=label,
            credentials_encrypted=blob,
            capabilities=["read_balance", "read_transactions", "place_trade"],
            metadata={},
        )
        await self.session.commit()
        return {
            "id": str(conn.id),
            "connection_type": conn.connection_type,
            "label": conn.label,
            "status": conn.status,
            "capabilities": list(conn.capabilities),
            "created_at": conn.created_at.isoformat().replace("+00:00", "Z"),
        }

    async def list_for_user(self, user_id: UUID) -> list[dict[str, Any]]:
        rows = await self.repo.list_for_user(user_id)
        return [
            {
                "id": str(c.id),
                "connection_type": c.connection_type,
                "label": c.label,
                "status": c.status,
                "capabilities": list(c.capabilities),
                "created_at": c.created_at.isoformat().replace("+00:00", "Z"),
            }
            for c in rows
        ]

    async def get_active_wallbit_credentials(
        self, user_id: UUID
    ) -> tuple[UUID, WallbitCredentials] | None:
        conn = await self.repo.get_active_wallbit(user_id)
        if conn is None:
            return None
        creds = WallbitCredentials.from_blob(bytes(conn.credentials_encrypted))
        return conn.id, creds
