"""Organization profiles and local model key resolution."""

from __future__ import annotations

import os

from fastapi import HTTPException

from legal_eval_api.audit import record_audit
from legal_eval_api.config import AVAILABLE_MODELS, LOCAL_KEY_VARS
from legal_eval_api.crypto import decrypt_secret, encrypt_secret
from legal_eval_api.db import (
    create_org,
    delete_secret,
    get_enabled_models,
    get_org,
    get_secrets,
    list_org_ids,
    list_secret_keys,
    set_enabled_models,
    upsert_secret,
)
from legal_eval_api.schemas import (
    CreateOrgRequest,
    CreateOrgResponse,
    OrgProfile,
    OrgSecretsStatus,
    UpdateOrgModelsRequest,
    UpdateOrgSecretsRequest,
)


def register_org(request: CreateOrgRequest) -> CreateOrgResponse:
    org_id, api_key = create_org(request.name)
    return CreateOrgResponse(
        org_id=org_id,
        name=request.name,
        api_key=api_key,
        enabled_models=["openai", "google", "bedrock_claude"],
    )


def get_profile(org_id: str) -> OrgProfile:
    org = get_org(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return OrgProfile(
        org_id=org["org_id"],
        name=org["name"],
        enabled_models=get_enabled_models(org_id),
        stored_secret_keys=list_secret_keys(org_id),
        created_at=org["created_at"],
    )


def update_models(org_id: str, request: UpdateOrgModelsRequest) -> OrgProfile:
    unknown = [m for m in request.enabled_models if m not in AVAILABLE_MODELS]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model(s): {', '.join(unknown)}",
        )
    if not request.enabled_models:
        raise HTTPException(status_code=400, detail="Enable at least one model.")
    set_enabled_models(org_id, request.enabled_models)
    record_audit(
        org_id,
        "models.updated",
        resource_type="org",
        resource_id=org_id,
        metadata={"enabled_models": request.enabled_models},
    )
    return get_profile(org_id)


def update_secrets(org_id: str, request: UpdateOrgSecretsRequest) -> OrgSecretsStatus:
    allowed = {"OPENAI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"}
    for env_key, value in request.secrets.items():
        if env_key not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported secret: {env_key}")
        if value.strip():
            upsert_secret(org_id, env_key, encrypt_secret(value.strip()))
        else:
            delete_secret(org_id, env_key)
    record_audit(org_id, "secrets.updated", resource_type="org", resource_id=org_id)
    return get_secrets_status(org_id)


def get_secrets_status(org_id: str) -> OrgSecretsStatus:
    return OrgSecretsStatus(
        stored_keys=list_secret_keys(org_id),
        openai=bool(_has_key(org_id, "OPENAI_API_KEY")),
        google=bool(_has_key(org_id, "GOOGLE_API_KEY")),
        anthropic=bool(_has_key(org_id, "ANTHROPIC_API_KEY")),
    )


def _has_key(org_id: str, env_key: str) -> bool:
    return env_key in list_secret_keys(org_id)


def resolve_api_keys(org_id: str, overrides: dict[str, str]) -> dict[str, str]:
    """Merge keys from local legal-eval/.env, optional org overrides, per-run overrides."""
    resolved: dict[str, str] = {}
    for env_key in LOCAL_KEY_VARS:
        local_val = os.environ.get(env_key, "").strip()
        if local_val:
            resolved[env_key] = local_val
    for env_key, encrypted in get_secrets(org_id).items():
        try:
            resolved[env_key] = decrypt_secret(encrypted)
        except ValueError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
    for env_key, value in overrides.items():
        if value.strip():
            resolved[env_key] = value.strip()
    return resolved


def local_key_available(env_key: str, resolved: dict[str, str]) -> bool:
    return bool(resolved.get(env_key, "").strip())


def ensure_models_enabled(org_id: str, models: list[str]) -> None:
    enabled = set(get_enabled_models(org_id))
    disabled = [m for m in models if m not in enabled]
    if disabled:
        raise HTTPException(
            status_code=400,
            detail=f"Model(s) not enabled for org: {', '.join(disabled)}. "
            "Update org settings at PUT /api/v1/orgs/me/models",
        )


def migrate_legacy_resources(default_org_id: str) -> None:
    """Attach pre-Phase-2 datasets/runs (no org_id) to the default org."""
    from legal_eval_api.storage import DATASETS_DIR, RUNS_META_DIR, read_json, write_json

    if DATASETS_DIR.exists():
        for path in DATASETS_DIR.iterdir():
            if not path.is_dir():
                continue
            meta_file = path / "meta.json"
            if meta_file.exists():
                meta = read_json(meta_file)
                if "org_id" not in meta:
                    meta["org_id"] = default_org_id
                    write_json(meta_file, meta)

    if RUNS_META_DIR.exists():
        for meta_file in RUNS_META_DIR.glob("*.json"):
            meta = read_json(meta_file)
            if "org_id" not in meta:
                meta["org_id"] = default_org_id
                write_json(meta_file, meta)


def ensure_default_org() -> str | None:
    """Create a default org when DB is empty; migrate legacy files."""
    ids = list_org_ids()
    if ids:
        migrate_legacy_resources(ids[0])
        return ids[0]

    org_id, api_key = create_org("Default")
    migrate_legacy_resources(org_id)
    print(  # noqa: T201
        f"\n[legal-eval-api] Created default organization.\n"
        f"  org_id:  {org_id}\n"
        f"  api_key: {api_key}\n"
        f"  Save this key in the UI Settings page.\n"
    )
    return org_id
