"""Tests for enterprise features."""

from legal_eval_api.audit import get_audit_log, record_audit
from legal_eval_api.db import init_db
from legal_eval_api.enterprise import get_enterprise_settings, update_enterprise_settings
from legal_eval_api.orgs import register_org
from legal_eval_api.schemas import CreateOrgRequest, UpdateEnterpriseSettingsRequest


def test_audit_log() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Audit Co"))
    record_audit(org.org_id, "run.created", resource_type="run", resource_id="run123")
    events = get_audit_log(org.org_id)
    assert len(events) >= 1
    assert events[0]["action"] == "run.created"


def test_enterprise_settings_roundtrip() -> None:
    init_db()
    org = register_org(CreateOrgRequest(name="Enterprise Co"))
    updated = update_enterprise_settings(
        org.org_id,
        UpdateEnterpriseSettingsRequest(
            webhook_url="https://example.com/hook",
            webhook_secret="whsec_test",
            bedrock_region="us-west-2",
            sso_domain="firm.com",
        ),
    )
    assert updated.webhook_configured is True
    assert updated.webhook_secret_stored is True
    assert updated.bedrock_region == "us-west-2"
    assert updated.sso_domain == "firm.com"
    loaded = get_enterprise_settings(org.org_id)
    assert loaded.webhook_url == "https://example.com/hook"
