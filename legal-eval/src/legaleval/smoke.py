"""Pre-flight smoke test: first N eval examples against every configured model."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean
from typing import TextIO

from legaleval.data.schema import EvalExample, read_eval_set_jsonl
from legaleval.models.runner import (
    CallLogRow,
    ModelClient,
    ModelConfig,
    create_client,
    execute_example,
    load_models_config,
    resolve_model_names,
)
from legaleval.paths import default_eval_set_path, models_config_path, project_root

SMOKE_EXAMPLE_LIMIT = 3
SMOKE_RUN_ID = "smoke"


@dataclass(frozen=True)
class SmokeExampleOutcome:
    example_id: str
    row: CallLogRow

    @property
    def parse_ok(self) -> bool:
        return (
            self.row.error is None
            and self.row.parse_error is None
            and self.row.parsed is not None
        )

    @property
    def parsed_fields(self) -> dict[str, object] | None:
        if self.row.parsed is None:
            return None
        return {
            "present": self.row.parsed["present"],
            "span": self.row.parsed["span"],
            "confidence": self.row.parsed["confidence"],
        }

    @property
    def issue(self) -> str | None:
        if self.parse_ok:
            return None
        if self.row.error:
            return self.row.error
        if self.row.parse_error:
            return f"parse_error: {self.row.parse_error}"
        return "no parsed output"


@dataclass
class SmokeModelOutcome:
    model_name: str
    config: ModelConfig
    outcomes: list[SmokeExampleOutcome] = field(default_factory=list)
    client_error: str | None = None

    @property
    def parse_ok_count(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.parse_ok)

    @property
    def mean_latency_ms(self) -> float | None:
        latencies = [
            outcome.row.latency_ms
            for outcome in self.outcomes
            if outcome.row.latency_ms is not None
        ]
        if not latencies:
            return None
        return round(mean(latencies), 1)

    @property
    def passed(self) -> bool:
        return self.parse_ok_count > 0


def is_parse_ok(row: CallLogRow) -> bool:
    return row.error is None and row.parse_error is None and row.parsed is not None


def run_smoke_model(
    config: ModelConfig,
    examples: list[EvalExample],
    *,
    run_id: str = SMOKE_RUN_ID,
    client_factory=create_client,
    executor=execute_example,
) -> SmokeModelOutcome:
    result = SmokeModelOutcome(model_name=config.name, config=config)
    try:
        client: ModelClient = client_factory(config)
    except Exception as exc:  # noqa: BLE001
        result.client_error = f"{type(exc).__name__}: {exc}"
        for example in examples:
            result.outcomes.append(
                SmokeExampleOutcome(
                    example_id=example.id,
                    row=CallLogRow(
                        run_id=run_id,
                        example_id=example.id,
                        category=example.category,
                        contract_title=example.contract_title,
                        provider=config.provider,
                        model=config.name,
                        model_id=config.model_id,
                        error=result.client_error,
                    ),
                )
            )
        return result

    try:
        for example in examples:
            row = executor(client, example, run_id=run_id)
            result.outcomes.append(
                SmokeExampleOutcome(example_id=example.id, row=row)
            )
    finally:
        client.close()
    return result


def run_smoke(
    *,
    examples: list[EvalExample],
    configs: dict[str, ModelConfig],
    run_id: str = SMOKE_RUN_ID,
    client_factory=create_client,
    executor=execute_example,
) -> list[SmokeModelOutcome]:
    return [
        run_smoke_model(
            configs[name],
            examples,
            run_id=run_id,
            client_factory=client_factory,
            executor=executor,
        )
        for name in sorted(configs)
    ]


def _format_parsed(fields: dict[str, object] | None) -> str:
    if fields is None:
        return "—"
    return json.dumps(fields, ensure_ascii=False)


def _format_issue(issue: str | None, max_len: int = 72) -> str:
    if issue is None:
        return ""
    if len(issue) <= max_len:
        return issue
    return issue[: max_len - 1] + "…"


def render_smoke_report(
    results: list[SmokeModelOutcome],
    *,
    example_limit: int = SMOKE_EXAMPLE_LIMIT,
    stream: TextIO | None = None,
) -> None:
    import sys

    out = stream or sys.stdout
    model_count = len(results)
    print(
        f"legal-eval smoke test — first {example_limit} examples, "
        f"{model_count} model(s)",
        file=out,
    )
    print("=" * 72, file=out)

    for result in results:
        cfg = result.config
        print(file=out)
        print(f"MODEL: {result.model_name}", file=out)
        print(
            f"  provider_path={cfg.resolved_provider_path}  provider={cfg.provider}  "
            f"model_id={cfg.model_id}",
            file=out,
        )
        if cfg.region:
            print(f"  region={cfg.region}", file=out)
        print(
            f"  parse_ok: {result.parse_ok_count}/{example_limit}  "
            f"mean_latency_ms: {result.mean_latency_ms if result.mean_latency_ms is not None else '—'}",
            file=out,
        )
        if result.client_error:
            print(f"  client_error: {result.client_error}", file=out)

        print(
            f"  {'example_id':<14} {'ok':<4} {'latency_ms':>10}  parsed / issue",
            file=out,
        )
        print(f"  {'-' * 14} {'-' * 4} {'-' * 10}  {'-' * 34}", file=out)
        for outcome in result.outcomes:
            ok = "yes" if outcome.parse_ok else "no"
            latency = (
                f"{outcome.row.latency_ms:.1f}"
                if outcome.row.latency_ms is not None
                else "—"
            )
            detail = (
                _format_parsed(outcome.parsed_fields)
                if outcome.parse_ok
                else _format_issue(outcome.issue)
            )
            print(
                f"  {outcome.example_id:<14} {ok:<4} {latency:>10}  {detail}",
                file=out,
            )

    passed = [r.model_name for r in results if r.parse_ok_count == example_limit]
    partial = [
        r.model_name
        for r in results
        if 0 < r.parse_ok_count < example_limit
    ]
    failed = [r.model_name for r in results if r.parse_ok_count == 0]

    print(file=out)
    print("=" * 72, file=out)
    if passed:
        print(f"PASSED ({len(passed)}): {', '.join(passed)}", file=out)
    else:
        print("PASSED (0): none", file=out)
    if partial:
        print(f"PARTIAL ({len(partial)}): {', '.join(partial)}", file=out)
    if failed:
        print(f"NEEDS ATTENTION ({len(failed)}): {', '.join(failed)}", file=out)
    else:
        print("NEEDS ATTENTION (0): none", file=out)


def smoke_exit_code(
    results: list[SmokeModelOutcome],
    *,
    example_limit: int = SMOKE_EXAMPLE_LIMIT,
) -> int:
    if any(result.parse_ok_count == 0 for result in results):
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Pre-flight smoke test: run the first few eval examples against "
            "every model in models.yaml using real API clients."
        ),
    )
    parser.add_argument(
        "--eval-set",
        type=Path,
        default=None,
        help=f"Path to eval_set.jsonl (default: {default_eval_set_path()}).",
    )
    parser.add_argument(
        "--models",
        default="all",
        help='Comma-separated model keys from models.yaml, or "all" (default).',
    )
    parser.add_argument(
        "--models-config",
        type=Path,
        default=None,
        help=f"Path to models.yaml (default: {models_config_path()}).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=SMOKE_EXAMPLE_LIMIT,
        help=f"Number of eval examples to run (default: {SMOKE_EXAMPLE_LIMIT}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.limit < 1:
        parser.error("--limit must be at least 1")

    eval_set_path = args.eval_set or default_eval_set_path()
    if not eval_set_path.is_absolute():
        eval_set_path = project_root() / eval_set_path
    if not eval_set_path.exists():
        parser.error(f"Eval set not found: {eval_set_path}")

    config_path = args.models_config or models_config_path()
    if not config_path.is_absolute():
        config_path = project_root() / config_path
    if not config_path.exists():
        parser.error(f"models.yaml not found: {config_path}")

    examples = read_eval_set_jsonl(eval_set_path)[: args.limit]
    if not examples:
        parser.error(f"No examples in eval set: {eval_set_path}")

    configs = load_models_config(config_path)
    if not configs:
        parser.error(f"No models defined in {config_path}")

    try:
        selected = resolve_model_names(args.models, configs)
    except ValueError as exc:
        parser.error(str(exc))
    configs = {name: configs[name] for name in selected}

    results = run_smoke(examples=examples, configs=configs)
    render_smoke_report(results, example_limit=args.limit)
    return smoke_exit_code(results, example_limit=args.limit)


if __name__ == "__main__":
    raise SystemExit(main())
