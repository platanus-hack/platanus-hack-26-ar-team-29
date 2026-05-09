"""Round-trip + address-derivation tests for EthereumCustodialCredentials.

Pure unit tests — no DB, no FastAPI app. Sets a Fernet key in-process so
``app.persistence.crypto`` doesn't fail on import.
"""

from __future__ import annotations

import os

import pytest
from cryptography.fernet import Fernet


@pytest.fixture(autouse=True, scope="module")
def _fernet_env() -> None:
    # Inject a deterministic-ish key for the module. We use a freshly-generated
    # Fernet key to avoid hardcoding a "real-looking" one in source.
    os.environ["FERNET_KEY"] = Fernet.generate_key().decode()
    # Bust the lru_cache on get_settings so it re-reads the new env.
    from app.config import get_settings

    get_settings.cache_clear()


def test_credentials_round_trip() -> None:
    from app.providers.ethereum.auth import EthereumCustodialCredentials

    creds = EthereumCustodialCredentials(
        private_key="0x" + "11" * 32,
        network="sepolia",
    )
    blob = creds.to_blob()
    assert isinstance(blob, bytes)
    assert b"11" * 32 not in blob  # encrypted, not plaintext

    restored = EthereumCustodialCredentials.from_blob(blob)
    assert restored.private_key == creds.private_key
    assert restored.network == creds.network


def test_address_derivation_from_known_hex() -> None:
    """Static test vector: private key 0x111...1 -> known address."""
    from eth_account import Account

    from app.providers.ethereum.client import EthereumClient

    priv = "0x" + "11" * 32
    acct = Account.from_key(priv)
    expected = acct.address  # eth-account is the source of truth.

    derived = EthereumClient.derive_address(priv)
    assert derived == expected
    assert derived.startswith("0x")
    assert len(derived) == 42


def test_mnemonic_derivation_canonical_vector() -> None:
    """The canonical 'abandon ... about' mnemonic derives to a well-known address.

    BIP-44 m/44'/60'/0'/0/0 for that mnemonic is
    0x9858EfFD232B4033E47d90003D41EC34EcaEda94.
    """
    from eth_account import Account

    Account.enable_unaudited_hdwallet_features()
    mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    acct = Account.from_mnemonic(mnemonic)
    assert acct.address == "0x9858EfFD232B4033E47d90003D41EC34EcaEda94"


def test_normalize_private_key_input_hex_with_and_without_prefix() -> None:
    from app.services.connections import _normalize_private_key_input

    expected = "0x" + "11" * 32
    assert _normalize_private_key_input(expected) == expected
    assert _normalize_private_key_input("11" * 32) == expected


def test_normalize_private_key_input_mnemonic() -> None:
    from app.services.connections import _normalize_private_key_input

    mnemonic = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    out = _normalize_private_key_input(mnemonic)
    assert out.startswith("0x")
    assert len(out) == 66  # 0x + 64 hex chars


def test_normalize_private_key_input_rejects_garbage() -> None:
    from app.common.errors import APIError
    from app.services.connections import _normalize_private_key_input

    with pytest.raises(APIError) as excinfo:
        _normalize_private_key_input("not a key")
    assert excinfo.value.code == "VALIDATION_FAILED"


def test_normalize_private_key_input_rejects_empty() -> None:
    from app.common.errors import APIError
    from app.services.connections import _normalize_private_key_input

    with pytest.raises(APIError):
        _normalize_private_key_input("")
    with pytest.raises(APIError):
        _normalize_private_key_input("   ")


def test_normalize_private_key_input_rejects_bad_mnemonic_checksum() -> None:
    from app.common.errors import APIError
    from app.services.connections import _normalize_private_key_input

    # 12 words but the last is wrong → BIP-39 checksum failure.
    bad = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    with pytest.raises(APIError) as excinfo:
        _normalize_private_key_input(bad)
    assert excinfo.value.code == "VALIDATION_FAILED"
