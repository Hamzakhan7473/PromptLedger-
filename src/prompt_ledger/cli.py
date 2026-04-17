from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from prompt_ledger.audit import run_audit
from prompt_ledger.optimization import OptimizationEvent, emit_optimization_event
from prompt_ledger.paths import manifest_path, repo_root
from prompt_ledger.promote import promote_environment
from prompt_ledger.scenarios import run_all_scenarios, run_scenario_file

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.command()
def audit(
    registry: Path | None = typer.Option(
        None,
        help="Registry root (defaults to prompts/registry)",
    ),
) -> None:
    """Run static governance audits on all prompt packs."""

    root = repo_root()
    reg = registry or (root / "prompts" / "registry")
    findings = run_audit(registry_root=reg)
    if not findings:
        console.print("[green]Audit passed: no findings.[/green]")
        raise typer.Exit(0)

    table = Table(title="Audit findings")
    table.add_column("Severity")
    table.add_column("Prompt")
    table.add_column("Version")
    table.add_column("Code")
    table.add_column("Message")
    for f in findings:
        table.add_row(f.severity, f.prompt_id, f.version, f.code, f.message)
    console.print(table)
    raise typer.Exit(1)


@app.command()
def test(
    scenarios_dir: Path | None = typer.Option(
        None,
        help="Directory of scenario YAML files",
    ),
) -> None:
    """Run render/grounding scenarios (correctness-first checks without live LLM calls)."""

    root = repo_root()
    sdir = scenarios_dir or (root / "tests" / "scenarios")
    results = run_all_scenarios(sdir)
    failed = [r for r in results if not r.ok]
    for r in results:
        if r.ok:
            console.print(f"[green]OK[/green]  {r.scenario_id}")
        else:
            console.print(f"[red]FAIL[/red] {r.scenario_id}")
            for err in r.errors:
                console.print(f"  - {err}")
    if failed:
        raise typer.Exit(1)
    console.print(f"[green]All {len(results)} scenario(s) passed.[/green]")


@app.command("test-one")
def test_one(
    scenario: Path = typer.Argument(..., exists=True, readable=True),
) -> None:
    """Run a single scenario file."""

    res = run_scenario_file(scenario)
    if res.ok:
        console.print(f"[green]OK[/green] {res.scenario_id}")
        raise typer.Exit(0)
    console.print(f"[red]FAIL[/red] {res.scenario_id}")
    for err in res.errors:
        console.print(f"  - {err}")
    raise typer.Exit(1)


@app.command()
def promote(
    environment: str = typer.Option(
        "production",
        "--environment",
        "-e",
        help="Environment block in prompts/manifest.yaml to update",
    ),
    sync_from: str = typer.Option(
        "staging",
        "--sync-from",
        help="Copy pins from this environment (e.g. staging -> production)",
    ),
    manifest: Path | None = typer.Option(
        None,
        help="Override manifest path",
    ),
    notify_optimization_api: bool = typer.Option(
        False,
        help="If PROMPT_OPTIMIZATION_API_URL is set, emit a promotion event",
    ),
) -> None:
    """Promote prompt pins (typically run from CI on the default branch)."""

    data = promote_environment(
        target=environment,
        sync_from=sync_from,
        manifest=manifest,
    )
    console.print(f"[green]Updated[/green] {manifest or manifest_path()}")
    if notify_optimization_api:
        envs = data.get("environments", {})
        pins = envs.get(environment, {})
        for prompt_id, version in pins.items():
            emit_optimization_event(
                OptimizationEvent(
                    prompt_id=prompt_id,
                    version=str(version),
                    environment=environment,
                    metrics={"event": "promote", "sync_from": sync_from},
                )
            )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
