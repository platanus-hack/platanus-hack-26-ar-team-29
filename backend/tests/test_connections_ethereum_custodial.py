"""End-to-end shape tests for the custodial Ethereum REST surface.

These run against the real FastAPI app, including the real Postgres DB pointed
at by ``DATABASE_URL``. If the DB is unreachable (no FERNET_KEY, no Postgres,
or the schema is out of date) the tests skip rather than fail. CI is
responsible for spinning up a DB and running migrations before invoking pytest.
"""

from __future__ import annotations

import asyncio
import socket
from urllib.parse import urlparse

import pytest


def _parse_db_host_port() -> tuple[str, int]:
    from app.config import get_settings

    settings = get_settings()
    url = settings.database_url
    parsed = urlparse(url.replace("postgresql+asyncpg", "postgresql"))
    return parsed.hostname or "localhost", parsed.port or 5432


def _db_reachable() -> bool:
    from app.config import get_settings

    settings = get_settings()
    if not settings.fernet_key:
        return False
    host, port = _parse_db_host_port()
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


# Runtime gate: skip the entire module if no DB is reachable at collection time.
# This keeps the default ``uv run pytest -q`` run green on a dev machine that
# hasn't booted Postgres while still exercising the path in CI.
pytestmark = pytest.mark.skipif(
    not _db_reachable(),
    reason="no DATABASE_URL/Postgres reachable + FERNET_KEY missing — see backend/docs/testing.md",
)


KNOWN_HEX = "0x" + "11" * 32
KNOWN_HEX_ADDRESS = None  # filled in by the first test that imports eth_account.

CANONICAL_MNEMONIC = (
    "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
)
CANONICAL_MNEMONIC_ADDRESS = "0x9858EfFD232B4033E47d90003D41EC34EcaEda94"


def _expected_hex_address() -> str:
    from eth_account import Account

    return Account.from_key(KNOWN_HEX).address


def test_import_with_hex_returns_address(sync_client) -> None:  # type: ignore[no-untyped-def]
    body = {
        "network": "sepolia",
        "private_key": KNOWN_HEX,
        "label": "Mi Sepolia",
        "primary_asset_hint": "USDC",
    }
    r = sync_client.post("/api/v1/connections/ethereum-custodial/import", json=body)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["connection_type"] == "ethereum_custodial"
    assert data["network"] == "sepolia"
    assert data["chain_id"] == 11155111
    assert data["address"].lower() == _expected_hex_address().lower()
    assert "send_onchain" in data["capabilities"]
    assert "id" in data


def test_import_with_mnemonic_matches_address(sync_client) -> None:  # type: ignore[no-untyped-def]
    body = {
        "network": "sepolia",
        "private_key": CANONICAL_MNEMONIC,
        "label": "Demo mnemonic",
    }
    r = sync_client.post("/api/v1/connections/ethereum-custodial/import", json=body)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["address"] == CANONICAL_MNEMONIC_ADDRESS


def test_import_mainnet_rejected(sync_client) -> None:  # type: ignore[no-untyped-def]
    # "base" is intentionally allowed (deviation §9); other mainnets remain rejected.
    for net in ("mainnet", "polygon", "arbitrum", "optimism"):
        r = sync_client.post(
            "/api/v1/connections/ethereum-custodial/import",
            json={"network": net, "private_key": KNOWN_HEX},
        )
        assert r.status_code == 400, f"{net} should be rejected"
        assert r.json()["error"]["code"] == "NETWORK_NOT_ALLOWED"


def test_import_invalid_input_rejected(sync_client) -> None:  # type: ignore[no-untyped-def]
    r = sync_client.post(
        "/api/v1/connections/ethereum-custodial/import",
        json={"network": "sepolia", "private_key": "not a key"},
    )
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "VALIDATION_FAILED"


def test_create_returns_mnemonic_then_omitted_on_list(sync_client) -> None:  # type: ignore[no-untyped-def]
    r = sync_client.post(
        "/api/v1/connections/ethereum-custodial/create",
        json={"network": "sepolia", "label": "Demo wallet"},
    )
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert "mnemonic" in data
    assert len(data["mnemonic"].split()) == 12
    assert data["address"].startswith("0x")
    assert data["network"] == "sepolia"
    assert "warning_es" in data
    conn_id = data["id"]

    # Subsequent reads omit the mnemonic.
    r2 = sync_client.get("/api/v1/connections")
    assert r2.status_code == 200
    listed = r2.json()
    matching = [c for c in listed if c["id"] == conn_id]
    assert matching, "newly-created connection should be listed"
    assert "mnemonic" not in matching[0]
    assert matching[0]["address"] == data["address"]


def test_export_private_key_for_custodial(sync_client) -> None:  # type: ignore[no-untyped-def]
    # Create a fresh wallet so the exported key matches what's stored.
    cr = sync_client.post(
        "/api/v1/connections/ethereum-custodial/create",
        json={"network": "sepolia"},
    )
    assert cr.status_code == 200
    conn_id = cr.json()["data"]["id"]
    addr = cr.json()["data"]["address"]

    er = sync_client.post(
        f"/api/v1/connections/{conn_id}/export-private-key",
        json={"confirm": True},
    )
    assert er.status_code == 200, er.text
    body = er.json()["data"]
    assert body["address"] == addr
    assert body["network"] == "sepolia"
    assert body["private_key"].startswith("0x")
    assert len(body["private_key"]) == 66
    # Cache-Control header set per 02-3 §5.13.5.
    assert "no-store" in er.headers.get("cache-control", "").lower()


def test_export_private_key_rejects_non_custodial(sync_client) -> None:  # type: ignore[no-untyped-def]
    from unittest.mock import AsyncMock, patch
    from uuid import uuid4
    from app.persistence.models.connections import ProviderConnection

    conn_id = str(uuid4())
    fake_conn = ProviderConnection(
        id=uuid4(),
        user_id=uuid4(),
        connection_type="wallbit",
        label="probe-bypass",
        auth_kind="api_key",
        credentials_encrypted=b"fake",
        credentials_kid="v1",
        status="healthy",
    )

    with patch(
        "app.persistence.repositories.connections.ConnectionRepository.get_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = fake_conn
        er = sync_client.post(
            f"/api/v1/connections/{conn_id}/export-private-key",
            json={"confirm": True},
        )

    assert er.status_code == 400, er.text
    assert er.json()["error"]["code"] == "NOT_EXPORTABLE"
