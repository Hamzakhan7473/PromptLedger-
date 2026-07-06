"""Org enterprise settings (webhooks, Bedrock VPC, SSO domain)."""

from __future__ import annotations

from fastapi import HTTPException

from legal_eval_api.audit import record_audit
from legal_eval_api.crypto import decrypt_secret, encrypt_secret
from legal_eval_api.db import get_org_settings, upsert_org_settings
from legal_eval_api.schemas import EnterpriseSettings, UpdateEnterpriseSettingsRequest


def get_enterprise_settings(org_id: str) -> EnterpriseSettings:
    raw = get_org_settings(org_id)
    return EnterpriseSettings(
        org_id=org_id,
        webhook_url=raw.get("webhook_url"),
        webhook_configured=bool(raw.get("webhook_url")),
        webhook_secret_stored=bool(raw.get("webhook_secret_encrypted")),
        bedrock_region=raw.get("bedrock_region"),
        bedrock_endpoint_url=raw.get("bedrock_endpoint_url"),
        sso_domain=raw.get("sso_domain"),
        updated_at=raw.get("updated_at"),
    )


def update_enterprise_settings(
    org_id: str,
    request: UpdateEnterpriseSettingsRequest,
) -> EnterpriseSettings:
    if request.webhook_url is not None and request.webhook_url.strip():
        url = request.webhook_url.strip()
        if not url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="Webhook URL must be http(s).")
    else:
        url = request.webhook_url

    secret_encrypted = None
    clear_secret = False
    if request.webhook_secret is not None:
        if request.webhook_secret.strip():
            secret_encrypted = encrypt_secret(request.webhook_secret.strip())
        else:
            clear_secret = True

    upsert_org_settings(
        org_id,
        webhook_url=url,
        webhook_secret_encrypted=secret_encrypted,
        clear_webhook_secret=clear_secret,
        bedrock_region=request.bedrock_region,
        bedrock_endpoint_url=request.bedrock_endpoint_url,
        sso_domain=request.sso_domain,
    )
    record_audit(
        org_id,
        "settings.updated",
        resource_type="org",
        resource_id=org_id,
        metadata={
            "webhook_configured": bool(url),
            "bedrock_region": request.bedrock_region,
            "sso_domain": request.sso_domain,
        },
    )
    return get_enterprise_settings(org_id)


def get_webhook_config(org_id: str) -> tuple[str | None, str | None]:
    raw = get_org_settings(org_id)
    url = raw.get("webhook_url")
    encrypted = raw.get("webhook_secret_encrypted")
    if not url:
        return None, None
    secret = None
    if encrypted:
        try:
            secret = decrypt_secret(encrypted)
        except ValueError:
            secret = None
    return url, secret


def get_bedrock_overrides(org_id: str) -> dict[str, str]:
    raw = get_org_settings(org_id)
    overrides: dict[str, str] = {}
    if raw.get("bedrock_region"):
        overrides["region"] = raw["bedrock_region"]
    if raw.get("bedrock_endpoint_url"):
        overrides["endpoint_url"] = raw["bedrock_endpoint_url"]
    return overrides
