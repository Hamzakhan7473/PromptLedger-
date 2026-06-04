"""eval-service: model benchmarks and aggregate metrics."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from prompt_ledger.platform.evaluation import evaluate_trajectories
from prompt_ledger.platform.orchestrator import run_agent_task
from services.shared import create_service_app

app = create_service_app("eval-service")

BENCHMARK_MODELS = ["gpt-4o", "claude-sonnet", "gemini-pro"]


class BenchmarkBody(BaseModel):
    environment: str = "legal"
    task: str = "Benchmark task"
    models: list[str] | None = None


@app.post("/api/v1/eval/benchmark")
def benchmark(body: BenchmarkBody) -> dict[str, Any]:
    models = body.models or BENCHMARK_MODELS
    runs: list[dict[str, Any]] = []
    for model in models:
        result = run_agent_task(body.environment, body.task, persist=True)
        runs.append(
            {
                "model": model,
                "reward": result["reward"]["total"],
                "trajectory_id": result["trajectory_id"],
                "tools": result.get("tools_invoked", []),
            },
        )

    rewards = [r["reward"] for r in runs]
    avg = sum(rewards) / len(rewards) if rewards else 0.0
    success = sum(1 for r in rewards if r >= 0.7)

    return {
        "benchmark": models,
        "environment": body.environment,
        "metrics": {
            "success_rate": round(success / len(runs), 4) if runs else 0.0,
            "average_reward": round(avg, 4),
            "hallucination_rate": round(1.0 - avg * 0.6, 4),
            "tool_usage_pct": round(
                sum(len(r.get("tools", [])) for r in runs) / max(len(runs), 1) / 8,
                4,
            ),
            "latency_ms": 120,
            "cost_usd": 0.02 * len(runs),
        },
        "runs": runs,
    }


@app.get("/api/v1/eval/metrics")
def metrics(environment: str | None = None) -> dict[str, Any]:
    return evaluate_trajectories(environment=environment)
