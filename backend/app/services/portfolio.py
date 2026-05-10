"""PortfolioService — direct Wallbit fetch (no canonical ledger in MVP)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.canonical.models import CanonicalBalance, CanonicalPosition
from app.common.errors import NOT_FOUND, PROVIDER_UNAVAILABLE, APIError
from app.persistence.repositories.connections import ConnectionRepository
from app.providers.ethereum.client import EthereumClient, EthereumClientError
from app.providers.wallbit.adapter import (
    checking_balance_to_rows,
    stocks_balance_to_rows,
    transaction_cost_basis_by_symbol,
)
from app.providers.wallbit.auth import WallbitCredentials
from app.providers.wallbit.client import WallbitAPIError, WallbitClient

log = structlog.get_logger(__name__)

WEI_PER_ETH = 10**18


def _float_or_none(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


class PortfolioService:
    def __init__(
        self,
        session: AsyncSession,
        wallbit_base_url: str,
        eth_client: EthereumClient | None = None,
    ) -> None:
        self.session = session
        self.wallbit_base_url = wallbit_base_url
        self.eth_client = eth_client
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

    async def read_balances(self, user_id: UUID) -> list[CanonicalBalance]:
        balances: list[CanonicalBalance] = []

        # Wallbit balances (may be absent — user could have only an ETH wallet).
        wallbit_conn = await self.repo.get_active_wallbit(user_id)
        if wallbit_conn is not None:
            creds = WallbitCredentials.from_blob(bytes(wallbit_conn.credentials_encrypted))
            async with WallbitClient(api_key=creds.api_key, base_url=self.wallbit_base_url) as wc:
                try:
                    checking_raw = await wc.get_checking_balance()
                except WallbitAPIError as exc:
                    raise APIError(
                        PROVIDER_UNAVAILABLE,
                        http_status=502,
                        message_es="Wallbit no respondió correctamente al buscar balances.",
                        message_en="Wallbit upstream error.",
                        details={"status": exc.status, "body": exc.body},
                    ) from exc
            for row in checking_balance_to_rows(checking_raw):
                balances.append(
                    CanonicalBalance(
                        provider="Wallbit",
                        account=row.get("account", "checking"),
                        symbol=row.get("symbol", "USD"),
                        currency=row.get("currency", "USD"),
                        amount=float(row.get("amount", 0.0)),
                        usd_value=float(row.get("amount", 0.0))
                        if row.get("currency") == "USD"
                        else None,
                        raw=row.get("raw", {}),
                    )
                )

        # Ethereum custodial wallets — show address + native ETH balance per
        # connection. Failures here are logged but don't abort the whole call.
        if self.eth_client is not None:
            for conn in await self.repo.list_for_user(user_id):
                if conn.connection_type != "ethereum_custodial" or conn.status != "active":
                    continue
                md = dict(conn.connection_metadata or {})
                address = md.get("address")
                network = md.get("network")
                if not isinstance(address, str) or not isinstance(network, str):
                    continue
                try:
                    wei = await self.eth_client.get_eth_balance(network, address)
                except EthereumClientError as exc:
                    log.warning(
                        "eth_balance_read_failed",
                        connection_id=str(conn.id),
                        network=network,
                        error=str(exc),
                    )
                    continue
                eth_amount = wei / WEI_PER_ETH
                short_addr = f"{address[:6]}…{address[-4:]}"
                balances.append(
                    CanonicalBalance(
                        provider="Ethereum",
                        account=f"{short_addr} ({network})",
                        symbol="ETH",
                        currency="ETH",
                        amount=eth_amount,
                        usd_value=None,
                        raw={"address": address, "network": network, "wei": wei},
                    )
                )

        return balances

    async def read_positions(self, user_id: UUID) -> list[CanonicalPosition]:
        creds = await self._get_credentials(user_id)
        async with WallbitClient(api_key=creds.api_key, base_url=self.wallbit_base_url) as wc:
            try:
                stocks_raw = await wc.get_stocks_balance()
            except WallbitAPIError as exc:
                raise APIError(
                    PROVIDER_UNAVAILABLE,
                    http_status=502,
                    message_es="Wallbit no respondió correctamente al buscar posiciones.",
                    message_en="Wallbit upstream error.",
                    details={"status": exc.status, "body": exc.body},
                ) from exc

            stocks_rows = stocks_balance_to_rows(stocks_raw)

            cost_basis_by_symbol: dict[str, dict[str, float]] = {}
            try:
                transactions_raw = await wc.list_transactions(limit=None)
            except WallbitAPIError as exc:
                log.warning(
                    "wallbit_transactions_cost_basis_read_failed",
                    status=exc.status,
                    body=exc.body,
                )
            else:
                cost_basis_by_symbol = transaction_cost_basis_by_symbol(transactions_raw)

        positions = []
        for row in stocks_rows:
            symbol = str(row.get("symbol") or "")
            shares = _float_or_none(row.get("shares")) or 0.0
            basis = cost_basis_by_symbol.get(symbol, {})

            current_price_usd = _float_or_none(row.get("current_price_usd"))
            if current_price_usd is None:
                current_price_usd = basis.get("latest_price_usd")

            usd_value = _float_or_none(row.get("usd_value"))
            if usd_value is None and current_price_usd is not None:
                usd_value = shares * current_price_usd

            avg_cost_usd = _float_or_none(row.get("avg_cost_usd")) or basis.get("avg_cost_usd")
            cost_basis_usd = _float_or_none(row.get("cost_basis_usd"))
            if cost_basis_usd is None and avg_cost_usd is not None:
                cost_basis_usd = shares * avg_cost_usd

            unrealized_pnl_usd = None
            pnl_percentage = None
            if usd_value is not None and cost_basis_usd is not None and cost_basis_usd > 0:
                unrealized_pnl_usd = usd_value - cost_basis_usd
                pnl_percentage = (unrealized_pnl_usd / cost_basis_usd) * 100

            positions.append(
                CanonicalPosition(
                    provider="Wallbit",
                    account=row.get("account", "investment"),
                    symbol=symbol,
                    shares=shares,
                    current_price_usd=current_price_usd,
                    usd_value=usd_value,
                    avg_cost_usd=avg_cost_usd,
                    cost_basis_usd=cost_basis_usd,
                    unrealized_pnl_usd=unrealized_pnl_usd,
                    pnl_percentage=pnl_percentage,
                    raw=row.get("raw", {}),
                )
            )
        return positions

    async def read_transactions(self, user_id: UUID, limit: int = 50) -> list[dict[str, Any]]:
        from sqlalchemy import select

        from app.persistence.models.ledger import CanonicalTransaction

        stmt = (
            select(CanonicalTransaction)
            .where(CanonicalTransaction.user_id == user_id)
            .order_by(CanonicalTransaction.occurred_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        txs = result.scalars().all()

        return [
            {
                "id": str(tx.id),
                "external_id": tx.external_id,
                "type": tx.type,
                "direction": tx.direction,
                "source_amount": float(tx.source_amount) if tx.source_amount else None,
                "source_currency": tx.source_currency,
                "dest_amount": float(tx.dest_amount) if tx.dest_amount else None,
                "dest_unit": tx.dest_unit,
                "fee_amount": float(tx.fee_amount),
                "fee_currency": tx.fee_currency,
                "status": tx.status,
                "occurred_at": tx.occurred_at.isoformat(),
                "classifier": tx.classifier,
                "merchant": tx.merchant,
                "source_kind": tx.source_kind,
            }
            for tx in txs
        ]
