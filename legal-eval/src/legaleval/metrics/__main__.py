"""Compute and report eval metrics from raw model run logs."""

from __future__ import annotations

import argparse
from pathlib import Path

from legaleval.metrics.compute import DEFAULT_BOOTSTRAP_N, run_metrics
from legaleval.models.runner import project_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute presence, span-grounding, and reliability metrics.",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run identifier matching results/<run_id>/.",
    )
    parser.add_argument(
        "--eval-set",
        required=True,
        type=Path,
        help="Path to eval_set.jsonl with gold labels.",
    )
    parser.add_argument(
        "--bootstrap",
        type=int,
        default=DEFAULT_BOOTSTRAP_N,
        help=f"Bootstrap resamples for 95%% CIs (default: {DEFAULT_BOOTSTRAP_N}).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for bootstrap resampling.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    eval_set_path = args.eval_set
    if not eval_set_path.is_absolute():
        eval_set_path = project_root() / eval_set_path
    if not eval_set_path.exists():
        parser.error(f"Eval set not found: {eval_set_path}")

    _, output_path = run_metrics(
        args.run_id,
        eval_set_path,
        n_bootstrap=args.bootstrap,
        seed=args.seed,
    )
    print(f"\nWrote metrics to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
