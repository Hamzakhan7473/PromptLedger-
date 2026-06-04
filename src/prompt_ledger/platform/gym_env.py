from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from prompt_ledger.paths import repo_root
from prompt_ledger.platform.environments import RLEnvironment, load_environments
from prompt_ledger.platform.tools import execute_tool

_EPISODES: dict[str, dict[str, Any]] = {}


@dataclass
class EpisodeState:
    episode_id: str
    environment: str
    env_config: RLEnvironment
    step_index: int = 0
    done: bool = False
    history: list[dict[str, Any]] = field(default_factory=list)
    last_observation: dict[str, Any] = field(default_factory=dict)
    total_reward: float = 0.0


def reset(environment: str, *, seed: int | None = None) -> dict[str, Any]:
    """OpenAI Gym-style reset."""
    envs = load_environments()
    if environment not in envs:
        raise KeyError(f"unknown environment {environment!r}")
    env = envs[environment]
    episode_id = str(uuid.uuid4())
    obs = {
        "environment": environment,
        "label": env.label,
        "tools": env.tools,
        "task_slot": "awaiting_action",
        "seed": seed,
    }
    state = EpisodeState(
        episode_id=episode_id,
        environment=environment,
        env_config=env,
        last_observation=obs,
    )
    _EPISODES[episode_id] = {
        "state": state,
        "transitions": [],
    }
    return {
        "episode_id": episode_id,
        "observation": obs,
        "info": {"prompt_id": env.prompt_id, "pack_dir": env.pack_dir},
    }


def step(episode_id: str, action: str | dict[str, Any]) -> dict[str, Any]:
    """Execute one environment step; action is tool id or {tool, input}."""
    bucket = _EPISODES.get(episode_id)
    if not bucket:
        raise KeyError(f"unknown episode {episode_id!r}")
    state: EpisodeState = bucket["state"]
    if state.done:
        return _step_response(state, reward=0.0, terminated=True)

    if isinstance(action, dict):
        tool_id = str(action.get("tool") or action.get("action") or "")
        task = str(action.get("input") or action.get("task") or "")
    else:
        tool_id = str(action)
        task = f"step_{state.step_index}"

    if tool_id not in state.env_config.tools and tool_id != "finish":
        return _step_response(
            state,
            reward=-0.1,
            observation={"error": f"invalid action {tool_id}"},
            terminated=False,
        )

    root = repo_root()
    if tool_id == "finish":
        state.done = True
        obs = {"status": "finished", "steps": state.step_index}
        reward = 0.5
    else:
        tc = execute_tool(
            tool_id,
            prompt_id=state.env_config.prompt_id,
            repo_root=root,
            task=task,
        )
        obs = {"tool": tool_id, "output": tc.output, "latency_ms": tc.latency_ms}
        reward = 0.2 if tc.output.get("error") is None else 0.05
        state.history.append(
            {
                "step": state.step_index,
                "action": tool_id,
                "observation": obs,
            },
        )

    state.step_index += 1
    state.last_observation = obs
    state.total_reward += reward

    bucket["transitions"].append(
        {
            f"state_{state.step_index - 1}": {"step": state.step_index - 1},
            f"action_{state.step_index - 1}": tool_id if tool_id != "finish" else "finish",
            f"observation_{state.step_index - 1}": obs,
        },
    )

    terminated = state.done or state.step_index >= len(state.env_config.tools)
    if terminated and not state.done:
        state.done = True
    return _step_response(state, reward=reward, terminated=terminated)


def episode_reward(episode_id: str) -> dict[str, Any]:
    bucket = _EPISODES.get(episode_id)
    if not bucket:
        raise KeyError(f"unknown episode {episode_id!r}")
    state: EpisodeState = bucket["state"]
    return {"episode_id": episode_id, "reward": state.total_reward, "done": state.done}


def episode_done(episode_id: str) -> bool:
    bucket = _EPISODES.get(episode_id)
    if not bucket:
        raise KeyError(f"unknown episode {episode_id!r}")
    return bucket["state"].done


def get_episode_transitions(episode_id: str) -> list[dict[str, Any]]:
    bucket = _EPISODES.get(episode_id)
    if not bucket:
        raise KeyError(f"unknown episode {episode_id!r}")
    return bucket["transitions"]


def _step_response(
    state: EpisodeState,
    *,
    reward: float,
    observation: dict[str, Any] | None = None,
    terminated: bool,
) -> dict[str, Any]:
    return {
        "episode_id": state.episode_id,
        "observation": observation or state.last_observation,
        "reward": round(reward, 4),
        "terminated": terminated,
        "truncated": False,
        "done": state.done,
        "info": {"step": state.step_index},
    }
