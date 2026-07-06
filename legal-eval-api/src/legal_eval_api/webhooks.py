"""Webhook delivery on run lifecycle events."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from legal_eval_api.enterprise import get_webhook_config

logger = logging.getLogger(__name__)


def _sign_payload(secret: str, body: bytes) -> str:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def dispatch_webhook(org_id: str, event: str, payload: dict[str, Any]) -> None:
    url, secret = get_webhook_config(org_id)
    if not url:
        return

    envelope = {"event": event, "org_id": org_id, "data": payload}
    body = json.dumps(envelope, separators=(",", ":"), default=str).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "legal-eval-api/0.4"}
    if secret:
        headers["X-Legal-Eval-Signature"] = _sign_payload(secret, body)

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, content=body, headers=headers)
            response.raise_for_status()
    except Exception as exc:  # noqa: BLE001 — webhook must not fail the run
        logger.warning("Webhook delivery failed for org %s: %s", org_id, exc)
