"""On-chain (custodial Ethereum) transfer + gas + simulate service.

Phase 1: ETH and ERC-20 (USDC) transfers on testnets only. See 02-3 §5.13.2.
DeFi (Aave / Morpho) lands in Phase 2 in a sibling module.
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
    INVALID_ADDRESS,
    PROVIDER_UNAVAILABLE,
    VALIDATION_FAILED,
    APIError,
)
from app.providers.ethereum.client import EthereumClient, EthereumClientError
from app.providers.ethereum.networks import get_network
from app.services.connections import ConnectionService

log = structlog.get_logger(__name__)


# Multipliers applied to the network's reported gas price for the three
# user-facing tiers. The numbers are intentionally simple — testnets don't have
# the volatility that justifies a richer model in v1.
_GAS_SPEED_MULTIPLIERS = {
    "slow": Decimal("0.85"),
    "standard": Decimal("1.0"),
    "fast": Decimal("1.25"),
}


# Gas-units estimate used when surfacing fee_estimate on simulate / transfer
# replies. Replaced by a real estimate where one is available.
_DEFAULT_GAS_UNITS = {
    "ETH": 21_000,
    "ERC20": 65_000,
}


class OnchainService:
    def __init__(
        self,
        session: AsyncSession,
        connection_service: ConnectionService,
        eth_client: EthereumClient,
    ) -> None:
        self.session = session
        self._conns = connection_service
        self._eth = eth_client

    # ------------------- gas suggestion -------------------

    async def get_gas(self, user_id: UUID, connection_id: UUID) -> dict[str, Any]:
        _, _creds, md = await self._conns.get_active_ethereum_custodial(user_id, connection_id)
        network = md.get("network")
        if not network:
            raise APIError(
                VALIDATION_FAILED,
                http_status=500,
                message_es="La conexión no tiene red asociada.",
                message_en="Connection metadata missing network.",
            )

        try:
            gas_price_wei = await self._eth.get_gas_price_wei(network)
        except EthereumClientError as exc:
            raise APIError(
                PROVIDER_UNAVAILABLE,
                http_status=502,
                message_es=exc.user_message_es,
                message_en="Failed to fetch gas price.",
            ) from exc

        tiers: dict[str, dict[str, Any]] = {}
        for name, mul in _GAS_SPEED_MULTIPLIERS.items():
            wei = int(Decimal(int(gas_price_wei)) * mul)
            tiers[name] = {
                "gas_price_wei": str(wei),
                "gas_price_gwei": EthereumClient.wei_to_gwei_float(wei),
            }
        return {
            "network": network,
            "base_gas_price_wei": str(gas_price_wei),
            "base_gas_price_gwei": EthereumClient.wei_to_gwei_float(gas_price_wei),
            "tiers": tiers,
        }

    # ------------------- simulate -------------------

    async def simulate(
        self,
        user_id: UUID,
        connection_id: UUID,
        asset: str,
        to: str,
        amount: str,
    ) -> dict[str, Any]:
        _, creds, md = await self._conns.get_active_ethereum_custodial(user_id, connection_id)
        network = creds.network
        net = get_network(network)
        assert net is not None
        if not EthereumClient.is_address(to):
            raise APIError(
                INVALID_ADDRESS,
                http_status=400,
                message_es="La dirección destino no es válida.",
                message_en="Invalid recipient address.",
            )
        from_addr = md.get("address") or EthereumClient.derive_address(creds.private_key)
        asset_u = (asset or "").strip().upper()

        try:
            if asset_u == "ETH":
                amount_wei = _eth_amount_to_wei(amount)
                tx = {
                    "from": EthereumClient.to_checksum(from_addr),
                    "to": EthereumClient.to_checksum(to),
                    "value": amount_wei,
                }
                result = await self._eth.simulate_call(network, tx)
            else:
                token = net.erc20_contracts.get(asset_u)
                if not token:
                    raise APIError(
                        ASSET_NOT_SUPPORTED,
                        http_status=400,
                        message_es=(f"El activo {asset_u} no está disponible en {network}."),
                        message_en=f"Asset {asset_u} not supported on {network}.",
                    )
                # For ERC-20 we just delegate to estimate_gas / call against the
                # transfer() function. Build an unsigned tx via build_transaction.
                contract_addr = EthereumClient.to_checksum(token)
                # Raw amount in token units uses on-chain decimals — fetch them.
                _bal_raw, decimals = await self._eth.get_erc20_balance(
                    network, from_addr, contract_addr
                )
                amount_raw = _decimal_amount_to_raw(amount, decimals)
                tx = await _build_erc20_transfer_call(
                    self._eth, network, from_addr, contract_addr, to, amount_raw
                )
                result = await self._eth.simulate_call(network, tx)
        except APIError:
            raise
        except EthereumClientError as exc:
            raise APIError(
                PROVIDER_UNAVAILABLE,
                http_status=502,
                message_es=exc.user_message_es,
                message_en="Simulation failed.",
            ) from exc

        return {
            "network": network,
            "asset": asset_u,
            "ok": bool(result.get("ok")),
            "gas_estimate": result.get("gas_estimate"),
            "revert_summary": result.get("revert_summary"),
        }

    # ------------------- transfer -------------------

    async def transfer(
        self,
        user_id: UUID,
        connection_id: UUID,
        asset: str,
        to: str,
        amount: str,
        gas_speed: str | None = None,
    ) -> dict[str, Any]:
        _, creds, md = await self._conns.get_active_ethereum_custodial(user_id, connection_id)
        network = creds.network
        net = get_network(network)
        assert net is not None

        if not EthereumClient.is_address(to):
            raise APIError(
                INVALID_ADDRESS,
                http_status=400,
                message_es="La dirección destino no es válida.",
                message_en="Invalid recipient address.",
            )

        speed = (gas_speed or "standard").lower()
        if speed not in _GAS_SPEED_MULTIPLIERS:
            raise APIError(
                VALIDATION_FAILED,
                http_status=400,
                message_es="gas_speed debe ser slow, standard o fast.",
                message_en="gas_speed must be slow / standard / fast.",
                params={"gas_speed": gas_speed},
            )

        asset_u = (asset or "").strip().upper()

        try:
            if asset_u == "ETH":
                amount_wei = _eth_amount_to_wei(amount)
                result = await self._eth.send_eth(
                    network=network,
                    from_priv=creds.private_key,
                    to=to,
                    amount_wei=amount_wei,
                )
                gas_units = int(result.get("gas") or _DEFAULT_GAS_UNITS["ETH"])
            else:
                token = net.erc20_contracts.get(asset_u)
                if not token:
                    raise APIError(
                        ASSET_NOT_SUPPORTED,
                        http_status=400,
                        message_es=(f"El activo {asset_u} no está disponible en {network}."),
                        message_en=f"Asset {asset_u} not supported on {network}.",
                    )
                from_addr = md.get("address") or EthereumClient.derive_address(creds.private_key)
                _bal_raw, decimals = await self._eth.get_erc20_balance(network, from_addr, token)
                amount_raw = _decimal_amount_to_raw(amount, decimals)
                result = await self._eth.send_erc20(
                    network=network,
                    from_priv=creds.private_key,
                    token_contract=token,
                    to=to,
                    amount_raw=amount_raw,
                )
                gas_units = int(result.get("gas") or _DEFAULT_GAS_UNITS["ERC20"])
        except APIError:
            raise
        except EthereumClientError as exc:
            # Heuristic: web3 reverts that mention "insufficient" balance/funds
            # bubble up as a structured INSUFFICIENT_FUNDS rather than a generic
            # 502. We deliberately do not surface raw revert strings.
            raw_lower = (exc.raw or "").lower()
            if "insufficient" in raw_lower or "exceeds balance" in raw_lower:
                raise APIError(
                    INSUFFICIENT_FUNDS,
                    http_status=400,
                    message_es=("Saldo insuficiente para esta transferencia (incluyendo gas)."),
                    message_en="Insufficient funds for transfer (including gas).",
                ) from exc
            raise APIError(
                PROVIDER_UNAVAILABLE,
                http_status=502,
                message_es=exc.user_message_es,
                message_en="On-chain transfer failed.",
            ) from exc

        gas_price_wei = int(result.get("gas_price_wei") or 0)
        # Apply the user's chosen multiplier to the surfaced fee estimate. We
        # don't override the actual broadcast tx: in v1 we rely on the node's
        # base gas price for simplicity. The multiplier is reflected in the
        # returned ``gas_estimate_gwei`` so the caller sees their tier.
        adjusted_gas_price = int(Decimal(gas_price_wei) * _GAS_SPEED_MULTIPLIERS[speed])
        fee_wei = adjusted_gas_price * gas_units
        tx_hash = result["tx_hash"]
        if not tx_hash.startswith("0x"):
            tx_hash = "0x" + tx_hash
        explorer = net.explorer_tx_template.format(hash=tx_hash)

        # TODO(phase-1.1): stream status transitions over the connection.<id>
        # WebSocket topic per 02-3 §5.13.2; that topic doesn't exist yet.
        log.info(
            "onchain_transfer_broadcast",
            connection_id=str(connection_id),
            network=network,
            asset=asset_u,
            tx_hash=tx_hash,
            gas_units=gas_units,
            gas_speed=speed,
        )
        return {
            "tx_hash": tx_hash,
            "status": "pending",
            "block_explorer_url": explorer,
            "gas_estimate_gwei": EthereumClient.wei_to_gwei_float(adjusted_gas_price),
            "fee_estimate_eth": EthereumClient.wei_to_eth_str(fee_wei),
        }


# ---------- helpers ----------


def _eth_amount_to_wei(amount: str) -> int:
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
    return int((d * Decimal(10**18)).to_integral_value())


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


async def _build_erc20_transfer_call(
    eth: EthereumClient,
    network: str,
    from_addr: str,
    token_addr: str,
    to: str,
    amount_raw: int,
) -> dict[str, Any]:
    """Build an ``eth_call``-shaped tx for ERC-20 ``transfer``.

    We hand-encode the call data to avoid pulling another web3 dependency into
    this layer. Function selector for ``transfer(address,uint256)`` is 0xa9059cbb.
    """
    selector = "a9059cbb"
    to_padded = to.lower().replace("0x", "").rjust(64, "0")
    amount_hex = format(int(amount_raw), "x").rjust(64, "0")
    data = "0x" + selector + to_padded + amount_hex
    return {
        "from": EthereumClient.to_checksum(from_addr),
        "to": EthereumClient.to_checksum(token_addr),
        "data": data,
    }
