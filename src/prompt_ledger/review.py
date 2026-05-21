from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def emit_review_webhook(payload: dict[str, Any]) -> bool:
    """POST human-review payload to PROMPT_LEDGER_REVIEW_WEBHOOK_URL (best-effort)."""

    url = os.environ.get("PROMPT_LEDGER_REVIEW_WEBHOOK_URL")
    if not url:
        return False
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
