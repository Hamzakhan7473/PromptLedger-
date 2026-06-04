from __future__ import annotations

import uuid
from typing import Any

from prompt_ledger.manifest import get_pin, load_manifest
from prompt_ledger.paths import repo_root
from prompt_ledger.registry import discover_registry, get_version
from prompt_ledger.render import format_retrieved_context, render_prompt
from prompt_ledger.scenarios import _load_fixture

from prompt_ledger.platform.environments import load_environments
from prompt_ledger.platform.models import Trajectory, TrajectoryStep
from prompt_ledger.platform.reward import compute_reward
from prompt_ledger.platform.router import select_model
from prompt_ledger.platform.tools import _FIXTURE_BY_PROMPT, execute_tool
from prompt_ledger.platform.trajectory_store import save_trajectory


def run_agent_task(
    environment: str,
    task: str,
    *,
    environment_name: str = "staging",
    cost_sensitive: bool = False,
    persist: bool = True,
) -> dict[str, Any]:
    """
    Agent orchestrator (demo): route model → run tools → render prompt → reward → store trajectory.
    Production path: API Gateway → this service → LLM providers (not called in stub mode).
    """
    envs = load_environments()
    if environment not in envs:
        raise KeyError(f"unknown environment {environment!r}")
    env = envs[environment]
    root = repo_root()

    route = select_model(env, cost_sensitive=cost_sensitive)
    manifest = load_manifest()
    ver = get_pin(manifest, environment_name, env.prompt_id) or "1.0.0"
    reg = discover_registry(root / "prompts" / "registry")
    pv = get_version(reg[env.prompt_id], ver)

    variables = _default_variables(env.prompt_id, task)
    retrieved = None
    rel = _FIXTURE_BY_PROMPT.get(env.prompt_id)
    if rel:
        retrieved = format_retrieved_context(_load_fixture((root / rel).resolve()))

    system_s, user_s = render_prompt(pv, retrieved_context=retrieved, variables=variables)
    prompt_text = f"SYSTEM:\n{system_s}\n\nUSER:\n{user_s}"

    steps: list[TrajectoryStep] = []
    for idx, tool_id in enumerate(env.tools):
        tc = execute_tool(tool_id, prompt_id=env.prompt_id, repo_root=root, task=task)
        steps.append(
            TrajectoryStep(
                step_index=idx,
                state={"task": task, "environment": environment},
                action=f"invoke_tool:{tool_id}",
                tool_calls=[tc],
                observation=tc.output,
                output=str(tc.output.get("preview", tc.output))[:400],
            ),
        )

    final_output = (
        f"[{route.model_key}] Task complete for {env.label}. "
        f"Grounded on {len(retrieved or '')} chars of context. "
        f"Policy pack: {env.pack_dir}."
    )

    traj = Trajectory(
        id=str(uuid.uuid4()),
        environment=environment,
        prompt_id=env.prompt_id,
        prompt_version=ver,
        model=route.model_key,
        task=task,
        prompt_text=prompt_text,
        steps=steps,
        final_output=final_output,
        metadata={
            "provider": route.provider,
            "model_id": route.model_id,
            "demo_vertical": env.demo_vertical,
            "stub_llm": True,
        },
    )
    traj.reward = compute_reward(traj, env)

    if persist:
        save_trajectory(traj)

    return {
        "trajectory_id": traj.id,
        "environment": environment,
        "model": route.model_key,
        "provider": route.provider,
        "prompt_id": env.prompt_id,
        "prompt_version": ver,
        "tools_invoked": env.tools,
        "final_output": final_output,
        "reward": traj.reward.to_dict(),
        "trajectory": traj.to_dict(),
    }


def _default_variables(prompt_id: str, task: str) -> dict[str, str]:
    defaults = {
        "legal.contract_review": {"clause_text": task[:500]},
        "finance.transaction_classification": {
            "transaction_json": '{"merchant":"Demo","amount_usd":100}',
        },
        "healthcare.clinical_guidance": {"clinical_question": task[:500]},
        "general.policy_support": {"customer_question": task[:500]},
    }
    return defaults.get(prompt_id, {"task": task[:500]})
