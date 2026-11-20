"""A tiny, bounded orchestration loop for teaching and testing.

This is not an LLM runtime. The act() and verify() callbacks stand in for
a worker and an independent verifier; real deployments need sandboxing,
leases, idempotency keys, audit logs, and human approval for risky actions.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Callable


TERMINAL = {"completed", "needs_human", "budget_exhausted"}


@dataclass(frozen=True)
class Verdict:
    passed: bool
    feedback: str = ""
    escalate: bool = False


def _save(path: Path, state: dict) -> None:
    """Atomically replace the small JSON state record."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _load(path: Path, task_id: str) -> dict:
    if not path.exists():
        return {
            "task_id": task_id,
            "status": "pending",
            "attempts": 0,
            "last_feedback": "",
            "artifact": None,
            "history": [],
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("task_id") != task_id:
        raise ValueError("state file belongs to a different task_id")
    return state


def run_loop(
    task_id: str,
    act: Callable[[str, int], str],
    verify: Callable[[str], Verdict],
    state_path: Path,
    max_attempts: int = 3,
) -> dict:
    """Run until verified, escalated, or the explicit attempt budget is spent.

    A completed or escalated task is terminal: rerunning the same task_id
    returns its persisted state rather than repeating side effects.
    """
    if not task_id.strip():
        raise ValueError("task_id must not be empty")
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    state = _load(state_path, task_id)
    if state["status"] in TERMINAL:
        return state

    while state["attempts"] < max_attempts:
        state["attempts"] += 1
        state["status"] = "running"
        _save(state_path, state)

        proposal = act(state["last_feedback"], state["attempts"])
        verdict = verify(proposal)
        state["history"].append({
            "attempt": state["attempts"],
            "proposal": proposal,
            "passed": verdict.passed,
            "feedback": verdict.feedback,
            "escalate": verdict.escalate,
        })

        if verdict.escalate:
            state["status"] = "needs_human"
            state["last_feedback"] = verdict.feedback
            _save(state_path, state)
            return state

        if verdict.passed:
            state["status"] = "completed"
            state["artifact"] = proposal
            state["last_feedback"] = ""
            _save(state_path, state)
            return state

        state["last_feedback"] = verdict.feedback
        state["status"] = "retrying"
        _save(state_path, state)

    state["status"] = "budget_exhausted"
    _save(state_path, state)
    return state
