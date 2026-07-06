"""Read-only share links for completed runs."""

from __future__ import annotations

from fastapi import HTTPException

from legal_eval_api.audit import record_audit
from legal_eval_api.db import generate_share_token, upsert_share_link
from legal_eval_api.schemas import ShareLinkResponse
from legal_eval_api.storage import read_json, run_meta_path


def create_share_link(org_id: str, run_id: str) -> ShareLinkResponse:
    meta = _get_run_meta(run_id)
    if meta.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    if meta.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Run must be completed before sharing.")

    token = generate_share_token()
    upsert_share_link(run_id, org_id, token)
    record_audit(
        org_id,
        "share.created",
        resource_type="run",
        resource_id=run_id,
    )
    return ShareLinkResponse(
        run_id=run_id,
        token=token,
        share_url=f"/runs/{run_id}/summary?token={token}",
        api_url=f"/api/v1/runs/{run_id}?token={token}",
    )


def assert_run_access(org_id: str, run_id: str) -> dict:
    meta = _get_run_meta(run_id)
    if meta.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return meta


def _get_run_meta(run_id: str) -> dict:
    path = run_meta_path(run_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Run not found: {run_id}")
    return read_json(path)
