"""CLI for judge adjudication and validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from legaleval.judge.adjudicate import run_adjudication
from legaleval.judge.borderline import DEFAULT_GRAY_HIGH, DEFAULT_GRAY_LOW
from legaleval.judge.validate import DEFAULT_SAMPLE_SIZE, validate_and_exit
from legaleval.models.runner import project_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adjudicate borderline spans and validate judge trustworthiness.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    adjudicate = subparsers.add_parser(
        "adjudicate",
        help="Run judge on gray-zone TP-presence cases from a model run.",
    )
    adjudicate.add_argument("--run-id", required=True)
    adjudicate.add_argument("--eval-set", required=True, type=Path)
    adjudicate.add_argument(
        "--model",
        required=True,
        help="Evaluated model key whose predictions to adjudicate.",
    )
    adjudicate.add_argument("--gray-low", type=float, default=DEFAULT_GRAY_LOW)
    adjudicate.add_argument("--gray-high", type=float, default=DEFAULT_GRAY_HIGH)
    adjudicate.add_argument("--models-config", type=Path, default=None)

    validate = subparsers.add_parser(
        "validate",
        help="Validate judge against gold-span reference labels (fails if kappa < 0.6).",
    )
    validate.add_argument("--eval-set", required=True, type=Path)
    validate.add_argument("--sample-size", type=int, default=DEFAULT_SAMPLE_SIZE)
    validate.add_argument("--seed", type=int, default=42)
    validate.add_argument("--models-config", type=Path, default=None)

    return parser


def _resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "adjudicate":
        eval_set = _resolve_path(args.eval_set)
        if not eval_set.exists():
            parser.error(f"Eval set not found: {eval_set}")
        models_config = (
            _resolve_path(args.models_config) if args.models_config else None
        )
        decisions, output = run_adjudication(
            run_id=args.run_id,
            eval_set_path=eval_set,
            evaluated_model=args.model,
            gray_low=args.gray_low,
            gray_high=args.gray_high,
            models_config_path=models_config,
        )
        print(f"Adjudicated {len(decisions)} borderline cases -> {output}")
        return 0

    if args.command == "validate":
        eval_set = _resolve_path(args.eval_set)
        if not eval_set.exists():
            parser.error(f"Eval set not found: {eval_set}")
        models_config = (
            _resolve_path(args.models_config) if args.models_config else None
        )
        return validate_and_exit(
            eval_set,
            sample_size=args.sample_size,
            seed=args.seed,
            models_config_path=models_config,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
