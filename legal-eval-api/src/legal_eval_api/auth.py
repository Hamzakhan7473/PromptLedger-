"""Organization authentication dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Query

from legal_eval_api.db import get_org, get_org_by_api_key, get_share_org


@dataclass(frozen=True)
class AuthContext:
    org_id: str
    org_name: str
    via_share: bool = False


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def get_current_org(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthContext:
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization: Bearer <org_api_key>",
        )
    org = get_org_by_api_key(token)
    if not org:
        raise HTTPException(status_code=401, detail="Invalid organization API key.")
    return AuthContext(org_id=org["org_id"], org_name=org["name"])


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
