"""Ethereum custodial credential dataclass + encrypted-blob helpers.

Mirrors `app.providers.wallbit.auth.WallbitCredentials`. The blob stores the
raw hex private key + the network slug; the address is derived on demand and
is also persisted in `connection_metadata` for fast reads (without decrypting).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.persistence import crypto


@dataclass(slots=True)
class EthereumCustodialCredentials:
    private_key: str  # 0x-prefixed 32-byte hex
    network: str

    def to_blob(self) -> bytes:
        payload = json.dumps({"private_key": self.private_key, "network": self.network}).encode(
            "utf-8"
        )
        return crypto.encrypt(payload)

    @classmethod
    def from_blob(cls, blob: bytes) -> EthereumCustodialCredentials:
        decoded = json.loads(crypto.decrypt(blob).decode("utf-8"))
        return cls(private_key=decoded["private_key"], network=decoded["network"])
