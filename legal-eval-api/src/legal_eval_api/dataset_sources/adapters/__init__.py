"""Hugging Face row → EvalExample adapters."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from legaleval.data.schema import EvalExample

from legal_eval_api.dataset_sources.adapters.identity import identity_adapter
from legal_eval_api.dataset_sources.adapters.legalbench_abercrombie import (
    legalbench_abercrombie_adapter,
)

TaskFit = Literal["span_extraction", "classification_as_extraction"]


@dataclass(frozen=True)
class AdapterSpec:
    name: str
    description: str
    task_fit: TaskFit
    warning: str | None
    convert: Callable[[Iterable[Mapping[str, Any]]], list[EvalExample]]


CLASSIFICATION_WARNING = (
    "This dataset uses classification labels, not verbatim spans. "
    "Span Jaccard and presence F1 will not reflect extraction accuracy in the usual sense."
)


ADAPTER_REGISTRY: dict[str, AdapterSpec] = {
    "identity": AdapterSpec(
        name="identity",
        description=(
            "HF rows already use EvalExample columns "
            "(id, contract_excerpt, category, present, gold_spans, contract_title)."
        ),
        task_fit="span_extraction",
        warning=None,
        convert=identity_adapter,
    ),
    "legalbench_abercrombie": AdapterSpec(
        name="legalbench_abercrombie",
        description=(
            "LegalBench abercrombie config: maps text + answer label into EvalExample rows."
        ),
        task_fit="classification_as_extraction",
        warning=CLASSIFICATION_WARNING,
        convert=legalbench_abercrombie_adapter,
    ),
}


def get_adapter(name: str) -> AdapterSpec:
    try:
        return ADAPTER_REGISTRY[name]
    except KeyError as exc:
        known = ", ".join(sorted(ADAPTER_REGISTRY))
        raise KeyError(f"Unknown adapter {name!r}. Known adapters: {known}") from exc


def list_adapters() -> list[AdapterSpec]:
    return [ADAPTER_REGISTRY[key] for key in sorted(ADAPTER_REGISTRY)]
