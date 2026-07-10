"""Firebase ID token verification via firebase-admin."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from legal_eval_api.config import FIREBASE_PROJECT_ID

_app_initialized = False


def firebase_auth_enabled() -> bool:
    return bool(FIREBASE_PROJECT_ID)


def _ensure_firebase_app() -> None:
    global _app_initialized
    if _app_initialized:
        return
    if not FIREBASE_PROJECT_ID:
        return
    import firebase_admin
    from firebase_admin import credentials

    if not firebase_admin._apps:
        # Cloud Run: Application Default Credentials from the metadata server.
        # Local dev: gcloud auth application-default login or GOOGLE_APPLICATION_CREDENTIALS.
        firebase_admin.initialize_app(
            credentials.ApplicationDefault(),
            {"projectId": FIREBASE_PROJECT_ID},
        )
    _app_initialized = True


def verify_firebase_id_token(token: str) -> dict[str, Any]:
    """Verify a Firebase ID token and return decoded claims."""
    if not firebase_auth_enabled():
        raise HTTPException(
            status_code=501,
            detail="Firebase authentication is not configured on this server.",
        )
    _ensure_firebase_app()
    from firebase_admin import auth

    try:
        return auth.verify_id_token(token, check_revoked=False)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token.") from exc


def default_org_name_from_claims(claims: dict[str, Any]) -> str:
    name = claims.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    email = claims.get("email")
    if isinstance(email, str) and "@" in email:
        local = email.split("@", 1)[0].replace(".", " ").replace("_", " ").strip()
        if local:
            return local.title()
    return "My Firm"
