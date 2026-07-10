"""Tests for Firebase ID token authentication."""

from __future__ import annotations

import secrets
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from legal_eval_api.auth import get_current_org, run_access
from legal_eval_api.db import get_org_by_api_key, get_org_by_firebase_uid, init_db
from legal_eval_api.main import app
from legal_eval_api.orgs import register_org
from legal_eval_api.schemas import CreateOrgRequest


@pytest.fixture
def api_client(tmp_path, monkeypatch) -> TestClient:
    data_root = tmp_path / "data"
    data_root.mkdir()
    import legal_eval_api.config as config_mod
    import legal_eval_api.db as db_mod

    monkeypatch.setattr(config_mod, "DATA_ROOT", data_root)
    monkeypatch.setattr(db_mod, "DATA_ROOT", data_root)
    monkeypatch.setattr(config_mod, "FIREBASE_PROJECT_ID", "legaleval")
    db_mod.init_db()
    return TestClient(app)


def test_org_api_key_auth_unchanged() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Legacy Co"))
    assert org.api_key.startswith("le_org_")
    assert get_org_by_api_key(org.api_key) is not None

    ctx = get_current_org(authorization=f"Bearer {org.api_key}")
    assert ctx.org_id == org.org_id
    assert ctx.via_firebase is False


def test_firebase_auto_org_creation(api_client: TestClient) -> None:
    claims = {"uid": "firebase_abc123", "email": "alice@firm.com"}

    with patch(
        "legal_eval_api.auth.verify_firebase_id_token",
        return_value=claims,
    ):
        response = api_client.get(
            "/api/v1/orgs/me",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice"
    assert body["onboarding_completed_at"] is None

    org = get_org_by_firebase_uid("firebase_abc123")
    assert org is not None
    assert org["org_id"] == body["org_id"]


def test_firebase_reuses_existing_org(api_client: TestClient) -> None:
    claims = {"uid": "firebase_repeat", "name": "Repeat User"}

    with patch(
        "legal_eval_api.auth.verify_firebase_id_token",
        return_value=claims,
    ):
        first = api_client.get(
            "/api/v1/orgs/me",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )
        second = api_client.get(
            "/api/v1/orgs/me",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["org_id"] == second.json()["org_id"]


def test_onboarding_complete(api_client: TestClient) -> None:
    claims = {"uid": f"firebase_onboard_{secrets.token_hex(4)}", "email": "onboard@example.com"}

    with patch(
        "legal_eval_api.auth.verify_firebase_id_token",
        return_value=claims,
    ):
        profile = api_client.get(
            "/api/v1/orgs/me",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )
        assert profile.json()["onboarding_completed_at"] is None

        status = api_client.get(
            "/api/v1/orgs/me/onboarding",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )
        assert status.json()["completed"] is False

        done = api_client.post(
            "/api/v1/orgs/me/onboarding/complete",
            headers={"Authorization": "Bearer fake.firebase.jwt"},
        )
        assert done.status_code == 200
        assert done.json()["completed"] is True
        assert done.json()["completed_at"]


def test_share_token_run_access_unaffected(api_client: TestClient, tmp_path, monkeypatch) -> None:
    import legal_eval_api.demo_seed as demo_mod

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "manifest.json").write_text('{"run_id":"demo"}', encoding="utf-8")
    results_root = tmp_path / "results"
    monkeypatch.setattr(demo_mod, "_BUNDLE_DIR", bundle)
    monkeypatch.setattr(demo_mod, "run_root", lambda run_id: results_root / run_id)

    from legal_eval_api.demo_seed import DEMO_RUN_ID, DEMO_SHARE_TOKEN, seed_public_demo_run

    seed_public_demo_run()

    ctx = run_access(
        run_id=DEMO_RUN_ID,
        authorization=None,
        token=DEMO_SHARE_TOKEN,
    )
    assert ctx.via_share is True
    assert ctx.org_id
