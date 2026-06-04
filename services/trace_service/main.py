"""trace-service: trajectory storage (Postgres + S3; SQLite in demo)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from prompt_ledger.platform.gym_env import get_episode_transitions
from prompt_ledger.platform.trajectory_store import get_trajectory, list_trajectories
from prompt_ledger.platform.orchestrator import run_agent_task
from services.shared import create_service_app

app = create_service_app("trace-service")


class RecordBody(BaseModel):
    environment: str
    task: str


@app.get("/api/v1/trace")
def list_traces(environment: str | None = None, limit: int = 50) -> dict[str, Any]:
    return {"trajectories": list_trajectories(environment=environment, limit=limit)}


@app.get("/api/v1/trace/{trajectory_id}")
def get_trace(trajectory_id: str) -> dict[str, Any]:
    data = get_trajectory(trajectory_id)
    if not data:
        from fastapi import HTTPException

        raise HTTPException(404, "trajectory not found")
    return data


@app.post("/api/v1/trace/record")
def record(body: RecordBody) -> dict[str, Any]:
    result = run_agent_task(body.environment, body.task, persist=True)
    steps = []
    for i, s in enumerate(result["trajectory"].get("steps", [])):
        steps.append({f"state_{i}": s["state"], f"action_{i}": s["action"], f"observation_{i}": s["observation"]})
    return {"trajectory_id": result["trajectory_id"], "steps": steps}


@app.get("/api/v1/trace/episode/{episode_id}/transitions")
def episode_transitions(episode_id: str) -> dict[str, Any]:
    return {"episode_id": episode_id, "transitions": get_episode_transitions(episode_id)}
