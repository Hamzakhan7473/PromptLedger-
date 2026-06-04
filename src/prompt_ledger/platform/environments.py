from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from prompt_ledger.platform.config import load_platform_yaml


@dataclass(frozen=True)
class RLEnvironment:
    key: str
    label: str
    description: str
    prompt_id: str
    pack_dir: str
    demo_vertical: str
    tools: list[str]
    reward_weights: dict[str, float]


def load_environments() -> dict[str, RLEnvironment]:
    raw = load_platform_yaml("environments.yaml")
    out: dict[str, RLEnvironment] = {}
    for key, v in (raw.get("environments") or {}).items():
        out[key] = RLEnvironment(
            key=key,
            label=str(v["label"]),
            description=str(v.get("description", "")),
            prompt_id=str(v["prompt_id"]),
            pack_dir=str(v["pack_dir"]),
            demo_vertical=str(v.get("demo_vertical", key)),
            tools=list(v.get("tools") or []),
            reward_weights={k: float(val) for k, val in (v.get("reward_weights") or {}).items()},
        )
    return out


def list_environments() -> list[dict[str, Any]]:
    return [
        {
            "id": e.key,
            "label": e.label,
            "description": e.description,
            "prompt_id": e.prompt_id,
            "tools": e.tools,
            "demo_vertical": e.demo_vertical,
        }
        for e in load_environments().values()
    ]
