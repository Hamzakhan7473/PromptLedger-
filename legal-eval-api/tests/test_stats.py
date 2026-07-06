"""Tests for org stats endpoint."""

from fastapi.testclient import TestClient

from legal_eval_api.db import init_db
from legal_eval_api.main import app
from legal_eval_api.orgs import register_org
from legal_eval_api.schemas import CreateOrgRequest


def test_org_stats_endpoint() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Stats Co"))
    client = TestClient(app)
    response = client.get(
        "/api/v1/orgs/me/stats",
        headers={"Authorization": f"Bearer {org.api_key}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["org_id"] == org.org_id
    assert body["total_runs"] == 0
    assert body["completed_runs"] == 0
