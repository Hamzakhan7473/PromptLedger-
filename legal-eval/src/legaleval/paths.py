"""Canonical paths for timestamped eval runs."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return project_root() / "data"


def default_eval_set_path() -> Path:
    return data_dir() / "eval_set.jsonl"


def models_config_path() -> Path:
    return project_root() / "models.yaml"


def run_root(run_id: str) -> Path:
    return project_root() / "results" / run_id


def run_raw_dir(run_id: str) -> Path:
    return run_root(run_id) / "raw"


def run_metrics_path(run_id: str) -> Path:
    return run_root(run_id) / "metrics.json"


def run_manifest_path(run_id: str) -> Path:
    return run_root(run_id) / "manifest.json"


def run_report_path(run_id: str) -> Path:
    return run_root(run_id) / "REPORT.md"


def run_judge_dir(run_id: str) -> Path:
    return run_root(run_id) / "judge"


def run_judge_validation_path(run_id: str) -> Path:
    return run_judge_dir(run_id) / "validation.json"


def run_calibration_dir(run_id: str) -> Path:
    return run_root(run_id) / "calibration"


def run_calibration_ece_path(run_id: str) -> Path:
    return run_calibration_dir(run_id) / "ece.json"


def run_errors_dir(run_id: str) -> Path:
    return run_root(run_id) / "errors"


def run_errors_summary_path(run_id: str) -> Path:
    return run_root(run_id) / "errors_summary.json"


def latest_run_link() -> Path:
    return project_root() / "results" / "latest"
