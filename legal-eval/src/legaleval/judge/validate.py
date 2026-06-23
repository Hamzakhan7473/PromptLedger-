"""Validate judge trustworthiness against CUAD gold-span reference labels.

Why an unvalidated judge invalidates the eval
--------------------------------------------

The judge is used ONLY for borderline span cases (token Jaccard in a gray zone)
where automatic overlap metrics are ambiguous. If the judge disagrees systematically
with the CUAD gold-span reference, then:

1. **Span grounding numbers become uninterpretable** — adjudicated cases would be
   relabeled using a standard that does not align with the dataset's human annotations.
2. **Cross-model comparisons are biased** — models with different error profiles will
   be unevenly re-scored depending on how often they land in the gray zone.
3. **Reported confidence is false** — downstream metrics that incorporate judge
   decisions would imply human-grade adjudication without empirical support.

Cohen's kappa below 0.6 indicates only slight-to-moderate agreement with the CUAD
reference — insufficient for a frontier-grade eval. The pipeline MUST fail loudly
rather than silently reporting judge-adjusted results that cannot be trusted.

Run validation before trusting any judge-mediated span scores::

    python -m legaleval.judge validate --eval-set data/eval_set.jsonl
"""

from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sklearn.metrics import cohen_kappa_score

from legaleval.data.cuad import EvalExample, read_eval_set_jsonl
from legaleval.judge.adjudicate import adjudicate_case
from legaleval.judge.borderline import BorderlineCase, primary_gold_span
from legaleval.judge.config import load_judge_config
from legaleval.metrics.span import best_gold_jaccard, span_in_contract
from legaleval.paths import project_root, run_judge_validation_path

DEFAULT_SAMPLE_SIZE = 60
DEFAULT_REFERENCE_JACCARD_THRESHOLD = 0.7
MIN_KAPPA = 0.6


@dataclass(frozen=True)
class ValidationCase:
    example_id: str
    category: str
    contract_excerpt: str
    gold_spans: list[str]
    predicted_span: str
    token_jaccard: float
    reference_span_correct: bool
    stratum: str


@dataclass(frozen=True)
class ValidationResult:
    example_id: str
    category: str
    token_jaccard: float
    reference_span_correct: bool
    judge_span_correct: bool | None
    judge_rationale: str | None
    agrees_with_reference: bool | None
    stratum: str
    error: str | None = None
    parse_error: str | None = None


def validation_output_path(run_id: str | None = None) -> Path:
    if run_id is None:
        return project_root() / "results" / "judge" / "validation.json"
    return run_judge_validation_path(run_id)


def cuad_reference_span_correct(
    predicted_span: str,
    gold_spans: list[str],
    contract_excerpt: str,
    *,
    jaccard_threshold: float = DEFAULT_REFERENCE_JACCARD_THRESHOLD,
) -> bool:
    """CUAD gold-span match proxy used as the human reference for validation."""
    if not predicted_span or not span_in_contract(predicted_span, contract_excerpt):
        return False
    return best_gold_jaccard(predicted_span, gold_spans) >= jaccard_threshold


def _truncate_span(span: str, fraction: float) -> str:
    start = int(len(span) * (1 - fraction) / 2)
    end = int(len(span) * (1 + fraction) / 2)
    return span[start:end].strip() or span


def _wrong_span_from_excerpt(excerpt: str, gold_spans: list[str]) -> str:
    words = excerpt.split()
    if len(words) >= 6:
        candidate = " ".join(words[:6])
        if best_gold_jaccard(candidate, gold_spans) < DEFAULT_REFERENCE_JACCARD_THRESHOLD:
            return candidate
    return excerpt[: min(80, len(excerpt))]


def build_validation_pool(examples: list[EvalExample]) -> list[ValidationCase]:
    """Build stratified validation candidates with known CUAD reference labels."""
    pool: list[ValidationCase] = []
    for example in examples:
        if not example.present or not example.gold_spans:
            continue
        gold = primary_gold_span(example.gold_spans)
        excerpt = example.contract_excerpt

        variants: list[tuple[str, str]] = [
            ("high_overlap", _truncate_span(gold, 0.15)),
            ("gray_partial", _truncate_span(gold, 0.45)),
            ("low_overlap", _wrong_span_from_excerpt(excerpt, example.gold_spans)),
        ]
        if gold in excerpt:
            variants.append(("exact_gold", gold))

        for stratum, predicted in variants:
            if not predicted:
                continue
            jaccard = best_gold_jaccard(predicted, example.gold_spans)
            reference = cuad_reference_span_correct(
                predicted, example.gold_spans, excerpt
            )
            pool.append(
                ValidationCase(
                    example_id=example.id,
                    category=example.category,
                    contract_excerpt=excerpt,
                    gold_spans=list(example.gold_spans),
                    predicted_span=predicted,
                    token_jaccard=round(jaccard, 6),
                    reference_span_correct=reference,
                    stratum=stratum,
                )
            )
    return pool


def stratified_sample(
    pool: list[ValidationCase],
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    seed: int = 42,
) -> list[ValidationCase]:
    """Sample evenly across (category, reference_label, stratum) buckets."""
    if not pool:
        raise ValueError("Validation pool is empty")
    if sample_size >= len(pool):
        return list(pool)

    buckets: dict[tuple[str, bool, str], list[ValidationCase]] = defaultdict(list)
    for case in pool:
        key = (case.category, case.reference_span_correct, case.stratum)
        buckets[key].append(case)

    rng = random.Random(seed)
    for bucket in buckets.values():
        rng.shuffle(bucket)

    selected: list[ValidationCase] = []
    bucket_keys = sorted(buckets)
    rng.shuffle(bucket_keys)

    while len(selected) < sample_size:
        added = False
        for key in bucket_keys:
            if buckets[key]:
                selected.append(buckets[key].pop())
                added = True
                if len(selected) >= sample_size:
                    break
        if not added:
            break
    return selected


def run_judge_on_validation_case(
    client: ModelClient,
    case: ValidationCase,
) -> ValidationResult:
    borderline = BorderlineCase(
        example_id=case.example_id,
        category=case.category,
        contract_excerpt=case.contract_excerpt,
        contract_title="",
        gold_spans=case.gold_spans,
        predicted_span=case.predicted_span,
        token_jaccard=case.token_jaccard,
        model="validation",
    )
    decision = adjudicate_case(client, borderline, run_id="validation")
    agrees: bool | None = None
    if decision.span_correct is not None:
        agrees = decision.span_correct == case.reference_span_correct
    return ValidationResult(
        example_id=case.example_id,
        category=case.category,
        token_jaccard=case.token_jaccard,
        reference_span_correct=case.reference_span_correct,
        judge_span_correct=decision.span_correct,
        judge_rationale=decision.rationale,
        agrees_with_reference=agrees,
        stratum=case.stratum,
        error=decision.error,
        parse_error=decision.parse_error,
    )


def compute_agreement(results: list[ValidationResult]) -> dict[str, Any]:
    scored = [row for row in results if row.judge_span_correct is not None]
    if not scored:
        return {
            "n_sampled": len(results),
            "n_scored": 0,
            "accuracy": None,
            "cohens_kappa": None,
            "passes_threshold": False,
        }

    reference = [row.reference_span_correct for row in scored]
    judge = [bool(row.judge_span_correct) for row in scored]
    accuracy = sum(r == j for r, j in zip(reference, judge, strict=True)) / len(scored)
    kappa = float(cohen_kappa_score(reference, judge))

    return {
        "n_sampled": len(results),
        "n_scored": len(scored),
        "n_errors": len(results) - len(scored),
        "accuracy": round(accuracy, 6),
        "cohens_kappa": round(kappa, 6),
        "min_kappa_required": MIN_KAPPA,
        "passes_threshold": kappa >= MIN_KAPPA,
    }


def run_validation(
    eval_set_path: Path,
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    seed: int = 42,
    models_config_path: Path | None = None,
    client: ModelClient | None = None,
) -> dict[str, Any]:
    examples = read_eval_set_jsonl(eval_set_path)
    pool = build_validation_pool(examples)
    sample = stratified_sample(pool, sample_size=sample_size, seed=seed)

    own_client = client is None
    if client is None:
        judge_config = load_judge_config(models_config_path)
        client = create_client(judge_config)

    results: list[ValidationResult] = []
    try:
        for case in sample:
            results.append(run_judge_on_validation_case(client, case))
    finally:
        if own_client:
            client.close()

    agreement = compute_agreement(results)
    payload: dict[str, Any] = {
        "sample_size": sample_size,
        "seed": seed,
        "reference_rule": (
            f"CUAD gold-span match: span in contract AND "
            f"token Jaccard >= {DEFAULT_REFERENCE_JACCARD_THRESHOLD}"
        ),
        "agreement": agreement,
        "cases": [
            {
                "example_id": row.example_id,
                "category": row.category,
                "stratum": row.stratum,
                "token_jaccard": row.token_jaccard,
                "reference_span_correct": row.reference_span_correct,
                "judge_span_correct": row.judge_span_correct,
                "agrees_with_reference": row.agrees_with_reference,
                "error": row.error,
                "parse_error": row.parse_error,
            }
            for row in results
        ],
    }
    return payload


def write_validation(
    payload: dict[str, Any], output_path: Path | None = None, *, run_id: str | None = None
) -> Path:
    path = output_path or validation_output_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    return path


def validate_and_exit(
    eval_set_path: Path,
    *,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    seed: int = 42,
    models_config_path: Path | None = None,
    client: ModelClient | None = None,
) -> int:
    """Run validation, write results, return 0 on pass or 1 if kappa < MIN_KAPPA."""
    payload = run_validation(
        eval_set_path,
        sample_size=sample_size,
        seed=seed,
        models_config_path=models_config_path,
        client=client,
    )
    output_path = write_validation(payload)
    agreement = payload["agreement"]
    kappa = agreement.get("cohens_kappa")

    print(f"Wrote judge validation to {output_path}")
    print(f"  accuracy:      {agreement.get('accuracy')}")
    print(f"  Cohen's kappa: {kappa}")
    print(f"  threshold:     {MIN_KAPPA}")

    if kappa is None:
        _fail_loudly(
            "Judge validation FAILED: no scored decisions (all API/parse errors). "
            "Cannot trust judge for span adjudication."
        )
        return 1

    if kappa < MIN_KAPPA:
        _fail_loudly(
            f"Judge validation FAILED: Cohen's kappa {kappa:.4f} < {MIN_KAPPA}. "
            "The judge is not trustworthy enough to report. "
            "Do NOT use judge-mediated span scores in eval results. "
            "Re-pin the judge model or revise the judge prompt, then re-run validation."
        )
        return 1

    print("Judge validation PASSED.")
    return 0


def _fail_loudly(message: str) -> None:
    border = "=" * 72
    print(f"\n{border}\nJUDGE VALIDATION FAILURE\n{border}", file=sys.stderr)
    print(message, file=sys.stderr)
    print(f"{border}\n", file=sys.stderr)
