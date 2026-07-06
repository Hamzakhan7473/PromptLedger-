"""Copy harness output into legal-eval-ui/public/results/.

NOTE: As of the runtime API artifacts endpoints (/api/v1/runs/{id}/artifacts), the UI
loads run data directly from the API and no longer depends on this copy for correctness.
This module remains for backward compatibility during migration and can be removed once
all deployments serve artifacts via the API only.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from legaleval.paths import project_root, run_root

from legal_eval_api.config import LEGAL_EVAL_UI_ROOT


def sync_run_to_ui(run_id: str) -> Path:
    src = run_root(run_id)
    if not src.exists():
        raise FileNotFoundError(f"Run output not found: {src}")

    dest = LEGAL_EVAL_UI_ROOT / "public" / "results" / run_id
    eval_set_src = _resolve_eval_set_path(run_id)

    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    shutil.copy2(eval_set_src, dest / "eval_set.jsonl")
    return dest


def _resolve_eval_set_path(run_id: str) -> Path:
    from legal_eval_api.storage import read_json, run_meta_path

    meta_file = run_meta_path(run_id)
    if meta_file.exists():
        meta = read_json(meta_file)
        dataset_id = meta.get("dataset_id")
        if dataset_id:
            from legal_eval_api.storage import dataset_eval_path

            path = dataset_eval_path(dataset_id)
            if path.exists():
                return path

    default = project_root() / "data" / "eval_set.jsonl"
    if default.exists():
        return default
    raise FileNotFoundError(f"No eval_set.jsonl for run {run_id}")
