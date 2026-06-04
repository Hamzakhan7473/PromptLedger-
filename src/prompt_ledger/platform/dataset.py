from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from prompt_ledger.paths import repo_root
from prompt_ledger.platform.trajectory_store import get_trajectory, list_trajectories


def build_rl_datasets(
    *,
    environment: str | None = None,
    reward_threshold: float = 0.7,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Export SFT, preference, DPO, and GRPO-shaped JSONL from stored trajectories."""
    out = output_dir or (repo_root() / ".data" / "datasets")
    out.mkdir(parents=True, exist_ok=True)

    rows = list_trajectories(environment=environment, limit=200)
    successful: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    for row in rows:
        full = get_trajectory(row["id"])
        if not full:
            continue
        if float(full.get("reward", {}).get("total", 0)) >= reward_threshold:
            successful.append(full)
        else:
            failed.append(full)

    sft_path = out / "sft.jsonl"
    pref_path = out / "preference.jsonl"
    dpo_path = out / "dpo.jsonl"
    grpo_path = out / "grpo.jsonl"

    _write_jsonl(sft_path, [_sft_record(t) for t in successful])
    _write_jsonl(pref_path, _preference_pairs(successful, failed))
    _write_jsonl(dpo_path, _dpo_pairs(successful, failed))
    _write_jsonl(grpo_path, [_grpo_record(t) for t in successful + failed])

    return {
        "output_dir": str(out),
        "successful": len(successful),
        "failed": len(failed),
        "files": {
            "sft": str(sft_path),
            "preference": str(pref_path),
            "dpo": str(dpo_path),
            "grpo": str(grpo_path),
        },
    }


def _sft_record(traj: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt": traj.get("prompt_text", ""),
        "completion": traj.get("final_output", ""),
        "metadata": {
            "environment": traj.get("environment"),
            "trajectory_id": traj.get("id"),
            "reward": traj.get("reward", {}).get("total"),
        },
    }


def _preference_pairs(
    good: list[dict[str, Any]],
    bad: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for g in good[: min(20, len(good))]:
        for b in bad[:1]:
            pairs.append(
                {
                    "prompt": g.get("prompt_text", ""),
                    "chosen": g.get("final_output", ""),
                    "rejected": b.get("final_output", ""),
                }
            )
    return pairs


def _dpo_pairs(
    good: list[dict[str, Any]],
    bad: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return [
        {
            "prompt": g.get("prompt_text", ""),
            "chosen": g.get("final_output", ""),
            "rejected": (bad[i % len(bad)] if bad else {}).get("final_output", ""),
        }
        for i, g in enumerate(good[:20])
    ]


def _grpo_record(traj: dict[str, Any]) -> dict[str, Any]:
    return {
        "prompt": traj.get("prompt_text", ""),
        "responses": [traj.get("final_output", "")],
        "rewards": [traj.get("reward", {}).get("total", 0.0)],
        "group_id": traj.get("environment"),
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
