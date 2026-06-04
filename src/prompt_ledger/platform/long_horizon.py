from __future__ import annotations

from typing import Any

from prompt_ledger.platform.config import load_platform_yaml
from prompt_ledger.platform.gym_env import reset, step


def list_long_horizon_tasks() -> list[dict[str, Any]]:
    raw = load_platform_yaml("long_horizon_tasks.yaml")
    return [
        {
            "id": k,
            "label": v.get("label"),
            "environment": v.get("environment"),
            "horizon_steps": v.get("horizon_steps"),
            "step_count": len(v.get("steps") or []),
        }
        for k, v in (raw.get("tasks") or {}).items()
    ]


def run_long_horizon_task(task_id: str) -> dict[str, Any]:
    raw = load_platform_yaml("long_horizon_tasks.yaml")
    task = (raw.get("tasks") or {}).get(task_id)
    if not task:
        raise KeyError(f"unknown task {task_id!r}")

    env = str(task["environment"])
    ep = reset(env)
    episode_id = ep["episode_id"]
    rewards: list[float] = []
    last: dict[str, Any] = {"done": False}

    for step_def in task.get("steps") or []:
        tool = str(step_def.get("tool", "rag_retriever"))
        last = step(episode_id, {"tool": tool, "task": step_def.get("id", "")})
        rewards.append(float(last["reward"]))
        if last["terminated"]:
            break

    return {
        "task_id": task_id,
        "episode_id": episode_id,
        "steps_executed": len(rewards),
        "horizon_steps": task.get("horizon_steps"),
        "rewards": rewards,
        "total_reward": round(sum(rewards), 4),
        "done": last.get("done", True),
    }


def computer_use_targets() -> dict[str, Any]:
    raw = load_platform_yaml("long_horizon_tasks.yaml")
    return raw.get("computer_use") or {}
