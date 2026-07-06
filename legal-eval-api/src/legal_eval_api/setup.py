"""Local self-host setup status (keys in legal-eval/.env)."""

from __future__ import annotations

import os

from legal_eval_api.config import LOCAL_KEY_VARS


def local_setup_status() -> dict[str, object]:
    keys = {name: bool(os.environ.get(name, "").strip()) for name in LOCAL_KEY_VARS}
    return {
        "mode": "self_hosted",
        "env_file": "legal-eval/.env",
        "keys": keys,
        "ready": any(keys.values()),
    }
