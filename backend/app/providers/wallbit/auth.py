"""Wallbit credential dataclass + encrypted-blob helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.persistence import crypto


@dataclass(slots=True)
class WallbitCredentials:
    api_key: str

    def to_blob(self) -> bytes:
        payload = json.dumps({"api_key": self.api_key}).encode("utf-8")
        return crypto.encrypt(payload)

    @classmethod
    def from_blob(cls, blob: bytes) -> WallbitCredentials:
        decoded = json.loads(crypto.decrypt(blob).decode("utf-8"))
        return cls(api_key=decoded["api_key"])
