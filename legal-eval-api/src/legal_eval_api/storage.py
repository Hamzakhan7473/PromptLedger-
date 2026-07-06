"""Filesystem persistence for datasets and run metadata."""

from __future__ import annotations

import json
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path

from legal_eval_api.config import DATASETS_DIR, DOCUMENT_STAGING_DIR, JOB_CONFIGS_DIR, RUNS_META_DIR


def ensure_dirs() -> None:
    for path in (DATASETS_DIR, RUNS_META_DIR, JOB_CONFIGS_DIR, DOCUMENT_STAGING_DIR):
        path.mkdir(parents=True, exist_ok=True)


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def dataset_dir(dataset_id: str) -> Path:
    return DATASETS_DIR / dataset_id


def dataset_meta_path(dataset_id: str) -> Path:
    return dataset_dir(dataset_id) / "meta.json"


def dataset_eval_path(dataset_id: str) -> Path:
    return dataset_dir(dataset_id) / "eval_set.jsonl"


def run_meta_path(run_id: str) -> Path:
    return RUNS_META_DIR / f"{run_id}.json"


def job_models_config_path(run_id: str) -> Path:
    return JOB_CONFIGS_DIR / f"{run_id}_models.yaml"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, default=str)
        handle.write("\n")


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def utc_now() -> datetime:
    return datetime.now(UTC)


def save_uploaded_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
