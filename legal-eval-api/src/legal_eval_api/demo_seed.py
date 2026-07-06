"""Seed a public read-only demo run for anonymous visitors (share-token access)."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from legaleval.paths import run_root

from legal_eval_api.db import (
    connect,
    hash_api_key,
    upsert_share_link,
    utc_now_iso,
)
from legal_eval_api.storage import run_meta_path, write_json

DEMO_RUN_ID = os.environ.get("LEGAL_EVAL_DEMO_RUN_ID", "demo")
DEMO_SHARE_TOKEN = os.environ.get("LEGAL_EVAL_DEMO_SHARE_TOKEN", "le_demo_public_v1")
DEMO_ORG_ID = os.environ.get("LEGAL_EVAL_DEMO_ORG_ID", "00000000demo")
DEMO_ORG_NAME = "Public demo"

_BUNDLE_DIR = Path(__file__).resolve().parents[2] / "demo_run" / "demo"


def _ensure_demo_org() -> None:
    with connect() as conn:
        row = conn.execute(
            "SELECT org_id FROM orgs WHERE org_id = ?",
            (DEMO_ORG_ID,),
        ).fetchone()
        if row:
            return
        conn.execute(
            """
            INSERT INTO orgs (org_id, name, api_key_hash, enabled_models, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                DEMO_ORG_ID,
                DEMO_ORG_NAME,
                hash_api_key(f"demo-no-login-{DEMO_ORG_ID}"),
                json.dumps(["openai", "google", "bedrock_claude"]),
                utc_now_iso(),
            ),
        )


def _install_demo_artifacts() -> None:
    dest = run_root(DEMO_RUN_ID)
    if dest.exists():
        return
    if not _BUNDLE_DIR.is_dir():
        return
    shutil.copytree(_BUNDLE_DIR, dest)


def _ensure_demo_run_meta() -> None:
    meta_path = run_meta_path(DEMO_RUN_ID)
    if meta_path.exists():
        return
    write_json(
        meta_path,
        {
            "run_id": DEMO_RUN_ID,
            "org_id": DEMO_ORG_ID,
            "dataset_id": None,
            "name": "Public demo run",
            "mode": "eval",
            "status": "completed",
            "models": ["model-a", "model-b"],
            "created_at": utc_now_iso(),
            "started_at": utc_now_iso(),
            "finished_at": utc_now_iso(),
            "error": None,
            "skip_judge_validate": False,
            "steps_completed": ["data", "models", "metrics", "report"],
            "judge_kappa": 0.75,
            "result": {"run_id": DEMO_RUN_ID},
            "share_token": DEMO_SHARE_TOKEN,
        },
    )


def seed_public_demo_run() -> None:
    """Install bundled demo artifacts and register a stable share token."""
    _install_demo_artifacts()
    if not run_root(DEMO_RUN_ID).exists():
        return
    _ensure_demo_org()
    _ensure_demo_run_meta()
    upsert_share_link(DEMO_RUN_ID, DEMO_ORG_ID, DEMO_SHARE_TOKEN)


def public_demo_link() -> dict[str, str] | None:
    if not run_root(DEMO_RUN_ID).exists():
        return None
    return {
        "run_id": DEMO_RUN_ID,
        "token": DEMO_SHARE_TOKEN,
        "summary_path": f"/runs/{DEMO_RUN_ID}/summary?token={DEMO_SHARE_TOKEN}",
        "artifacts_api": f"/api/v1/runs/{DEMO_RUN_ID}/artifacts?token={DEMO_SHARE_TOKEN}",
    }
