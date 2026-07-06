"""End-to-end checks that non-CUAD datasets work through metrics and judge validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from legaleval.data.schema import EvalExample, write_eval_set_jsonl
from legaleval.judge.validate import reference_span_correct, run_validation, validate_and_exit
from legaleval.metrics.compute import compute_run_metrics, write_metrics_json
from legaleval.models.runner import CallLogRow
from tests.test_judge import RuleMirrorJudge


NON_CUAD_EXAMPLES = [
    EvalExample(
        id="custom-001",
        contract_excerpt=(
            "Section 2. Payment Terms. Invoices are due within thirty (30) days. "
            "Late fees apply after day forty-five."
        ),
        category="Payment Terms",
        present=True,
        gold_spans=["Invoices are due within thirty (30) days"],
        contract_title="Vendor Agreement Alpha",
    ),
    EvalExample(
        id="custom-002",
        contract_excerpt="Section 2. Payment Terms. See general terms in Exhibit A.",
        category="Payment Terms",
        present=False,
        gold_spans=[],
        contract_title="Vendor Agreement Beta",
    ),
    EvalExample(
        id="custom-003",
        contract_excerpt=(
            "Article IV. Liquidated Damages. Buyer may recover pre-agreed damages "
            "of five thousand dollars per missed milestone."
        ),
        category="Liquidated Damages",
        present=True,
        gold_spans=["pre-agreed damages of five thousand dollars per missed milestone"],
        contract_title="Services Contract Gamma",
    ),
    EvalExample(
        id="custom-004",
        contract_excerpt="Article IV. Liquidated Damages. Not applicable to this order.",
        category="Liquidated Damages",
        present=False,
        gold_spans=[],
        contract_title="Services Contract Delta",
    ),
]


def test_metrics_for_non_cuad_categories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    eval_path = tmp_path / "custom.jsonl"
    write_eval_set_jsonl(NON_CUAD_EXAMPLES, eval_path)

    run_id = "custom-run"
    raw_dir = tmp_path / "raw" / run_id
    raw_dir.mkdir(parents=True)
    rows = [
        CallLogRow(
            run_id=run_id,
            example_id=example.id,
            category=example.category,
            contract_title=example.contract_title,
            provider="stub",
            model="stub",
            model_id="stub",
            latency_ms=1.0,
            parsed={
                "present": example.present,
                "span": example.gold_spans[0] if example.present else None,
                "confidence": 0.9,
                "reasoning": "stub",
            },
        )
        for example in NON_CUAD_EXAMPLES
    ]
    with (raw_dir / "stub.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(row.model_dump_json() + "\n")

    import legaleval.metrics.compute as compute_mod

    monkeypatch.setattr(compute_mod, "raw_results_dir", lambda rid: tmp_path / "raw" / rid)

    metrics = compute_run_metrics(run_id, eval_path, n_bootstrap=100, seed=0)
    stub_metrics = metrics["models"]["stub"]
    by_category = stub_metrics["presence"]["by_category"]
    assert "Payment Terms" in by_category
    assert "Liquidated Damages" in by_category
    assert "Anti-Assignment" not in by_category
    assert stub_metrics["presence"]["overall"]["f1"] == 1.0

    metrics_path = tmp_path / run_id / "metrics.json"
    write_metrics_json(metrics, metrics_path)
    assert metrics_path.exists()


def test_judge_validation_for_non_cuad_categories(tmp_path: Path) -> None:
    eval_path = tmp_path / "custom.jsonl"
    examples = [
        EvalExample(
            id=f"custom-v{i}",
            contract_excerpt=(
                "Section 2. Payment Terms. Invoices are due within thirty (30) days. "
                "Additional boilerplate text here."
            ),
            category="Payment Terms",
            present=True,
            gold_spans=["Invoices are due within thirty (30) days"],
            contract_title=f"Vendor-{i}",
        )
        for i in range(6)
    ]
    write_eval_set_jsonl(examples, eval_path)

    payload = run_validation(
        eval_path,
        sample_size=8,
        seed=0,
        client=RuleMirrorJudge(),
    )
    assert payload["agreement"]["cohens_kappa"] is not None
    assert payload["agreement"]["passes_threshold"] is True
    assert "Gold-span match" in payload["reference_rule"]

    exit_code = validate_and_exit(
        eval_path,
        sample_size=8,
        seed=0,
        client=RuleMirrorJudge(),
    )
    assert exit_code == 0


def test_reference_span_correct_with_custom_category() -> None:
    excerpt = "Buyer may recover pre-agreed damages of five thousand dollars."
    gold = ["pre-agreed damages of five thousand dollars"]
    assert reference_span_correct(gold[0], gold, excerpt)
