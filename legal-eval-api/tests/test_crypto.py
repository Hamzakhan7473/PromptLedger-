"""Tests for encryption."""

from legal_eval_api.crypto import decrypt_secret, encrypt_secret


def test_encrypt_roundtrip() -> None:
    plain = "sk-test-key-12345"
    assert decrypt_secret(encrypt_secret(plain)) == plain
