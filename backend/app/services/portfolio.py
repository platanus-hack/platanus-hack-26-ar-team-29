"""PortfolioService — direct Wallbit fetch (no canonical ledger in MVP)."""

from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import NOT_FOUND, PROVIDER_UNAVAILABLE, APIError
from app.persistence.repositories.connections import ConnectionRepository
from app.providers.wallbit.adapter import (
    checking_balance_to_rows,
    stocks_balance_to_rows,
    transactions_to_rows,
)
from app.providers.wallbit.auth import WallbitCredentials
from app.providers.wallbit.client import WallbitAPIError, WallbitClient

log = structlog.get_logger(__name__)


class PortfolioService:
    def __init__(self, session: AsyncSession, wallbit_base_url: str) -> None:
        self.session = session
        self.wallbit_base_url = wallbit_base_url
        self.repo = ConnectionRepository(session)

    async def _get_credentials(self, user_id: UUID) -> WallbitCredentials:
        conn = await self.repo.get_active_wallbit(user_id)
        if conn is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es=(
                    "Todavía no conectaste tu cuenta Wallbit. "
                    "Conectala en Configuración para empezar."
                ),
                message_en="No active Wallbit connection.",
            )
        return WallbitCredentials.from_blob(bytes(conn.credentials_encrypted))

    async def read_balances(self, user_id: UUID) -> list[dict[str, Any]]:
        creds = await self._get_credentials(user_id)
        async with WallbitClient(api_key=creds.api_key, base_url=self.wallbit_base_url) as wc:
            try:
                checking_raw, stocks_raw = await asyncio.gather(
                    wc.get_checking_balance(),
                    wc.get_stocks_balance(),
                    return_exceptions=False,
                )
            except WallbitAPIError as exc:
                raise APIError(
                    PROVIDER_UNAVAILABLE,
                    http_status=502,
                    message_es="Wallbit no respondió correctamente.",
                    message_en="Wallbit upstream error.",
                    details={"status": exc.status, "body": exc.body},
                ) from exc

        checking_rows = checking_balance_to_rows(checking_raw)
        stocks_rows = stocks_balance_to_rows(stocks_raw)
        return [*checking_rows, *stocks_rows]

    async def read_transactions(self, user_id: UUID, limit: int = 50) -> list[dict[str, Any]]:
        creds = await self._get_credentials(user_id)
        async with WallbitClient(api_key=creds.api_key, base_url=self.wallbit_base_url) as wc:
            try:
                raw = await wc.list_transactions(limit=limit)
            except WallbitAPIError as exc:
                raise APIError(
                    PROVIDER_UNAVAILABLE,
                    http_status=502,
                    message_es="Wallbit no respondió correctamente.",
                    message_en="Wallbit upstream error.",
                    details={"status": exc.status, "body": exc.body},
                ) from exc
        return transactions_to_rows(raw)
