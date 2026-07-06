"""Import Hugging Face datasets and convert them to EvalExample rows."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException
from legaleval.data.schema import EvalExample

from legal_eval_api.dataset_sources.adapters import AdapterSpec, get_adapter

logger = logging.getLogger(__name__)

DEFAULT_MAX_EXAMPLES = 100
MAX_EXAMPLES_CAP = 10_000


def load_hf_rows(
    *,
    repo_id: str,
    config: str | None,
    split: str,
    max_examples: int,
) -> list[dict[str, Any]]:
    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise HTTPException(
            status_code=503,
            detail="Hugging Face import requires the `datasets` package on the API server.",
        ) from exc

    capped = max(1, min(max_examples, MAX_EXAMPLES_CAP))
    try:
        if config:
            dataset = load_dataset(repo_id, config, split=split)
        else:
            dataset = load_dataset(repo_id, split=split)
    except Exception as exc:  # noqa: BLE001 — surface HF/network errors to client
        message = str(exc).strip() or type(exc).__name__
        lowered = message.lower()
        if "couldn't find" in lowered or "not found" in lowered or "unknown" in lowered:
            status = 404
        else:
            status = 502
        raise HTTPException(
            status_code=status,
            detail=f"Failed to load Hugging Face dataset {repo_id!r}"
            + (f" config {config!r}" if config else "")
            + f" split {split!r}: {message}",
        ) from exc

    rows: list[dict[str, Any]] = []
    for index, row in enumerate(dataset):
        if index >= capped:
            break
        rows.append(dict(row))
    if not rows:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Dataset {repo_id!r}"
                + (f" config {config!r}" if config else "")
                + f" split {split!r} returned no rows."
            ),
        )
    return rows


def import_hf_dataset(
    *,
    repo_id: str,
    config: str | None,
    split: str,
    max_examples: int,
    adapter_name: str,
) -> tuple[list[EvalExample], AdapterSpec]:
    adapter = _resolve_adapter(adapter_name)
    rows = load_hf_rows(
        repo_id=repo_id,
        config=config,
        split=split,
        max_examples=max_examples,
    )
    try:
        examples = adapter.convert(rows)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not examples:
        raise HTTPException(
            status_code=400,
            detail="Adapter produced no EvalExample rows after conversion.",
        )
    return examples, adapter


def _resolve_adapter(adapter_name: str) -> AdapterSpec:
    try:
        return get_adapter(adapter_name)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
