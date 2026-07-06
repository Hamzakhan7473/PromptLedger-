"""Tests for organizations."""

from legal_eval_api.db import get_org_by_api_key, init_db
from legal_eval_api.orgs import get_profile, register_org, resolve_api_keys, update_secrets
from legal_eval_api.schemas import CreateOrgRequest, UpdateOrgSecretsRequest


def test_register_and_auth() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Test Firm"))
    assert org.org_id
    assert org.api_key.startswith("le_org_")
    profile = get_profile(org.org_id)
    assert profile.name == "Test Firm"
    assert get_org_by_api_key(org.api_key) is not None


def test_store_and_resolve_secrets() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Keys Co"))
    update_secrets(
        org.org_id,
        UpdateOrgSecretsRequest(secrets={"OPENAI_API_KEY": "sk-test"}),
    )
    resolved = resolve_api_keys(org.org_id, {})
    assert resolved["OPENAI_API_KEY"] == "sk-test"
    resolved2 = resolve_api_keys(org.org_id, {"OPENAI_API_KEY": "sk-override"})
    assert resolved2["OPENAI_API_KEY"] == "sk-override"


def test_local_env_keys(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-local")
    init_db()
    org = register_org(CreateOrgRequest(name="Local Co"))
    resolved = resolve_api_keys(org.org_id, {})
    assert resolved["OPENAI_API_KEY"] == "sk-local"
