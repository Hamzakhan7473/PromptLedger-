"""Generic eval-set schema and JSONL I/O (dataset-source agnostic)."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class EvalExample(BaseModel):
    id: str
    contract_excerpt: str
    category: str
    present: bool
    gold_spans: list[str]
    contract_title: str


def read_eval_set_jsonl(path: Path) -> list[EvalExample]:
    examples: list[EvalExample] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                examples.append(EvalExample.model_validate_json(line))
    return examples


def write_eval_set_jsonl(
    examples: list[EvalExample],
    output_path: Path | None = None,
) -> Path:
    from legaleval.paths import default_eval_set_path

    path = output_path or default_eval_set_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for example in examples:
            handle.write(example.model_dump_json() + "\n")
    return path


def semantic_validation_errors(examples: list[EvalExample]) -> list[str]:
    """Return human-readable errors for dataset semantics (empty list = ok)."""
    errors: list[str] = []
    for line_no, example in enumerate(examples, start=1):
        if example.present and not example.gold_spans:
            errors.append(
                f"Line {line_no} (id={example.id!r}): present=true requires "
                "non-empty gold_spans"
            )
    if not any(example.present and example.gold_spans for example in examples):
        errors.append(
            "Dataset has no present examples with gold spans; judge validation "
            "requires at least one to build a validation pool."
        )
    return errors


def gold_span_warnings(examples: list[EvalExample]) -> list[str]:
    """Warn when gold spans are not verbatim substrings of the contract excerpt."""
    from legaleval.metrics.span import span_in_contract

    warnings: list[str] = []
    for example in examples:
        if not example.present:
            continue
        for span in example.gold_spans:
            if span and not span_in_contract(span, example.contract_excerpt):
                warnings.append(
                    f"Example {example.id!r}: gold_span not found verbatim in "
                    f"contract_excerpt: {span!r}"
                )
    return warnings
