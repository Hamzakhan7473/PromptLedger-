"""Map HF datasets that already expose EvalExample-shaped columns."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from legaleval.data.schema import EvalExample


def identity_adapter(rows: Iterable[Mapping[str, Any]]) -> list[EvalExample]:
    examples: list[EvalExample] = []
    for row_no, row in enumerate(rows, start=1):
        try:
            examples.append(EvalExample.model_validate(dict(row)))
        except ValueError as exc:
            raise ValueError(f"Row {row_no}: {exc}") from exc
    return examples
