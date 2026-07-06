"""Background eval jobs."""

from __future__ import annotations

import os
import threading
import traceback
from typing import Any

from fastapi import HTTPException
from legaleval.pipeline import generate_run_id, run_pipeline

from legal_eval_api.audit import record_audit
from legal_eval_api.datasets import get_dataset, get_dataset_eval_path, validate_models
from legal_eval_api.enterprise import get_bedrock_overrides
from legal_eval_api.models_builder import build_models_config
from legal_eval_api.orgs import ensure_models_enabled, resolve_api_keys
from legal_eval_api.schemas import CreateRunRequest, RunDetail, RunSummary
from legal_eval_api.sharing import assert_run_access
from legal_eval_api.storage import (
    ensure_dirs,
    job_models_config_path,
    read_json,
    run_meta_path,
    utc_now,
    write_json,
)
from legal_eval_api.sync_ui import sync_run_to_ui
from legal_eval_api.webhooks import dispatch_webhook

_lock = threading.Lock()
_active: set[str] = set()


def create_run(org_id: str, request: CreateRunRequest) -> RunSummary:
    ensure_dirs()
    get_dataset(request.dataset_id, org_id)
    models = validate_models(request.models)
    ensure_models_enabled(org_id, models)
    api_keys = resolve_api_keys(org_id, request.api_keys)
    _validate_required_keys(models, api_keys, request.mode)

    run_id = generate_run_id()
    created_at = utc_now()

    meta = {
        "run_id": run_id,
        "org_id": org_id,
        "dataset_id": request.dataset_id,
        "name": request.name,
        "mode": request.mode,
        "status": "queued",
        "models": models,
        "created_at": created_at.isoformat(),
        "started_at": None,
        "finished_at": None,
        "error": None,
        "skip_judge_validate": request.skip_judge_validate,
        "steps_completed": [],
        "judge_kappa": None,
        "result": None,
        "share_token": None,
    }
    write_json(run_meta_path(run_id), meta)

    record_audit(
        org_id,
        "run.created",
        resource_type="run",
        resource_id=run_id,
        metadata={"models": models, "mode": request.mode, "dataset_id": request.dataset_id},
    )

    thread = threading.Thread(
        target=_execute_run,
        args=(run_id, org_id, request, api_keys),
        daemon=True,
        name=f"eval-{run_id}",
    )
    thread.start()
    return _to_summary(meta)


def _validate_required_keys(
    models: list[str],
    api_keys: dict[str, str],
    mode: str = "eval",
) -> None:
    from legal_eval_api.config import MODEL_KEY_REQUIREMENTS
    from legal_eval_api.datasets import model_catalog

    catalog = {m.id: m for m in model_catalog()}
    missing: list[str] = []
    unsupported: list[str] = []
    for model_id in models:
        info = catalog.get(model_id)
        if not info:
            continue
        if mode == "agent" and not info.agent_supported:
            unsupported.append(model_id)
        env_key = MODEL_KEY_REQUIREMENTS.get(model_id)
        if env_key and not api_keys.get(env_key, "").strip():
            missing.append(env_key)
    if unsupported:
        raise HTTPException(
            status_code=400,
            detail=f"Agent mode unsupported for model(s): {', '.join(unsupported)}",
        )
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Model keys not configured: {', '.join(sorted(set(missing)))}. "
            "Local: add to legal-eval/.env and restart `make api`. "
            "Web: save keys in Settings → Model API keys.",
        )


def _execute_run(
    run_id: str,
    org_id: str,
    request: CreateRunRequest,
    api_keys: dict[str, str],
) -> None:
    with _lock:
        if run_id in _active:
            return
        _active.add(run_id)

    meta = read_json(run_meta_path(run_id))
    meta["status"] = "running"
    meta["started_at"] = utc_now().isoformat()
    write_json(run_meta_path(run_id), meta)

    env_backup: dict[str, str | None] = {}
    try:
        eval_set_path = get_dataset_eval_path(request.dataset_id, org_id)
        dataset = get_dataset(request.dataset_id, org_id)
        models_config = build_models_config(
            request.models,
            job_models_config_path(run_id),
            bedrock_overrides=get_bedrock_overrides(org_id),
        )

        for key, value in api_keys.items():
            if value.strip():
                env_backup[key] = os.environ.get(key)
                os.environ[key] = value.strip()

        result = run_pipeline(
            run_id=run_id,
            eval_set_path=eval_set_path,
            models=",".join(request.models),
            mode=request.mode,
            rebuild_eval_set=False,
            skip_judge_validate=request.skip_judge_validate,
            models_config=models_config,
            dataset_name=dataset.name,
        )
        sync_run_to_ui(run_id)

        meta = read_json(run_meta_path(run_id))
        meta["status"] = "completed"
        meta["finished_at"] = utc_now().isoformat()
        meta["steps_completed"] = result.get("steps_completed", [])
        meta["judge_kappa"] = result.get("judge_kappa")
        meta["result"] = {
            "run_root": result.get("run_root"),
            "report_path": result.get("report_path"),
            "manifest_path": result.get("manifest_path"),
        }
        meta["error"] = None
        write_json(run_meta_path(run_id), meta)
        record_audit(
            org_id,
            "run.completed",
            resource_type="run",
            resource_id=run_id,
            metadata={"judge_kappa": meta.get("judge_kappa"), "mode": request.mode},
        )
        dispatch_webhook(
            org_id,
            "run.completed",
            {
                "run_id": run_id,
                "mode": request.mode,
                "models": request.models,
                "judge_kappa": meta.get("judge_kappa"),
                "ui_summary_url": f"/runs/{run_id}/summary",
            },
        )
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        _mark_failed(run_id, f"Pipeline aborted (exit {code})", org_id, request)
    except Exception as exc:
        _mark_failed(run_id, str(exc) or exc.__class__.__name__, org_id, request)
        traceback.print_exc()
    finally:
        for key, previous in env_backup.items():
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous
        with _lock:
            _active.discard(run_id)


def _mark_failed(
    run_id: str,
    message: str,
    org_id: str | None = None,
    request: CreateRunRequest | None = None,
) -> None:
    meta = read_json(run_meta_path(run_id))
    meta["status"] = "failed"
    meta["finished_at"] = utc_now().isoformat()
    meta["error"] = message
    write_json(run_meta_path(run_id), meta)
    resolved_org = org_id or meta.get("org_id")
    if resolved_org:
        record_audit(
            resolved_org,
            "run.failed",
            resource_type="run",
            resource_id=run_id,
            metadata={"error": message},
        )
        dispatch_webhook(
            resolved_org,
            "run.failed",
            {
                "run_id": run_id,
                "mode": meta.get("mode", "eval"),
                "error": message,
            },
        )


def list_runs(org_id: str) -> list[RunSummary]:
    ensure_dirs()
    runs: list[RunSummary] = []
    for path in sorted(run_meta_path("").parent.glob("*.json")):
        meta = read_json(path)
        if meta.get("org_id") == org_id:
            runs.append(_to_summary(meta))
    runs.sort(key=lambda item: item.created_at, reverse=True)
    return runs


def get_run(run_id: str, org_id: str) -> RunDetail:
    meta = assert_run_access(org_id, run_id)
    summary = _to_summary(meta)
    return RunDetail(
        **summary.model_dump(),
        steps_completed=meta.get("steps_completed") or [],
        judge_kappa=meta.get("judge_kappa"),
        result=meta.get("result"),
    )


def _to_summary(meta: dict[str, Any]) -> RunSummary:
    run_id = meta["run_id"]
    status = meta["status"]
    ui_url = f"/runs/{run_id}/summary" if status == "completed" else None
    share_url = None
    if meta.get("share_token"):
        share_url = f"/runs/{run_id}/summary?token={meta['share_token']}"
    return RunSummary(
        run_id=run_id,
        org_id=meta["org_id"],
        dataset_id=meta["dataset_id"],
        name=meta.get("name"),
        mode=meta.get("mode", "eval"),
        status=status,
        models=meta.get("models") or [],
        created_at=meta["created_at"],
        started_at=meta.get("started_at"),
        finished_at=meta.get("finished_at"),
        error=meta.get("error"),
        report_url=f"/api/v1/runs/{run_id}/report" if status == "completed" else None,
        ui_summary_url=ui_url,
        share_url=share_url,
    )
