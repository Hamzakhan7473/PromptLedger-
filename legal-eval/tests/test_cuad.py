"""Tests for CUAD eval-set construction."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest
from pydantic import TypeAdapter

from legaleval.data.schema import EvalExample, write_eval_set_jsonl
from legaleval.data.cuad import (
    build_eval_set_from_raw,
    cap_excerpt,
    normalize_cuad,
)
from tests.fixtures.synthetic_cuad import make_synthetic_cuad

EvalExampleList = TypeAdapter(list[EvalExample])


@pytest.fixture
def synthetic_cuad() -> dict:
    return make_synthetic_cuad()


def test_normalize_cuad_extracts_categories(synthetic_cuad: dict) -> None:
    contracts = normalize_cuad(synthetic_cuad)
    assert len(contracts) == 9
    categories = {qa.category for contract in contracts for qa in contract.qas}
    assert categories == {"Cap On Liability", "Anti-Assignment", "Audit Rights"}


def test_cap_excerpt_preserves_gold_span() -> None:
    context = "a" * 100 + "TARGET" + "b" * 200
    excerpt = cap_excerpt(context, ["TARGET"], [100], max_chars=50)
    assert "TARGET" in excerpt
    assert len(excerpt) <= len(context)


def test_cap_excerpt_truncates_absent_without_spans() -> None:
    context = "z" * 10_000
    excerpt = cap_excerpt(context, [], [], max_chars=8000)
    assert len(excerpt) == 8000
    assert excerpt == context[:8000]


def test_eval_examples_match_schema(synthetic_cuad: dict) -> None:
    examples = build_eval_set_from_raw(
        synthetic_cuad,
        categories=["Cap On Liability", "Anti-Assignment"],
        n_categories=2,
        n_per_category=4,
        seed=42,
    )
    validated = EvalExampleList.validate_python([ex.model_dump() for ex in examples])
    assert len(validated) == 8
    for example in validated:
        assert example.id.startswith("cuad-")
        if example.present:
            assert example.gold_spans
        else:
            assert example.gold_spans == []


def test_seed_determinism(synthetic_cuad: dict) -> None:
    kwargs = dict(
        categories=["Cap On Liability", "Anti-Assignment", "Audit Rights"],
        n_categories=3,
        n_per_category=6,
        seed=99,
    )
    first = build_eval_set_from_raw(synthetic_cuad, **kwargs)
    second = build_eval_set_from_raw(synthetic_cuad, **kwargs)
    assert [ex.model_dump() for ex in first] == [ex.model_dump() for ex in second]


def test_present_absent_balance(synthetic_cuad: dict) -> None:
    n_per_category = 6
    examples = build_eval_set_from_raw(
        synthetic_cuad,
        categories=["Cap On Liability", "Anti-Assignment", "Audit Rights"],
        n_categories=3,
        n_per_category=n_per_category,
        seed=7,
    )
    assert len(examples) == n_per_category * 3

    by_category: dict[str, Counter[bool]] = {}
    for example in examples:
        by_category.setdefault(example.category, Counter())[example.present] += 1

    for category, counts in by_category.items():
        assert counts[True] == n_per_category // 2, category
        assert counts[False] == n_per_category - n_per_category // 2, category


def test_write_eval_set_jsonl_roundtrip(
    synthetic_cuad: dict, tmp_path: Path
) -> None:
    examples = build_eval_set_from_raw(
        synthetic_cuad,
        categories=["Cap On Liability", "Anti-Assignment"],
        n_categories=2,
        n_per_category=4,
        seed=1,
    )
    output = tmp_path / "eval_set.jsonl"
    write_eval_set_jsonl(examples, output)

    lines = output.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 8
    for line in lines:
        payload = json.loads(line)
        EvalExample.model_validate(payload)
