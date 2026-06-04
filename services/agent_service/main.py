"""agent-service: LangGraph + Temporal + multi-agent execution (orchestration layer)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from prompt_ledger.platform.long_horizon import list_long_horizon_tasks, run_long_horizon_task
from prompt_ledger.platform.multi_agent import load_supervisor_graph, run_supervisor_task
from prompt_ledger.platform.orchestrator import run_agent_task
from services.shared import create_service_app

app = create_service_app("agent-service")


class RunBody(BaseModel):
    environment: str
    task: str
    cost_sensitive: bool = False


class SupervisorBody(BaseModel):
    environment: str
    task: str
    agents: list[str] | None = None


@app.get("/api/v1/agent/graph")
def supervisor_graph() -> dict[str, Any]:
    return load_supervisor_graph()


@app.post("/api/v1/agent/run")
def agent_run(body: RunBody) -> dict[str, Any]:
    return run_agent_task(body.environment, body.task, cost_sensitive=body.cost_sensitive)


@app.post("/api/v1/agent/supervisor")
def supervisor_run(body: SupervisorBody) -> dict[str, Any]:
    return run_supervisor_task(body.environment, body.task, agents=body.agents)


@app.get("/api/v1/agent/long-horizon")
def long_horizon_list() -> dict[str, Any]:
    return {"tasks": list_long_horizon_tasks()}


@app.post("/api/v1/agent/long-horizon/{task_id}")
def long_horizon_run(task_id: str) -> dict[str, Any]:
    return run_long_horizon_task(task_id)
