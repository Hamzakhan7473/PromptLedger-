"""Tests for dataset validation."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from legal_eval_api.datasets import parse_eval_jsonl, validate_dataset_semantics


def test_parse_eval_jsonl_valid() -> None:
    text = (
        '{"id":"a","contract_excerpt":"x","category":"Payment Terms",'
        '"present":true,"gold_spans":["x"],"contract_title":"T"}\n'
    )
    examples = parse_eval_jsonl(text)
    assert len(examples) == 1
    assert examples[0].id == "a"


def test_parse_eval_jsonl_invalid_line() -> None:
    with pytest.raises(HTTPException) as exc:
        parse_eval_jsonl('{"id":"missing fields"}\n')
    assert exc.value.status_code == 400


def test_reject_present_without_gold_spans() -> None:
    text = (
        '{"id":"a","contract_excerpt":"x","category":"Payment Terms",'
        '"present":true,"gold_spans":[],"contract_title":"T"}\n'
    )
    examples = parse_eval_jsonl(text)
    with pytest.raises(HTTPException) as exc:
        validate_dataset_semantics(examples)
    assert exc.value.status_code == 400
    assert "present=true requires non-empty gold_spans" in exc.value.detail


def test_reject_no_judge_validation_pool() -> None:
    text = (
        '{"id":"a","contract_excerpt":"x","category":"Payment Terms",'
        '"present":false,"gold_spans":[],"contract_title":"T"}\n'
    )
    examples = parse_eval_jsonl(text)
    with pytest.raises(HTTPException) as exc:
        validate_dataset_semantics(examples)
    assert exc.value.status_code == 400
    assert "judge validation" in exc.value.detail.lower()


def test_accepts_non_cuad_categories() -> None:
    text = (
        '{"id":"a","contract_excerpt":"Invoices are due in 30 days.",'
        '"category":"Payment Terms","present":true,'
        '"gold_spans":["Invoices are due in 30 days"],"contract_title":"T"}\n'
        '{"id":"b","contract_excerpt":"No payment clause.",'
        '"category":"Payment Terms","present":false,'
        '"gold_spans":[],"contract_title":"T2"}\n'
    )
    examples = parse_eval_jsonl(text)
    validate_dataset_semantics(examples)
