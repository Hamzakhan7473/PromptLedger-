"""CLI for calibration analysis."""

from __future__ import annotations

import argparse
from pathlib import Path

from legaleval.calibration.run import run_calibration, write_ece_json
from legaleval.models.runner import project_root


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute presence calibration (ECE) and reliability curves.",
    )
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--eval-set", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    eval_set = args.eval_set
    if not eval_set.is_absolute():
        eval_set = project_root() / eval_set
    if not eval_set.exists():
        parser.error(f"Eval set not found: {eval_set}")

    payload = run_calibration(args.run_id, eval_set)
    ece_path = write_ece_json(payload)
    print(f"Wrote ECE summary to {ece_path}")
    for model, data in payload["models"].items():
        print(f"  {model}: ECE={data['ece']:.4f} -> {data['plot_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
