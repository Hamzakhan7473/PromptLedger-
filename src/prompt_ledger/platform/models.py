from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ToolCall:
    tool: str
    input: dict[str, Any]
    output: dict[str, Any]
    latency_ms: float = 0.0


@dataclass
class TrajectoryStep:
    step_index: int
    state: dict[str, Any]
    action: str
    tool_calls: list[ToolCall]
    observation: dict[str, Any]
    output: str = ""


@dataclass
class RewardBreakdown:
    correctness: float = 0.0
    citation_quality: float = 0.0
    cost: float = 0.0
    latency: float = 0.0
    policy_compliance: float = 0.0
    human_feedback: float = 0.0
    total: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass
class Trajectory:
    id: str
    environment: str
    prompt_id: str
    prompt_version: str
    model: str
    task: str
    prompt_text: str
    steps: list[TrajectoryStep] = field(default_factory=list)
    final_output: str = ""
    reward: RewardBreakdown = field(default_factory=RewardBreakdown)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "environment": self.environment,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "model": self.model,
            "task": self.task,
            "prompt_text": self.prompt_text,
            "steps": [
                {
                    "step_index": s.step_index,
                    "state": s.state,
                    "action": s.action,
                    "tool_calls": [asdict(tc) for tc in s.tool_calls],
                    "observation": s.observation,
                    "output": s.output,
                }
                for s in self.steps
            ],
            "final_output": self.final_output,
            "reward": self.reward.to_dict(),
            "metadata": self.metadata,
        }
