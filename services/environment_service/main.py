"""environment-service: OpenAI Gym-style RL environments."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from prompt_ledger.platform.environments import list_environments
from prompt_ledger.platform.gym_env import episode_done, episode_reward, reset, step
from services.shared import create_service_app

app = create_service_app("environment-service")


class ResetBody(BaseModel):
    environment: str
    seed: int | None = None


class StepBody(BaseModel):
    episode_id: str
    action: str | dict[str, Any]


@app.get("/api/v1/env")
def list_envs() -> dict[str, Any]:
    return {"environments": list_environments()}


@app.post("/api/v1/env/reset")
def env_reset(body: ResetBody) -> dict[str, Any]:
    return reset(body.environment, seed=body.seed)


@app.post("/api/v1/env/step")
def env_step(body: StepBody) -> dict[str, Any]:
    return step(body.episode_id, body.action)


@app.get("/api/v1/env/{episode_id}/reward")
def env_reward(episode_id: str) -> dict[str, Any]:
    return episode_reward(episode_id)


@app.get("/api/v1/env/{episode_id}/done")
def env_done(episode_id: str) -> dict[str, bool]:
    return {"episode_id": episode_id, "done": episode_done(episode_id)}
