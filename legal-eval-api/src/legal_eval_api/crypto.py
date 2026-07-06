"""Encrypt provider API keys at rest."""

from __future__ import annotations

import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from legal_eval_api.config import DATA_ROOT

_MASTER_KEY_PATH = DATA_ROOT / ".master_key"


def _load_or_create_master_key() -> bytes:
    env_key = os.environ.get("LEGAL_EVAL_MASTER_KEY", "").strip()
    if env_key:
        return env_key.encode("utf-8")

    if _MASTER_KEY_PATH.exists():
        return _MASTER_KEY_PATH.read_bytes().strip()

    key = Fernet.generate_key()
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    _MASTER_KEY_PATH.write_bytes(key)
    return key


def encrypt_secret(plaintext: str) -> str:
    fernet = Fernet(_load_or_create_master_key())
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    fernet = Fernet(_load_or_create_master_key())
    try:
        return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Failed to decrypt secret (wrong master key?)") from exc
