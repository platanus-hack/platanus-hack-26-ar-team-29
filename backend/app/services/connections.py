"""ConnectionService — Wallbit + custodial Ethereum (02-3 §5.13)."""

from __future__ import annotations

import re
from typing import Any
from uuid import UUID

import structlog
from eth_account import Account
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.errors import (
    NETWORK_NOT_ALLOWED,
    NOT_EXPORTABLE,
    NOT_FOUND,
    PROVIDER_UNAVAILABLE,
    VALIDATION_FAILED,
    APIError,
)
from app.persistence.repositories.connections import ConnectionRepository
from app.providers.ethereum.auth import EthereumCustodialCredentials
from app.providers.ethereum.capabilities import PHASE_1_CAPABILITIES
from app.providers.ethereum.networks import (
    MAINNET_NETWORK_SLUGS,
    SUPPORTED_NETWORKS,
    get_network,
)
from app.providers.wallbit.auth import WallbitCredentials
from app.providers.wallbit.client import WallbitAPIError, WallbitClient

log = structlog.get_logger(__name__)

# Enable BIP-39 mnemonic support once at import; this is the documented
# eth-account opt-in.
Account.enable_unaudited_hdwallet_features()


_HEX_PRIVATE_KEY_RE = re.compile(r"^(0x)?[0-9a-fA-F]{64}$")


def _looks_like_mnemonic(s: str) -> bool:
    parts = s.strip().split()
    return len(parts) in (12, 15, 18, 21, 24)


def _looks_like_hex_private_key(s: str) -> bool:
    return bool(_HEX_PRIVATE_KEY_RE.fullmatch(s.strip()))


def _validate_network(network: str) -> None:
    if network in MAINNET_NETWORK_SLUGS:
        raise APIError(
            NETWORK_NOT_ALLOWED,
            http_status=400,
            message_es=(
                "Esta red mainnet no está habilitada. Redes permitidas: "
                "sepolia, holesky, polygon-amoy, arbitrum-sepolia, base-sepolia, base."
            ),
            message_en="This mainnet network is not allowed.",
            params={"network": network},
        )
    if network not in SUPPORTED_NETWORKS:
        raise APIError(
            NETWORK_NOT_ALLOWED,
            http_status=400,
            message_es=(
                "Red desconocida. Usá una de: "
                "sepolia, holesky, polygon-amoy, arbitrum-sepolia, base-sepolia, base."
            ),
            message_en="Unsupported network slug.",
            params={"network": network},
        )


def _normalize_private_key_input(raw: str) -> str:
    """Resolve a hex key OR mnemonic to a 0x-prefixed hex private key.

    Returns the canonical 0x-hex representation. Raises VALIDATION_FAILED with
    Spanish-first messages on any malformed input.
    """
    s = (raw or "").strip()
    if not s:
        raise APIError(
            VALIDATION_FAILED,
            http_status=400,
            message_es="La clave privada o frase mnemónica no puede estar vacía.",
            message_en="Empty private key / mnemonic.",
        )

    if _looks_like_hex_private_key(s):
        try:
            acct = Account.from_key(s if s.startswith("0x") else "0x" + s)
        except Exception as exc:
            raise APIError(
                VALIDATION_FAILED,
                http_status=400,
                message_es="La clave privada no es válida.",
                message_en="Invalid private key.",
            ) from exc
        return _ensure_hex_prefix(acct.key.hex())

    if _looks_like_mnemonic(s):
        try:
            acct = Account.from_mnemonic(s)
        except Exception as exc:
            raise APIError(
                VALIDATION_FAILED,
                http_status=400,
                message_es=(
                    "La frase mnemónica no es válida (revisá la cantidad de "
                    "palabras y el checksum BIP-39)."
                ),
                message_en="Invalid BIP-39 mnemonic.",
            ) from exc
        return _ensure_hex_prefix(acct.key.hex())

    raise APIError(
        VALIDATION_FAILED,
        http_status=400,
        message_es=(
            "Formato no reconocido. Enviá una clave privada hex de 32 bytes "
            "(con o sin prefijo 0x) o una frase BIP-39 de 12 / 24 palabras."
        ),
        message_en="Could not detect input shape (hex key vs mnemonic).",
    )


def _ensure_hex_prefix(key_hex: str) -> str:
    return key_hex if key_hex.startswith("0x") else "0x" + key_hex


class ConnectionService:
    def __init__(self, session: AsyncSession, wallbit_base_url: str) -> None:
        self.session = session
        self.wallbit_base_url = wallbit_base_url
        self.repo = ConnectionRepository(session)

    # ------------------- Wallbit (existing) -------------------

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
        out: list[dict[str, Any]] = []
        for c in rows:
            row: dict[str, Any] = {
                "id": str(c.id),
                "connection_type": c.connection_type,
                "label": c.label,
                "status": c.status,
                "capabilities": list(c.capabilities),
                "created_at": c.created_at.isoformat().replace("+00:00", "Z"),
            }
            # Surface the address + network for ethereum_custodial without
            # decrypting credentials.
            md = dict(c.connection_metadata or {})
            if c.connection_type == "ethereum_custodial":
                if "address" in md:
                    row["address"] = md["address"]
                if "network" in md:
                    row["network"] = md["network"]
                if "chain_id" in md:
                    row["chain_id"] = md["chain_id"]
                if "primary_asset_hint" in md:
                    row["primary_asset_hint"] = md["primary_asset_hint"]
            out.append(row)
        return out

    async def get_active_wallbit_credentials(
        self, user_id: UUID
    ) -> tuple[UUID, WallbitCredentials] | None:
        conn = await self.repo.get_active_wallbit(user_id)
        if conn is None:
            return None
        creds = WallbitCredentials.from_blob(bytes(conn.credentials_encrypted))
        return conn.id, creds

    # ------------------- Ethereum custodial -------------------

    def _build_eth_response(
        self,
        conn_id: UUID,
        label: str | None,
        address: str,
        network: str,
        chain_id: int,
        primary_asset_hint: str | None,
        capabilities: list[str],
        created_at_iso: str,
    ) -> dict[str, Any]:
        return {
            "id": str(conn_id),
            "connection_type": "ethereum_custodial",
            "label": label,
            "address": address,
            "network": network,
            "chain_id": chain_id,
            "primary_asset_hint": primary_asset_hint,
            "capabilities": capabilities,
            "created_at": created_at_iso,
        }

    async def import_ethereum_custodial(
        self,
        user_id: UUID,
        network: str,
        private_key_or_mnemonic: str,
        label: str | None,
        primary_asset_hint: str | None,
    ) -> dict[str, Any]:
        _validate_network(network)
        net = get_network(network)
        # _validate_network guarantees this; assert for type narrowing.
        assert net is not None

        # NOTE: We intentionally do NOT log the input here — even at DEBUG.
        # Audit redaction (02-3 §16 q6) covers private_key + mnemonic keys.
        priv_hex = _normalize_private_key_input(private_key_or_mnemonic)
        priv_hex = _ensure_hex_prefix(priv_hex)
        try:
            address = Account.from_key(priv_hex).address
        except Exception as exc:
            raise APIError(
                VALIDATION_FAILED,
                http_status=400,
                message_es="No pudimos derivar una dirección desde la clave provista.",
                message_en="Could not derive address from private key.",
            ) from exc

        creds = EthereumCustodialCredentials(private_key=priv_hex, network=network)
        blob = creds.to_blob()
        metadata: dict[str, Any] = {
            "address": address,
            "network": network,
            "chain_id": net.chain_id,
        }
        if primary_asset_hint:
            metadata["primary_asset_hint"] = primary_asset_hint

        conn = await self.repo.create_ethereum_custodial(
            user_id=user_id,
            label=label,
            credentials_encrypted=blob,
            capabilities=list(PHASE_1_CAPABILITIES),
            metadata=metadata,
        )
        await self.session.commit()
        log.info(
            "ethereum_custodial_imported",
            connection_id=str(conn.id),
            network=network,
            address=address,
            # private_key intentionally omitted from logs.
        )
        return self._build_eth_response(
            conn_id=conn.id,
            label=conn.label,
            address=address,
            network=network,
            chain_id=net.chain_id,
            primary_asset_hint=primary_asset_hint,
            capabilities=list(conn.capabilities),
            created_at_iso=conn.created_at.isoformat().replace("+00:00", "Z"),
        )

    async def create_ethereum_custodial(
        self,
        user_id: UUID,
        network: str,
        label: str | None,
        primary_asset_hint: str | None,
    ) -> dict[str, Any]:
        _validate_network(network)
        net = get_network(network)
        assert net is not None

        acct, mnemonic = Account.create_with_mnemonic()
        priv_hex = acct.key.hex()
        priv_hex = _ensure_hex_prefix(priv_hex)
        address = acct.address

        creds = EthereumCustodialCredentials(private_key=priv_hex, network=network)
        blob = creds.to_blob()
        metadata: dict[str, Any] = {
            "address": address,
            "network": network,
            "chain_id": net.chain_id,
            "manual_gas_funding_required": True,
        }
        if primary_asset_hint:
            metadata["primary_asset_hint"] = primary_asset_hint

        conn = await self.repo.create_ethereum_custodial(
            user_id=user_id,
            label=label,
            credentials_encrypted=blob,
            capabilities=list(PHASE_1_CAPABILITIES),
            metadata=metadata,
        )
        await self.session.commit()
        log.info(
            "ethereum_custodial_created",
            connection_id=str(conn.id),
            network=network,
            address=address,
            # mnemonic + private_key intentionally omitted from logs.
        )
        return {
            "id": str(conn.id),
            "address": address,
            "network": network,
            "chain_id": net.chain_id,
            "mnemonic": mnemonic,
            "warning_es": (
                "Esta es la única vez que verás esta frase. Guardala ahora si "
                "querés exportar la billetera. Tu billetera arranca con 0 ETH "
                "— mandale gas desde un faucet de testnet antes de transferir."
            ),
            "warning_en": (
                "This mnemonic is shown once. Save it now if you may want to "
                "export this wallet later. The wallet starts with 0 ETH — "
                "fund it from a testnet faucet before any transfer."
            ),
            "created_at": conn.created_at.isoformat().replace("+00:00", "Z"),
        }

    async def export_private_key(self, user_id: UUID, connection_id: UUID) -> dict[str, Any]:
        conn = await self.repo.get_by_id(connection_id, user_id)
        if conn is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="No encontramos esa conexión.",
                message_en="Connection not found.",
            )
        if conn.connection_type != "ethereum_custodial":
            # Per 02-3 §5.13.5: non-custodial Ethereum (and every other
            # provider) can never have its key exported because we don't
            # store one server-side.
            raise APIError(
                NOT_EXPORTABLE,
                http_status=400,
                message_es=(
                    "Esta conexión no es custodial: no tenemos clave privada para exportar."
                ),
                message_en="Connection is not custodial; no private key to export.",
            )
        if conn.disconnected_at is not None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="Esta conexión fue desconectada.",
                message_en="Connection has been disconnected.",
            )

        creds = EthereumCustodialCredentials.from_blob(bytes(conn.credentials_encrypted))
        md = dict(conn.connection_metadata or {})
        # NOTE: never log the private_key. The successful export is logged with
        # tool="export_private_key" and the value redacted (02-3 §5.13.5).
        log.info(
            "export_private_key_success",
            tool="export_private_key",
            connection_id=str(conn.id),
            success=True,
        )
        return {
            "private_key": creds.private_key,
            "address": md.get("address"),
            "network": creds.network,
            "warning_es": (
                "Esta clave privada controla tu billetera. No la compartas. "
                "Si la perdés o la filtrás, perdés los fondos."
            ),
            "warning_en": (
                "This private key controls your wallet. Do not share it. "
                "Losing or leaking it means losing the funds."
            ),
        }

    async def get_active_ethereum_custodial(
        self, user_id: UUID, connection_id: UUID
    ) -> tuple[UUID, EthereumCustodialCredentials, dict[str, Any]]:
        """Return (connection_id, decrypted creds, metadata) or raise NOT_FOUND."""
        conn = await self.repo.get_active_ethereum_custodial(connection_id, user_id)
        if conn is None:
            raise APIError(
                NOT_FOUND,
                http_status=404,
                message_es="No encontramos esa conexión Ethereum custodial.",
                message_en="Ethereum custodial connection not found.",
            )
        creds = EthereumCustodialCredentials.from_blob(bytes(conn.credentials_encrypted))
        return conn.id, creds, dict(conn.connection_metadata or {})
