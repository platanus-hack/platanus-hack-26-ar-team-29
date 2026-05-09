"""Fernet credential vault — see 02-1 §11 #13."""

from cryptography.fernet import Fernet

from app.config import get_settings


def _cipher() -> Fernet:
    key = get_settings().fernet_key
    if not key:
        raise RuntimeError("FERNET_KEY is not configured")
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt(plaintext: bytes) -> bytes:
    return _cipher().encrypt(plaintext)


def decrypt(ciphertext: bytes) -> bytes:
    return _cipher().decrypt(ciphertext)
