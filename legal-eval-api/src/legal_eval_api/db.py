"""SQLite persistence for organizations."""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator

from legal_eval_api.config import DATA_ROOT

DB_PATH = DATA_ROOT / "legal_eval.db"


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_org_api_key() -> str:
    return f"le_org_{secrets.token_urlsafe(32)}"


def generate_share_token() -> str:
    return secrets.token_urlsafe(24)


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orgs (
                org_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                api_key_hash TEXT NOT NULL UNIQUE,
                enabled_models TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                firebase_uid TEXT,
                onboarding_completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS org_secrets (
                org_id TEXT NOT NULL,
                env_key TEXT NOT NULL,
                encrypted_value TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (org_id, env_key),
                FOREIGN KEY (org_id) REFERENCES orgs(org_id)
            );

            CREATE TABLE IF NOT EXISTS share_links (
                run_id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                FOREIGN KEY (org_id) REFERENCES orgs(org_id)
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                event_id TEXT PRIMARY KEY,
                org_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL,
                FOREIGN KEY (org_id) REFERENCES orgs(org_id)
            );

            CREATE INDEX IF NOT EXISTS idx_audit_org_created
                ON audit_events (org_id, created_at DESC);

            CREATE TABLE IF NOT EXISTS org_settings (
                org_id TEXT PRIMARY KEY,
                webhook_url TEXT,
                webhook_secret_encrypted TEXT,
                bedrock_region TEXT,
                bedrock_endpoint_url TEXT,
                sso_domain TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (org_id) REFERENCES orgs(org_id)
            );
            """
        )
        _migrate_orgs_schema(conn)


def _migrate_orgs_schema(conn: sqlite3.Connection) -> None:
    """Apply additive schema changes for org identity columns."""
    columns = {row[1] for row in conn.execute("PRAGMA table_info(orgs)")}
    if "onboarding_completed_at" not in columns:
        conn.execute("ALTER TABLE orgs ADD COLUMN onboarding_completed_at TEXT")
    # Fresh firebase_uid column (not renamed from clerk_user_id — SQLite has no cheap rename).
    if "firebase_uid" not in columns:
        conn.execute("ALTER TABLE orgs ADD COLUMN firebase_uid TEXT")
    if "clerk_user_id" in columns:
        conn.execute(
            """
            UPDATE orgs
            SET firebase_uid = clerk_user_id
            WHERE firebase_uid IS NULL AND clerk_user_id IS NOT NULL
            """
        )
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_orgs_firebase_uid
            ON orgs(firebase_uid) WHERE firebase_uid IS NOT NULL
        """
    )


def create_org(name: str, *, firebase_uid: str | None = None) -> tuple[str, str]:
    org_id = secrets.token_hex(8)
    api_key = generate_org_api_key()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO orgs (
                org_id, name, api_key_hash, enabled_models, created_at, firebase_uid
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                org_id,
                name,
                hash_api_key(api_key),
                json.dumps(["openai", "google", "bedrock_claude"]),
                utc_now_iso(),
                firebase_uid,
            ),
        )
    return org_id, api_key


def get_org_by_api_key(api_key: str) -> dict[str, Any] | None:
    key_hash = hash_api_key(api_key)
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM orgs WHERE api_key_hash = ?",
            (key_hash,),
        ).fetchone()
    return dict(row) if row else None


def get_org(org_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM orgs WHERE org_id = ?", (org_id,)).fetchone()
    return dict(row) if row else None


def get_org_by_firebase_uid(firebase_uid: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM orgs WHERE firebase_uid = ?",
            (firebase_uid,),
        ).fetchone()
    return dict(row) if row else None


def complete_onboarding(org_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE orgs SET onboarding_completed_at = ? WHERE org_id = ?",
            (utc_now_iso(), org_id),
        )


def list_org_ids() -> list[str]:
    with connect() as conn:
        rows = conn.execute("SELECT org_id FROM orgs ORDER BY created_at").fetchall()
    return [row["org_id"] for row in rows]


def set_enabled_models(org_id: str, models: list[str]) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE orgs SET enabled_models = ? WHERE org_id = ?",
            (json.dumps(models), org_id),
        )


def get_enabled_models(org_id: str) -> list[str]:
    org = get_org(org_id)
    if not org:
        return []
    return json.loads(org["enabled_models"])


def upsert_secret(org_id: str, env_key: str, encrypted_value: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO org_secrets (org_id, env_key, encrypted_value, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(org_id, env_key) DO UPDATE SET
                encrypted_value = excluded.encrypted_value,
                updated_at = excluded.updated_at
            """,
            (org_id, env_key, encrypted_value, utc_now_iso()),
        )


def delete_secret(org_id: str, env_key: str) -> None:
    with connect() as conn:
        conn.execute(
            "DELETE FROM org_secrets WHERE org_id = ? AND env_key = ?",
            (org_id, env_key),
        )


def list_secret_keys(org_id: str) -> list[str]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT env_key FROM org_secrets WHERE org_id = ? ORDER BY env_key",
            (org_id,),
        ).fetchall()
    return [row["env_key"] for row in rows]


def get_secrets(org_id: str) -> dict[str, str]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT env_key, encrypted_value FROM org_secrets WHERE org_id = ?",
            (org_id,),
        ).fetchall()
    return {row["env_key"]: row["encrypted_value"] for row in rows}


def upsert_share_link(run_id: str, org_id: str, token: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO share_links (run_id, org_id, token_hash, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                token_hash = excluded.token_hash,
                created_at = excluded.created_at
            """,
            (run_id, org_id, hash_api_key(token), utc_now_iso()),
        )


def get_share_org(run_id: str, token: str) -> str | None:
    token_hash = hash_api_key(token)
    with connect() as conn:
        row = conn.execute(
            """
            SELECT org_id FROM share_links
            WHERE run_id = ? AND token_hash = ?
            """,
            (run_id, token_hash),
        ).fetchone()
    return row["org_id"] if row else None


def insert_audit_event(
    *,
    event_id: str,
    org_id: str,
    action: str,
    resource_type: str | None = None,
    resource_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_events
                (event_id, org_id, action, resource_type, resource_id, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                org_id,
                action,
                resource_type,
                resource_id,
                json.dumps(metadata or {}),
                utc_now_iso(),
            ),
        )


def list_audit_events(org_id: str, *, limit: int = 100) -> list[dict[str, Any]]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT * FROM audit_events
            WHERE org_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (org_id, limit),
        ).fetchall()
    events: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["metadata"] = json.loads(item["metadata"])
        events.append(item)
    return events


def get_org_settings(org_id: str) -> dict[str, Any]:
    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM org_settings WHERE org_id = ?",
            (org_id,),
        ).fetchone()
    if not row:
        return {
            "org_id": org_id,
            "webhook_url": None,
            "webhook_secret_encrypted": None,
            "bedrock_region": None,
            "bedrock_endpoint_url": None,
            "sso_domain": None,
            "updated_at": None,
        }
    return dict(row)


def upsert_org_settings(
    org_id: str,
    *,
    webhook_url: str | None = None,
    webhook_secret_encrypted: str | None = None,
    clear_webhook_secret: bool = False,
    bedrock_region: str | None = None,
    bedrock_endpoint_url: str | None = None,
    sso_domain: str | None = None,
) -> dict[str, Any]:
    current = get_org_settings(org_id)
    secret = current.get("webhook_secret_encrypted")
    if clear_webhook_secret:
        secret = None
    elif webhook_secret_encrypted is not None:
        secret = webhook_secret_encrypted

    with connect() as conn:
        conn.execute(
            """
            INSERT INTO org_settings (
                org_id, webhook_url, webhook_secret_encrypted,
                bedrock_region, bedrock_endpoint_url, sso_domain, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(org_id) DO UPDATE SET
                webhook_url = excluded.webhook_url,
                webhook_secret_encrypted = excluded.webhook_secret_encrypted,
                bedrock_region = excluded.bedrock_region,
                bedrock_endpoint_url = excluded.bedrock_endpoint_url,
                sso_domain = excluded.sso_domain,
                updated_at = excluded.updated_at
            """,
            (
                org_id,
                webhook_url if webhook_url is not None else current.get("webhook_url"),
                secret,
                bedrock_region if bedrock_region is not None else current.get("bedrock_region"),
                bedrock_endpoint_url
                if bedrock_endpoint_url is not None
                else current.get("bedrock_endpoint_url"),
                sso_domain if sso_domain is not None else current.get("sso_domain"),
                utc_now_iso(),
            ),
        )
    return get_org_settings(org_id)
