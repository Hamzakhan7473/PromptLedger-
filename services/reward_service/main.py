"""reward-service: weighted reward computation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from prompt_ledger.platform.models import RewardBreakdown
from prompt_ledger.platform.orchestrator import run_agent_task
from prompt_ledger.platform.reward_formula import (
    compute_standard_reward,
    from_trajectory_breakdown,
    load_default_weights,
)
from services.shared import create_service_app

app = create_service_app("reward-service")


class RewardBody(BaseModel):
    correctness: float = Field(ge=0, le=1)
    citations: float = Field(ge=0, le=1)
    latency: float = Field(ge=0, le=1)
    cost: float = Field(ge=0, le=1)
    compliance: float = Field(ge=0, le=1)


class TrajectoryRewardBody(BaseModel):
    environment: str
    task: str


@app.get("/api/v1/reward/formula")
def formula() -> dict[str, Any]:
    from prompt_ledger.platform.config import load_platform_yaml

    raw = load_platform_yaml("reward_formula.yaml")
    return {"weights": load_default_weights(), "formula": raw.get("formula", "").strip()}


@app.post("/api/v1/reward/compute")
def compute(body: RewardBody) -> dict[str, Any]:
    return compute_standard_reward(
        correctness=body.correctness,
        citations=body.citations,
        latency=body.latency,
        cost=body.cost,
        compliance=body.compliance,
    )


@app.post("/api/v1/reward/from-run")
def from_run(body: TrajectoryRewardBody) -> dict[str, Any]:
    result = run_agent_task(body.environment, body.task, persist=False)
    rb = RewardBreakdown(**{k: v for k, v in result["reward"].items() if k != "total"})
    rb.total = result["reward"]["total"]
    standard = from_trajectory_breakdown(rb)
    return {"run": result, "standard_reward": standard}
