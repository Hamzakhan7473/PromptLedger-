"""Tests for run artifact endpoints."""

from fastapi.testclient import TestClient

from legal_eval_api.db import init_db
from legal_eval_api.main import app
from legal_eval_api.orgs import register_org
from legal_eval_api.schemas import CreateOrgRequest
from legal_eval_api.storage import run_meta_path, write_json
from legaleval.paths import run_root

EXISTING_RUN_ID = "20260625T183510Z_45633959"


def test_run_artifacts_bundle() -> None:
    if not run_root(EXISTING_RUN_ID).exists():
        return

    init_db()
    org = register_org(CreateOrgRequest(name="Artifacts Co"))
    write_json(
        run_meta_path(EXISTING_RUN_ID),
        {
            "run_id": EXISTING_RUN_ID,
            "org_id": org.org_id,
            "dataset_id": "test",
            "status": "completed",
            "models": ["openai"],
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )

    client = TestClient(app)
    response = client.get(
        f"/api/v1/runs/{EXISTING_RUN_ID}/artifacts",
        headers={"Authorization": f"Bearer {org.api_key}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == EXISTING_RUN_ID
    assert "manifest" in body
    assert "metrics" in body
    assert "examples" in body
    assert isinstance(body["raw_by_model"], dict)


def test_run_artifact_file_png() -> None:
    if not run_root(EXISTING_RUN_ID).exists():
        return

    init_db()
    org = register_org(CreateOrgRequest(name="Files Co"))
    write_json(
        run_meta_path(EXISTING_RUN_ID),
        {
            "run_id": EXISTING_RUN_ID,
            "org_id": org.org_id,
            "dataset_id": "test",
            "status": "completed",
            "models": ["openai"],
            "created_at": "2026-01-01T00:00:00+00:00",
        },
    )

    cal_dir = run_root(EXISTING_RUN_ID) / "calibration"
    png_files = list(cal_dir.glob("*.png")) if cal_dir.exists() else []
    if not png_files:
        return

    model_png = png_files[0].name
    client = TestClient(app)
    response = client.get(
        f"/api/v1/runs/{EXISTING_RUN_ID}/artifacts/files/calibration/{model_png}",
        headers={"Authorization": f"Bearer {org.api_key}"},
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/")
