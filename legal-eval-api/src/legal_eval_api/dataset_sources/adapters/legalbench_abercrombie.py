"""LegalBench abercrombie → EvalExample (classification-as-extraction)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from legaleval.data.schema import EvalExample

_CATEGORY = "abercrombie_mark_type"
_TITLE = "LegalBench abercrombie"


def legalbench_abercrombie_adapter(rows: Iterable[Mapping[str, Any]]) -> list[EvalExample]:
    examples: list[EvalExample] = []
    for row_no, row in enumerate(rows, start=1):
        text = row.get("text")
        if text is None:
            raise ValueError(f"Row {row_no}: missing 'text' column")
        answer = row.get("answer")
        if answer is None:
            raise ValueError(f"Row {row_no}: missing 'answer' column")
        example_id = str(row.get("index", row_no - 1))
        label = str(answer).strip()
        examples.append(
            EvalExample(
                id=example_id,
                contract_excerpt=str(text),
                category=_CATEGORY,
                present=True,
                gold_spans=[label],
                contract_title=_TITLE,
            ),
        )
    return examples
