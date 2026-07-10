"""API configuration."""

from __future__ import annotations

import os
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = API_ROOT.parent
LEGAL_EVAL_ROOT = REPO_ROOT / "legal-eval"
LEGAL_EVAL_UI_ROOT = REPO_ROOT / "legal-eval-ui"
MODELS_TEMPLATE = LEGAL_EVAL_ROOT / "models.yaml.example"

DATA_ROOT = Path(os.environ.get("LEGAL_EVAL_API_DATA", API_ROOT / "data"))
DATASETS_DIR = DATA_ROOT / "datasets"
RUNS_META_DIR = DATA_ROOT / "runs"
JOB_CONFIGS_DIR = DATA_ROOT / "job_configs"
DOCUMENT_STAGING_DIR = DATA_ROOT / "document_staging"

API_HOST = os.environ.get("LEGAL_EVAL_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("LEGAL_EVAL_API_PORT", "8787"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "LEGAL_EVAL_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if origin.strip()
]

AVAILABLE_MODELS = ("openai", "google", "bedrock_claude")

# Keys loaded from legal-eval/.env when running `make api` locally.
LOCAL_KEY_VARS = ("OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY")

# Internal: which env key each model needs (None = AWS credential chain for Bedrock).
MODEL_KEY_REQUIREMENTS: dict[str, str | None] = {
    "openai": "OPENAI_API_KEY",
    "google": "GOOGLE_API_KEY",
    "bedrock_claude": None,
}

# Firebase project ID (same GCP project as Cloud Run, e.g. legaleval)
FIREBASE_PROJECT_ID = os.environ.get(
    "FIREBASE_PROJECT_ID",
    os.environ.get("GCP_PROJECT_ID", "legaleval"),
).strip()
