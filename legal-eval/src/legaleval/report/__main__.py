"""CLI for failure taxonomy reports."""

from __future__ import annotations

import argparse
from pathlib import Path

from legaleval.models.runner import project_root
from legaleval.report.errors import run_error_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate per-model failure taxonomy markdown reports.",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--eval-set", required=True, type=Path)
    parser.add_argument(
        "--worst-per-bucket",
        type=int,
        default=10,
        help="Number of worst examples per error bucket (default: 10).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    eval_set = args.eval_set
    if not eval_set.is_absolute():
        eval_set = project_root() / eval_set
    if not eval_set.exists():
        parser.error(f"Eval set not found: {eval_set}")

    summary = run_error_reports(
        args.run_id,
        eval_set,
        worst_per_bucket=args.worst_per_bucket,
    )
    for model, data in summary["models"].items():
        print(
            f"  {model}: {data['total_errors']} errors -> {data['report_path']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
