from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from prompt_ledger.load import read_yaml, write_yaml
from prompt_ledger.paths import repo_root


def approval_path() -> Path:
    return repo_root() / ".promptledger" / "approval.yaml"


@dataclass
class ApprovalRecord:
    status: str  # pending | approved | declined
    target_environment: str
    sync_from: str | None
    requested_at: str
    requested_by: str
    approved_at: str | None = None
    approved_by: str | None = None
    declined_at: str | None = None
    declined_by: str | None = None
    note: str | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_approval() -> ApprovalRecord | None:
    p = approval_path()
    if not p.is_file():
        return None
    raw = read_yaml(p)
    return ApprovalRecord(
        status=str(raw.get("status", "pending")),
        target_environment=str(raw["target_environment"]),
        sync_from=raw.get("sync_from"),
        requested_at=str(raw.get("requested_at", "")),
        requested_by=str(raw.get("requested_by", "unknown")),
        approved_at=raw.get("approved_at"),
        approved_by=raw.get("approved_by"),
        declined_at=raw.get("declined_at"),
        declined_by=raw.get("declined_by"),
        note=raw.get("note"),
    )


def save_approval(rec: ApprovalRecord) -> Path:
    p = approval_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    write_yaml(p, asdict(rec))
    return p


def request_approval(
    *,
    target_environment: str,
    sync_from: str | None,
    requested_by: str,
) -> ApprovalRecord:
    existing = load_approval()
    if existing and existing.status == "pending":
        raise ValueError("an approval request is already pending; approve or decline it first")
    rec = ApprovalRecord(
        status="pending",
        target_environment=target_environment,
        sync_from=sync_from,
        requested_at=_now(),
        requested_by=requested_by,
    )
    save_approval(rec)
    return rec


def approve(*, approved_by: str, note: str | None = None) -> ApprovalRecord:
    rec = load_approval()
    if not rec or rec.status != "pending":
        raise ValueError("no pending approval request")
    rec.status = "approved"
    rec.approved_at = _now()
    rec.approved_by = approved_by
    rec.note = note
    save_approval(rec)
    return rec


def decline(*, declined_by: str, note: str | None = None) -> ApprovalRecord:
    rec = load_approval()
    if not rec or rec.status != "pending":
        raise ValueError("no pending approval request")
    rec.status = "declined"
    rec.declined_at = _now()
    rec.declined_by = declined_by
    rec.note = note
    save_approval(rec)
    return rec


def assert_approved_for_promotion(target_environment: str, sync_from: str | None) -> None:
    rec = load_approval()
    if not rec or rec.status != "approved":
        raise ValueError("promotion requires an approved request (prompt-ledger approval approve)")
    if rec.target_environment != target_environment:
        raise ValueError(
            f"approval is for {rec.target_environment!r}, not {target_environment!r}",
        )
    if (rec.sync_from or None) != (sync_from or None):
        raise ValueError("approval sync_from does not match promote --sync-from")
