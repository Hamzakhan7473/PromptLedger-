"""Immutable audit trail for org actions."""

from __future__ import annotations

import secrets
from typing import Any

from legal_eval_api.db import insert_audit_event, list_audit_events


def record_audit(
    org_id: str,
    action: str,
    *,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    insert_audit_event(
        event_id=secrets.token_hex(12),
        org_id=org_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
    )


def get_audit_log(org_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
    return list_audit_events(org_id, limit=limit)
