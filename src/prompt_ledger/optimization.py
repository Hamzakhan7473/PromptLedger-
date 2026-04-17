from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class OptimizationEvent:
    """Payload for an external Self-Improving Prompt Optimization service."""

    prompt_id: str
    version: str
    environment: str
    metrics: dict[str, Any]


def emit_optimization_event(event: OptimizationEvent) -> bool:
    """Best-effort POST to PROMPT_OPTIMIZATION_API_URL; never raises for CI."""

    url = os.environ.get("PROMPT_OPTIMIZATION_API_URL")
    if not url:
        return False
    body = json.dumps(asdict(event)).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
