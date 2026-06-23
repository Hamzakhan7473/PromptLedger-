"""CLI entrypoint for running eval sets against configured models."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from legaleval.models.runner import project_root, run_eval


def _default_run_id() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{uuid4().hex[:8]}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run legal-eval examples against configured LLM providers.",
    )
    parser.add_argument(
        "--models",
        required=True,
        help='Comma-separated model keys from models.yaml, or "all".',
    )
    parser.add_argument(
        "--eval-set",
        required=True,
        type=Path,
        help="Path to eval_set.jsonl.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Run identifier for results/<run_id>/raw/ (default: timestamp + uuid).",
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=None,
        help="Path to models.yaml (default: <project>/models.yaml).",
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

    models_config_path = args.models_config
    if models_config_path is not None and not models_config_path.is_absolute():
        models_config_path = project_root() / models_config_path

    run_id = args.run_id or _default_run_id()
    output_dir = run_eval(
        models=args.models,
        eval_set_path=eval_set_path,
        run_id=run_id,
        models_config_path=models_config_path,
    )
    print(f"Wrote raw results to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
