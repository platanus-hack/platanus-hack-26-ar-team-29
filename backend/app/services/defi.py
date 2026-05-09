"""DeFi service — Aave V3 supply / withdraw / market reads (02-3 §5.13.3).

Phase 2 surface. v1 supports Aave V3 only; the registry in `aave.py` ships
Base mainnet + USDC, and is the only place to extend for new (network, asset)
pairs. Morpho lands later in a sibling adapter that exposes the same shapes.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import (
    ASSET_NOT_SUPPORTED,
    INSUFFICIENT_FUNDS,
    NOT_FOUND,
    PROVIDER_UNAVAILABLE,
    VALIDATION_FAILED,
    APIError,
)
from app.providers.ethereum import aave
from app.providers.ethereum.client import EthereumClient, EthereumClientError
from app.providers.ethereum.networks import get_network
from app.services.connections import ConnectionService

log = structlog.get_logger(__name__)


SUPPORTED_PROTOCOLS = frozenset({"aave"})

# Sentinel for "withdraw all" — Aave V3 treats `type(uint256).max` as
# "balance of caller in this market". Same trick saves a balance read.
_UINT256_MAX = (1 << 256) - 1


class DefiService:
    def __init__(
        self,
        session: AsyncSession,
        connection_service: ConnectionService,
        eth_client: EthereumClient,
    ) -> None:
        self.session = session
        self._conns = connection_service
        self._eth = eth_client

    # ---------------- read paths ----------------

    async def list_markets(
        self,
        protocol: str | None = None,
        network: str | None = None,
        asset: str | None = None,
        min_apy: float | None = None,
    ) -> list[dict[str, Any]]:
        if protocol and protocol.lower() not in SUPPORTED_PROTOCOLS:
            return []
        markets = aave.list_markets(network=network, asset_symbol=asset)
        out: list[dict[str, Any]] = []
        for m in markets:
            try:
                payload = await self._build_market_payload(m)
            except EthereumClientError as exc:
                log.warning(
                    "aave_market_read_failed",
                    network=m.network,
                    asset=m.asset_symbol,
                    error=str(exc),
                )
                continue
            if min_apy is not None and payload["supply_apy"] < min_apy:
                continue
            out.append(payload)
        return out

    async def get_market(self, protocol: str, market_id: str) -> dict[str, Any]:
        if protocol.lower() not in SUPPORTED_PROTOCOLS:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es=f"Protocolo {protocol} no soportado.",
                message_en=f"Protocol {protocol} not supported.",
            )
        parsed = aave.parse_market_id(market_id)
        if not parsed:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="market_id desconocido.",
                message_en="Unknown market_id.",
                params={"market_id": market_id},
            )
        network, symbol = parsed
        m = aave.get_market(network, symbol)
        if not m:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="market_id desconocido.",
                message_en="Unknown market_id.",
                params={"market_id": market_id},
            )
        try:
            return await self._build_market_payload(m)
        except EthereumClientError as exc:
            raise APIError(
                PROVIDER_UNAVAILABLE,
                http_status=502,
                message_es=exc.user_message_es,
                message_en="Failed to read market data from RPC.",
            ) from exc

    async def list_positions(self, user_id: UUID, connection_id: UUID) -> list[dict[str, Any]]:
        _, creds, md = await self._conns.get_active_ethereum_custodial(user_id, connection_id)
        network = creds.network
        user_addr = md.get("address") or EthereumClient.derive_address(creds.private_key)

        out: list[dict[str, Any]] = []
        for m in aave.list_markets(network=network):
            try:
                supplied_raw, _ = await self._eth.get_erc20_balance(network, user_addr, m.a_token)
            except EthereumClientError as exc:
                log.warning(
                    "aave_position_read_failed",
                    network=network,
                    asset=m.asset_symbol,
                    error=str(exc),
                )
                continue
            if supplied_raw <= 0:
                continue
            supplied = _raw_to_decimal_str(supplied_raw, m.decimals)
            try:
                reserve = await self._eth.aave_get_reserve_data(network, m.pool, m.asset_address)
            except EthereumClientError:
                # Position is real even if rates are momentarily unreadable; surface zero APY.
                reserve = {"current_liquidity_rate": 0}
            apy = aave.ray_apr_to_apy(int(reserve["current_liquidity_rate"]))
            out.append(
                {
                    "position_id": f"aave-v3-{network}-{m.asset_symbol}-{user_addr.lower()[:10]}",
                    "protocol": "aave",
                    "market_id": aave.market_id(m),
                    "network": network,
                    "asset": {
                        "symbol": m.asset_symbol,
                        "contract_address": m.asset_address,
                        "decimals": m.decimals,
                    },
                    "supplied_amount": supplied,
                    "supplied_usd": supplied,  # USDC ≈ 1 USD; documented in defi.md.
                    "supply_apy": apy,
                    "estimated_annual_yield_usd": str(
                        (Decimal(supplied) * Decimal(str(apy))).quantize(Decimal("0.01"))
                    ),
                }
            )
        return out

    # ---------------- write paths ----------------

    async def supply(
        self,
        user_id: UUID,
        connection_id: UUID,
        protocol: str,
        market_id: str,
        asset: str,
        amount: str,
    ) -> dict[str, Any]:
        m, network, creds, md = await self._resolve_market(
            user_id, connection_id, protocol, market_id, asset
        )
        amount_raw = _decimal_amount_to_raw(amount, m.decimals)
        user_addr = md.get("address") or EthereumClient.derive_address(creds.private_key)
        net = get_network(network)
        assert net is not None  # guaranteed by allowlist check upstream

        try:
            allowance = await self._eth.erc20_allowance(network, user_addr, m.asset_address, m.pool)
        except EthereumClientError as exc:
            raise APIError(
                PROVIDER_UNAVAILABLE,
                http_status=502,
                message_es=exc.user_message_es,
                message_en="Failed to read ERC-20 allowance.",
            ) from exc

        approve_tx_hash: str | None = None
        if allowance < amount_raw:
            try:
                approve_res = await self._eth.erc20_approve(
                    network=network,
                    from_priv=creds.private_key,
                    token_contract=m.asset_address,
                    spender=m.pool,
                    amount_raw=_UINT256_MAX,
                )
            except EthereumClientError as exc:
                raise APIError(
                    PROVIDER_UNAVAILABLE,
                    http_status=502,
                    message_es=exc.user_message_es,
                    message_en="ERC-20 approve failed.",
                ) from exc
            approve_tx_hash = _ensure_0x(approve_res["tx_hash"])

        try:
            supply_res = await self._eth.aave_supply(
                network=network,
                from_priv=creds.private_key,
                pool_address=m.pool,
                asset_address=m.asset_address,
                amount_raw=amount_raw,
            )
        except EthereumClientError as exc:
            raise self._wrap_write_error(exc, "supply") from exc

        supply_tx_hash = _ensure_0x(supply_res["tx_hash"])

        # Estimate annual yield using the latest supply APY for the market.
        try:
            reserve = await self._eth.aave_get_reserve_data(network, m.pool, m.asset_address)
            apy = aave.ray_apr_to_apy(int(reserve["current_liquidity_rate"]))
        except EthereumClientError:
            apy = 0.0
        eay_usd = str((Decimal(amount) * Decimal(str(apy))).quantize(Decimal("0.01")))

        explorer_urls = []
        if approve_tx_hash:
            explorer_urls.append(net.explorer_tx_template.format(hash=approve_tx_hash))
        explorer_urls.append(net.explorer_tx_template.format(hash=supply_tx_hash))

        log.info(
            "defi_supply_broadcast",
            connection_id=str(connection_id),
            protocol="aave",
            market_id=aave.market_id(m),
            network=network,
            asset=m.asset_symbol,
            amount=amount,
            approve_tx_hash=approve_tx_hash,
            supply_tx_hash=supply_tx_hash,
        )
        return {
            "approve_tx_hash": approve_tx_hash,
            "supply_tx_hash": supply_tx_hash,
            "position_id": f"aave-v3-{network}-{m.asset_symbol}-{user_addr.lower()[:10]}",
            "supplied_amount": amount,
            "estimated_annual_yield_usd": eay_usd,
            "block_explorer_urls": explorer_urls,
        }

    async def withdraw(
        self,
        user_id: UUID,
        connection_id: UUID,
        protocol: str,
        market_id: str,
        asset: str,
        amount: str,
    ) -> dict[str, Any]:
        m, network, creds, md = await self._resolve_market(
            user_id, connection_id, protocol, market_id, asset
        )
        user_addr = md.get("address") or EthereumClient.derive_address(creds.private_key)
        net = get_network(network)
        assert net is not None

        if isinstance(amount, str) and amount.strip().lower() == "max":
            amount_raw = _UINT256_MAX
            display_amount = "max"
        else:
            amount_raw = _decimal_amount_to_raw(amount, m.decimals)
            display_amount = amount

        try:
            withdraw_res = await self._eth.aave_withdraw(
                network=network,
                from_priv=creds.private_key,
                pool_address=m.pool,
                asset_address=m.asset_address,
                amount_raw=amount_raw,
                to=user_addr,
            )
        except EthereumClientError as exc:
            raise self._wrap_write_error(exc, "withdraw") from exc

        tx_hash = _ensure_0x(withdraw_res["tx_hash"])

        log.info(
            "defi_withdraw_broadcast",
            connection_id=str(connection_id),
            protocol="aave",
            market_id=aave.market_id(m),
            network=network,
            asset=m.asset_symbol,
            amount=display_amount,
            tx_hash=tx_hash,
        )
        return {
            "withdraw_tx_hash": tx_hash,
            "withdrawn_amount": display_amount,
            "block_explorer_urls": [net.explorer_tx_template.format(hash=tx_hash)],
        }

    # ---------------- internals ----------------

    async def _build_market_payload(self, m: aave.AaveMarket) -> dict[str, Any]:
        reserve = await self._eth.aave_get_reserve_data(m.network, m.pool, m.asset_address)
        supply_apy = aave.ray_apr_to_apy(int(reserve["current_liquidity_rate"]))
        borrow_apy = aave.ray_apr_to_apy(int(reserve["current_variable_borrow_rate"]))
        a_token_supply = await self._eth.erc20_total_supply(m.network, m.a_token)
        try:
            v_debt_supply = await self._eth.erc20_total_supply(
                m.network, reserve["variable_debt_token_address"]
            )
        except EthereumClientError:
            v_debt_supply = 0
        total_supplied = _raw_to_decimal_str(a_token_supply, m.decimals)
        util = aave.utilization(a_token_supply, v_debt_supply)
        return {
            "protocol": "aave",
            "market_id": aave.market_id(m),
            "asset": {
                "symbol": m.asset_symbol,
                "contract_address": m.asset_address,
                "decimals": m.decimals,
            },
            "network": m.network,
            "supply_apy": supply_apy,
            "borrow_apy": borrow_apy,
            # USDC ≈ 1 USD assumption; ok for the ship-it demo, swap for a
            # price oracle when `list_markets` returns multiple assets.
            "total_supplied_usd": total_supplied,
            "utilization": util,
            "tvl_usd": total_supplied,
        }

    async def _resolve_market(
        self,
        user_id: UUID,
        connection_id: UUID,
        protocol: str,
        market_id: str,
        asset: str,
    ) -> tuple[aave.AaveMarket, str, Any, dict[str, Any]]:
        if protocol.lower() not in SUPPORTED_PROTOCOLS:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es=f"Protocolo {protocol} no soportado.",
                message_en=f"Protocol {protocol} not supported.",
                params={"protocol": protocol},
            )
        parsed = aave.parse_market_id(market_id)
        if not parsed:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="market_id desconocido.",
                message_en="Unknown market_id.",
                params={"market_id": market_id},
            )
        market_network, market_symbol = parsed
        if asset and asset.upper() != market_symbol:
            raise APIError(
                VALIDATION_FAILED,
                http_status=400,
                message_es="El asset no coincide con el market_id.",
                message_en="asset does not match market_id.",
                params={"asset": asset, "market_id": market_id},
            )
        m = aave.get_market(market_network, market_symbol)
        if not m:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="market_id desconocido.",
                message_en="Unknown market_id.",
                params={"market_id": market_id},
            )

        _, creds, md = await self._conns.get_active_ethereum_custodial(user_id, connection_id)
        if creds.network != market_network:
            raise APIError(
                ASSET_NOT_SUPPORTED,
                http_status=400,
                message_es=(
                    f"La conexión está en {creds.network} y el mercado en {market_network}."
                ),
                message_en="Connection network does not match market network.",
                params={
                    "connection_network": creds.network,
                    "market_network": market_network,
                },
            )
        return m, market_network, creds, md

    @staticmethod
    def _wrap_write_error(exc: EthereumClientError, op: str) -> APIError:
        raw_lower = (exc.raw or "").lower()
        if "insufficient" in raw_lower or "exceeds balance" in raw_lower:
            return APIError(
                INSUFFICIENT_FUNDS,
                http_status=400,
                message_es="Saldo insuficiente para esta operación (incluyendo gas).",
                message_en="Insufficient funds for the operation (including gas).",
            )
        return APIError(
            PROVIDER_UNAVAILABLE,
            http_status=502,
            message_es=exc.user_message_es,
            message_en=f"On-chain {op} failed.",
        )


# ---------------- helpers ----------------


def _decimal_amount_to_raw(amount: str, decimals: int) -> int:
    try:
        d = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise APIError(
            VALIDATION_FAILED,
            http_status=400,
            message_es="El monto no es un número válido.",
            message_en="amount is not a valid decimal.",
        ) from exc
    if d <= 0:
        raise APIError(
            VALIDATION_FAILED,
            http_status=400,
            message_es="El monto debe ser mayor que cero.",
            message_en="amount must be > 0.",
        )
    return int((d * (Decimal(10) ** decimals)).to_integral_value())


def _raw_to_decimal_str(raw: int, decimals: int) -> str:
    if raw == 0:
        return "0"
    d = Decimal(int(raw)) / (Decimal(10) ** decimals)
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


def _ensure_0x(h: str) -> str:
    return h if h.startswith("0x") else "0x" + h
