"""Read eval run artifacts from harness output (local filesystem today; S3 later)."""

from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from legaleval.paths import project_root, run_root

from legal_eval_api.storage import dataset_eval_path, read_json, run_meta_path

# Relative paths under run_root allowed for GET .../artifacts/files/{path}
ALLOWED_FILE_PREFIXES = (
    "calibration/",
    "errors/",
    "judge/",
    "raw/",
)
ALLOWED_ROOT_FILES = frozenset(
    {
        "manifest.json",
        "metrics.json",
        "errors_summary.json",
        "eval_set.jsonl",
        "REPORT.md",
    }
)

DEFAULT_JUDGE_VALIDATION: dict[str, Any] = {
    "sample_size": 0,
    "seed": 0,
    "reference_rule": "",
    "agreement": {
        "n_sampled": 0,
        "n_scored": 0,
        "n_errors": 0,
        "accuracy": None,
        "cohens_kappa": None,
        "min_kappa_required": 0.6,
        "passes_threshold": False,
    },
    "cases": [],
}

DEFAULT_CALIBRATION: dict[str, Any] = {
    "run_id": "",
    "eval_set": "",
    "models": {},
}


def resolve_run_dir(run_id: str) -> Path:
    root = run_root(run_id)
    if not root.exists():
        raise HTTPException(status_code=404, detail=f"Run artifacts not found: {run_id}")
    return root


def _read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return _read_json(path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            rows.append(json.loads(stripped))
    return rows


def resolve_eval_set_path(run_id: str) -> Path:
    """Same resolution order as sync_ui._resolve_eval_set_path."""
    in_run = run_root(run_id) / "eval_set.jsonl"
    if in_run.exists():
        return in_run

    meta_file = run_meta_path(run_id)
    if meta_file.exists():
        meta = read_json(meta_file)
        dataset_id = meta.get("dataset_id")
        if dataset_id:
            path = dataset_eval_path(dataset_id)
            if path.exists():
                return path

    default = project_root() / "data" / "eval_set.jsonl"
    if default.exists():
        return default

    raise HTTPException(
        status_code=404,
        detail=f"eval_set.jsonl not found for run {run_id}",
    )


def load_judge_decisions(judge_dir: Path) -> dict[str, list[dict[str, Any]]]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    if not judge_dir.exists():
        return by_model
    for file in judge_dir.iterdir():
        if file.suffix == ".jsonl" and file.name.endswith("_decisions.jsonl"):
            model = file.name.replace("_decisions.jsonl", "")
            by_model[model] = _read_jsonl(file)
    return by_model


def load_raw_by_model(raw_dir: Path) -> dict[str, list[dict[str, Any]]]:
    by_model: dict[str, list[dict[str, Any]]] = {}
    if not raw_dir.exists():
        return by_model
    for file in raw_dir.iterdir():
        if file.suffix == ".jsonl":
            by_model[file.stem] = _read_jsonl(file)
    return by_model


def load_run_artifacts_bundle(run_id: str) -> dict[str, Any]:
    """Aggregate artifact JSON used by the UI (storage backend swappable here)."""
    base = resolve_run_dir(run_id)

    manifest = _read_json(base / "manifest.json")
    metrics = _read_json(base / "metrics.json")
    errors_summary = _read_json(base / "errors_summary.json")

    judge_validation = _read_json_if_exists(base / "judge" / "validation.json")
    if judge_validation is None:
        judge_validation = {**DEFAULT_JUDGE_VALIDATION}

    calibration = _read_json_if_exists(base / "calibration" / "ece.json")
    if calibration is None:
        calibration = {**DEFAULT_CALIBRATION, "run_id": run_id}

    eval_set_path = resolve_eval_set_path(run_id)
    examples = _read_jsonl(eval_set_path)
    raw_by_model = load_raw_by_model(base / "raw")
    judge_by_model = load_judge_decisions(base / "judge")

    return {
        "run_id": run_id,
        "manifest": manifest,
        "metrics": metrics,
        "errors_summary": errors_summary,
        "judge_validation": judge_validation,
        "calibration": calibration,
        "examples": examples,
        "raw_by_model": raw_by_model,
        "judge_by_model": judge_by_model,
        "models": sorted(raw_by_model.keys()),
    }


def resolve_artifact_file(run_id: str, relative_path: str) -> tuple[Path, str]:
    """Return (absolute path, media type) for a file under the run directory."""
    normalized = relative_path.strip().lstrip("/")
    if not normalized or ".." in normalized.split("/"):
        raise HTTPException(status_code=400, detail="Invalid artifact path.")

    allowed = normalized in ALLOWED_ROOT_FILES or normalized.startswith(ALLOWED_FILE_PREFIXES)
    if not allowed:
        raise HTTPException(status_code=400, detail=f"Artifact path not allowed: {normalized}")

    base = resolve_run_dir(run_id)
    target = (base / normalized).resolve()
    if not str(target).startswith(str(base.resolve())):
        raise HTTPException(status_code=400, detail="Invalid artifact path.")

    if not target.exists() or not target.is_file():
        raise HTTPException(status_code=404, detail=f"Artifact file not found: {normalized}")

    media_type, _ = mimetypes.guess_type(target.name)
    return target, media_type or "application/octet-stream"
