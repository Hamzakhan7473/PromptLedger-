from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from prompt_ledger.platform.dataset import build_rl_datasets
from prompt_ledger.platform.environments import list_environments
from prompt_ledger.platform.evaluation import evaluate_trajectories
from prompt_ledger.platform.observability import observability_stack
from prompt_ledger.platform.orchestrator import run_agent_task
from prompt_ledger.platform.router import list_models
from prompt_ledger.platform.tools import list_tools
from prompt_ledger.platform.trajectory_store import get_trajectory, list_trajectories

agent_app = typer.Typer(help="Agent orchestrator, trajectories, and RL datasets")
console = Console()


def _emit_json(data: Any) -> None:
    typer.echo(json.dumps(data, indent=2, default=str))


@agent_app.command("list-envs")
def agent_list_envs(json_out: bool = typer.Option(False, "--json")) -> None:
    """List RL environments (tax, legal, financial modeling, contract review, research)."""
    envs = list_environments()
    if json_out:
        _emit_json({"environments": envs})
        return
    table = Table(title="RL environments")
    table.add_column("ID")
    table.add_column("Label")
    table.add_column("Prompt")
    for e in envs:
        table.add_row(e["id"], e["label"], e["prompt_id"])
    console.print(table)


@agent_app.command("list-tools")
def agent_list_tools(json_out: bool = typer.Option(False, "--json")) -> None:
    tools = list_tools()
    if json_out:
        _emit_json({"tools": tools})
        return
    for t in tools:
        console.print(f"[cyan]{t['id']}[/cyan] — {t['label']} ({t['backend']})")


@agent_app.command("list-models")
def agent_list_models(json_out: bool = typer.Option(False, "--json")) -> None:
    models = list_models()
    if json_out:
        _emit_json({"models": models})
        return
    for m in models:
        console.print(f"{m['id']}: {m.get('provider')} / {m.get('model_id')}")


@agent_app.command("run")
def agent_run(
    env: str = typer.Option(..., "--env", "-e", help="Environment id"),
    task: str = typer.Option(..., "--task", "-t", help="User task / query"),
    cost_sensitive: bool = typer.Option(False, "--cost-sensitive"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    """Run agent orchestrator: tools → prompt render → reward → trajectory store."""
    try:
        result = run_agent_task(env, task, cost_sensitive=cost_sensitive)
    except KeyError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1) from e
    if json_out:
        _emit_json(result)
        return
    console.print(f"[green]Trajectory[/green] {result['trajectory_id']}")
    console.print(f"Model: {result['model']} ({result['provider']})")
    console.print(f"Reward: {result['reward']['total']}")
    console.print(result["final_output"][:300])


@agent_app.command("trajectories")
def agent_trajectories(
    env: str | None = typer.Option(None, "--env"),
    limit: int = typer.Option(20, "--limit"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    rows = list_trajectories(environment=env, limit=limit)
    if json_out:
        _emit_json({"trajectories": rows})
        return
    if not rows:
        console.print("No trajectories yet. Run: prompt-ledger agent run ...")
        return
    table = Table(title="Trajectories")
    table.add_column("ID")
    table.add_column("Env")
    table.add_column("Reward")
    table.add_column("Task")
    for r in rows:
        table.add_row(r["id"][:8], r["environment"], str(r["reward_total"]), r["task"][:40])
    console.print(table)


@agent_app.command("show")
def agent_show(
    trajectory_id: str = typer.Argument(...),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    data = get_trajectory(trajectory_id)
    if not data:
        console.print("[red]Not found[/red]")
        raise typer.Exit(1)
    if json_out:
        _emit_json(data)
        return
    console.print_json(data=data)


@agent_app.command("evaluate")
def agent_evaluate(
    env: str | None = typer.Option(None, "--env"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    metrics = evaluate_trajectories(environment=env)
    if json_out:
        _emit_json(metrics)
        return
    console.print(f"Runs: {metrics['count']}")
    console.print(f"Success rate: {metrics['success_rate']}")
    console.print(f"Average reward: {metrics['average_reward']}")


@agent_app.command("datasets")
def agent_datasets(
    env: str | None = typer.Option(None, "--env"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    result = build_rl_datasets(environment=env)
    if json_out:
        _emit_json(result)
        return
    console.print(f"[green]Datasets written to[/green] {result['output_dir']}")
    for name, path in result["files"].items():
        console.print(f"  {name}: {path}")


@agent_app.command("observability")
def agent_observability(json_out: bool = typer.Option(False, "--json")) -> None:
    stack = observability_stack()
    if json_out:
        _emit_json(stack)
        return
    console.print_json(data=stack)
