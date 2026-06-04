"""dataset-service: SFT, preference, DPO, GRPO dataset export."""

from __future__ import annotations

from typing import Any

from prompt_ledger.platform.dataset import build_rl_datasets
from services.shared import create_service_app

app = create_service_app("dataset-service")


@app.post("/api/v1/datasets/build")
def build(environment: str | None = None, reward_threshold: float = 0.7) -> dict[str, Any]:
    return build_rl_datasets(environment=environment, reward_threshold=reward_threshold)


@app.get("/api/v1/datasets/types")
def types() -> dict[str, list[str]]:
    return {
        "formats": ["sft", "preference", "dpo", "grpo"],
        "files": ["sft.jsonl", "preference.jsonl", "dpo.jsonl", "grpo.jsonl"],
    }
