from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from prompt_ledger.paths import repo_root
from prompt_ledger.platform.models import Trajectory


def trajectory_db_path() -> Path:
    env_path = __import__("os").environ.get("TRAJECTORY_DB_PATH")
    if env_path:
        return Path(env_path)
    return repo_root() / ".data" / "trajectories.db"


def init_db(path: Path | None = None) -> Path:
    db = path or trajectory_db_path()
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trajectories (
                id TEXT PRIMARY KEY,
                environment TEXT NOT NULL,
                prompt_id TEXT NOT NULL,
                model TEXT NOT NULL,
                task TEXT NOT NULL,
                payload JSON NOT NULL,
                reward_total REAL NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    return db


def save_trajectory(traj: Trajectory, path: Path | None = None) -> str:
    db = init_db(path)
    tid = traj.id or str(uuid.uuid4())
    traj.id = tid
    payload = json.dumps(traj.to_dict())
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO trajectories
            (id, environment, prompt_id, model, task, payload, reward_total)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                tid,
                traj.environment,
                traj.prompt_id,
                traj.model,
                traj.task,
                payload,
                traj.reward.total,
            ),
        )
        conn.commit()
    return tid


def list_trajectories(
    *,
    environment: str | None = None,
    limit: int = 50,
    path: Path | None = None,
) -> list[dict[str, Any]]:
    db = init_db(path)
    query = "SELECT id, environment, prompt_id, model, task, reward_total, created_at FROM trajectories"
    params: list[Any] = []
    if environment:
        query += " WHERE environment = ?"
        params.append(environment)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with sqlite3.connect(db) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_trajectory(trajectory_id: str, path: Path | None = None) -> dict[str, Any] | None:
    db = init_db(path)
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "SELECT payload FROM trajectories WHERE id = ?",
            (trajectory_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row[0])
