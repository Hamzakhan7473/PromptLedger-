"""Organization authentication dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query

from legal_eval_api.db import get_org, get_org_by_api_key, get_share_org
from legal_eval_api.firebase_auth import verify_firebase_id_token
from legal_eval_api.orgs import ensure_org_for_firebase_user


@dataclass(frozen=True)
class AuthContext:
    org_id: str
    org_name: str
    via_share: bool = False
    via_firebase: bool = False
    firebase_uid: str | None = None


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def _auth_from_org_api_key(token: str) -> AuthContext:
    org = get_org_by_api_key(token)
    if not org:
        raise HTTPException(status_code=401, detail="Invalid organization API key.")
    return AuthContext(org_id=org["org_id"], org_name=org["name"])


def _auth_from_firebase_token(token: str) -> AuthContext:
    claims = verify_firebase_id_token(token)
    firebase_uid = claims.get("uid") or claims.get("sub")
    if not isinstance(firebase_uid, str) or not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token.")
    org_id, org_name = ensure_org_for_firebase_user(firebase_uid, claims)
    return AuthContext(
        org_id=org_id,
        org_name=org_name,
        via_firebase=True,
        firebase_uid=firebase_uid,
    )


def get_current_org(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization: Bearer <firebase_id_token or org_api_key>",
        )
    if token.startswith("le_org_"):
        return _auth_from_org_api_key(token)
    return _auth_from_firebase_token(token)


def run_access(
    run_id: str,
    authorization: Annotated[str | None, Header()] = None,
    token: Annotated[str | None, Query()] = None,
) -> AuthContext:
    if token:
        org_id = get_share_org(run_id, token)
        if not org_id:
            raise HTTPException(status_code=403, detail="Invalid share token.")
        org = get_org(org_id)
        if not org:
            raise HTTPException(status_code=403, detail="Invalid share token.")
        return AuthContext(org_id=org_id, org_name=org["name"], via_share=True)
    return get_current_org(authorization)
