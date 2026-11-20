"""A tiny, deterministic model of an agent runtime's safety boundary.

This is an educational simulator, not AutoGPT source code and not an LLM.
It makes tool effects, approval gates, step budgets, and stop reasons testable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Effect = Literal["read", "workspace", "external"]


@dataclass(frozen=True)
class PlannedAction:
    name: str
    effect: Effect
    observation: str
    goal_complete: bool = False
    succeeds: bool = True


@dataclass(frozen=True)
class TraceEntry:
    step: int
    action: str
    effect: Effect
    status: Literal["executed", "blocked", "error"]
    observation: str


@dataclass
class RunResult:
    trace: list[TraceEntry] = field(default_factory=list)
    completed: bool = False
    stop_reason: str = "not_started"


def run_plan(
    goal: str,
    plan: list[PlannedAction],
    *,
    max_steps: int = 8,
    approved_external: set[str] | None = None,
) -> RunResult:
    """Replay a fixed plan with explicit external-action approval.

    The goal is retained as task context in this toy model. The simulator
    intentionally does not invent a planner, retry policy, or tool runtime.
    """
    if not goal.strip():
        raise ValueError("goal must not be empty")
    if max_steps < 0:
        raise ValueError("max_steps must be non-negative")

    approved = approved_external or set()
    result = RunResult(stop_reason="plan_exhausted")

    for index, action in enumerate(plan, start=1):
        if len(result.trace) >= max_steps:
            result.stop_reason = "budget_exhausted"
            return result

        if action.effect == "external" and action.name not in approved:
            result.trace.append(
                TraceEntry(
                    index, action.name, action.effect, "blocked",
                    "人工批准缺失；外部动作未执行",
                )
            )
            result.stop_reason = "approval_required"
            return result

        if not action.succeeds:
            result.trace.append(
                TraceEntry(
                    index, action.name, action.effect, "error",
                    "工具执行失败；需要上层策略决定是否恢复",
                )
            )
            result.stop_reason = "tool_error"
            return result

        result.trace.append(
            TraceEntry(index, action.name, action.effect, "executed", action.observation)
        )
        if action.goal_complete:
            result.completed = True
            result.stop_reason = "goal_complete"
            return result

    if len(result.trace) >= max_steps and plan:
        result.stop_reason = "budget_exhausted"
    return result
