"""End-to-end eval pipeline orchestration."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from legaleval.calibration.run import run_calibration, write_ece_json
from legaleval.data.cuad import DEFAULT_SEED as EVAL_SET_SEED, build_eval_set
from legaleval.data.schema import write_eval_set_jsonl
from legaleval.judge.adjudicate import run_adjudication
from legaleval.judge.validate import (
    DEFAULT_SAMPLE_SIZE,
    MIN_KAPPA,
    run_validation,
    write_validation,
)
from legaleval.manifest import build_manifest, write_manifest
from legaleval.metrics.compute import (
    DEFAULT_BOOTSTRAP_N,
    compute_run_metrics,
    write_metrics_json,
)
from legaleval.metrics.compute import load_raw_run
from legaleval.models.runner import load_models_config, run_eval
from legaleval.paths import (
    default_eval_set_path,
    latest_run_link,
    models_config_path,
    run_calibration_dir,
    run_errors_dir,
    run_errors_summary_path,
    run_judge_dir,
    run_judge_validation_path,
    run_manifest_path,
    run_metrics_path,
    run_raw_dir,
    run_report_path,
    run_root,
)
from legaleval.report.errors import run_error_reports
from legaleval.report.generate import write_report

PIPELINE_BOOTSTRAP_SEED = 42
PIPELINE_JUDGE_SEED = 42

RunMode = Literal["eval", "agent"]


def generate_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{uuid4().hex[:8]}"


class EvalSetNotFoundError(FileNotFoundError):
    """Raised when no eval set exists and CUAD auto-build was not requested."""


def ensure_eval_set(
    eval_set_path: Path,
    *,
    rebuild: bool = False,
    build_cuad_if_missing: bool = False,
    seed: int = EVAL_SET_SEED,
) -> Path:
    if rebuild:
        examples = build_eval_set(seed=seed)
        write_eval_set_jsonl(examples, eval_set_path)
        return eval_set_path

    if eval_set_path.exists():
        return eval_set_path

    if build_cuad_if_missing:
        examples = build_eval_set(seed=seed)
        write_eval_set_jsonl(examples, eval_set_path)
        return eval_set_path

    raise EvalSetNotFoundError(
        f"No eval set found at {eval_set_path}. "
        "Provide --eval-set PATH to your JSONL file, run "
        "`python -m legaleval.data.cuad` to build a CUAD sample, or pass "
        "--build-cuad-if-missing to download and sample CUAD automatically."
    )


def run_pipeline(
    *,
    run_id: str | None = None,
    eval_set_path: Path | None = None,
    models: str = "all",
    mode: RunMode = "eval",
    rebuild_eval_set: bool = False,
    build_cuad_if_missing: bool = False,
    skip_judge_validate: bool = False,
    models_config: Path | None = None,
    dataset_name: str | None = None,
) -> dict[str, Any]:
    run_id = run_id or generate_run_id()
    eval_set_path = eval_set_path or default_eval_set_path()
    config_path = models_config or models_config_path()
    run_date = datetime.now(UTC).isoformat()

    run_root(run_id).mkdir(parents=True, exist_ok=True)
    steps: list[str] = []

    # 1. Data
    ensure_eval_set(
        eval_set_path,
        rebuild=rebuild_eval_set,
        build_cuad_if_missing=build_cuad_if_missing,
        seed=EVAL_SET_SEED,
    )
    steps.append("data")
    eval_set_label = dataset_name or eval_set_path.name

    # 2. Models (direct eval or Deep Agents harness)
    if mode == "agent":
        from legaleval.agents.runner import run_agent_eval

        run_agent_eval(
            models=models,
            eval_set_path=eval_set_path,
            run_id=run_id,
            models_config_path=config_path,
        )
        steps.append("agent_models")
    else:
        run_eval(
            models=models,
            eval_set_path=eval_set_path,
            run_id=run_id,
            models_config_path=config_path,
        )
        steps.append("models")

    # 3. Metrics
    metrics = compute_run_metrics(
        run_id,
        eval_set_path,
        n_bootstrap=DEFAULT_BOOTSTRAP_N,
        seed=PIPELINE_BOOTSTRAP_SEED,
    )
    write_metrics_json(metrics, run_metrics_path(run_id))
    steps.append("metrics")

    # 4. Judge adjudication (all models in raw run)
    raw_by_model = load_raw_run(run_id)
    for model_name in sorted(raw_by_model):
        run_adjudication(
            run_id=run_id,
            eval_set_path=eval_set_path,
            evaluated_model=model_name,
            models_config_path=config_path,
            output_dir=run_judge_dir(run_id),
        )
    steps.append("judge_adjudicate")

    # 5. Judge validation
    validation = run_validation(
        eval_set_path,
        sample_size=DEFAULT_SAMPLE_SIZE,
        seed=PIPELINE_JUDGE_SEED,
        models_config_path=config_path,
    )
    write_validation(validation, run_judge_validation_path(run_id))
    steps.append("judge_validate")

    kappa = validation["agreement"].get("cohens_kappa")
    if not skip_judge_validate and (
        kappa is None or kappa < MIN_KAPPA
    ):
        _fail_judge_validation(kappa)

    # 6. Calibration
    calibration = run_calibration(
        run_id,
        eval_set_path,
        output_dir=run_calibration_dir(run_id),
    )
    write_ece_json(calibration, run_calibration_dir(run_id) / "ece.json")
    steps.append("calibration")

    # 7. Errors
    errors_summary = run_error_reports(
        run_id,
        eval_set_path,
        output_dir=run_errors_dir(run_id),
    )
    summary_path = run_errors_summary_path(run_id)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(errors_summary, handle, indent=2)
        handle.write("\n")
    steps.append("errors")

    # 8. Manifest
    manifest = build_manifest(
        run_id=run_id,
        run_date_utc=run_date,
        eval_set_path=eval_set_path,
        seeds={
            "eval_set": EVAL_SET_SEED,
            "bootstrap": PIPELINE_BOOTSTRAP_SEED,
            "judge_validation": PIPELINE_JUDGE_SEED,
        },
        steps_completed=steps,
        models_config=config_path,
        extra={
            "models_run": models,
            "mode": mode,
            "eval_set_label": eval_set_label,
            "judge_validation": {
                "cohens_kappa": kappa,
                "passes_threshold": validation["agreement"].get("passes_threshold"),
            },
        },
    )
    write_manifest(manifest, run_manifest_path(run_id))

    # 9. Report
    report_path = write_report(
        run_id,
        eval_set_path=eval_set_path,
        dataset_name=eval_set_label,
    )
    steps.append("report")

    # Latest symlink
    link = latest_run_link()
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(run_id)

    return {
        "run_id": run_id,
        "run_root": str(run_root(run_id)),
        "report_path": str(report_path),
        "manifest_path": str(run_manifest_path(run_id)),
        "steps_completed": steps,
        "judge_kappa": kappa,
    }


def _fail_judge_validation(kappa: float | None) -> None:
    border = "=" * 72
    print(f"\n{border}\nPIPELINE ABORTED: JUDGE VALIDATION FAILED\n{border}", file=sys.stderr)
    if kappa is None:
        print(
            "Judge produced no scored decisions. Cannot generate a trustworthy report.",
            file=sys.stderr,
        )
    else:
        print(
            f"Cohen's kappa {kappa:.4f} < {MIN_KAPPA}. "
            "Fix the judge model/prompt and re-run.",
            file=sys.stderr,
        )
    print(f"{border}\n", file=sys.stderr)
    raise SystemExit(1)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the full legal-eval pipeline.")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--eval-set", type=Path, default=None)
    parser.add_argument("--models", default="all")
    parser.add_argument(
        "--mode",
        choices=("eval", "agent"),
        default="eval",
        help="eval = direct model calls; agent = Deep Agents harness",
    )
    parser.add_argument(
        "--rebuild-eval-set",
        action="store_true",
        help="Download CUAD and overwrite the eval set at --eval-set (or default path).",
    )
    parser.add_argument(
        "--build-cuad-if-missing",
        action="store_true",
        help="If the eval set file is missing, download CUAD and build a balanced sample.",
    )
    parser.add_argument("--skip-judge-validate", action="store_true")
    parser.add_argument("--models-config", type=Path, default=None)
    args = parser.parse_args(argv)

    result = run_pipeline(
        run_id=args.run_id,
        eval_set_path=args.eval_set,
        models=args.models,
        mode=args.mode,
        rebuild_eval_set=args.rebuild_eval_set,
        build_cuad_if_missing=args.build_cuad_if_missing,
        skip_judge_validate=args.skip_judge_validate,
        models_config=args.models_config,
    )
    print(f"Run complete: {result['run_id']}")
    print(f"  Report:   {result['report_path']}")
    print(f"  Manifest: {result['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
