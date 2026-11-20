from pathlib import Path

import pytest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts" / "agents" / "loop-engineering"))
from loop_engine import Verdict, run_loop


def test_loop_retries_with_verifier_feedback_then_completes(tmp_path: Path):
    state_file = tmp_path / "state" / "loop.json"
    calls = []

    def act(feedback: str, attempt: int) -> str:
        calls.append((feedback, attempt))
        return "patch-v1" if attempt == 1 else "patch-v2"

    def verify(proposal: str) -> Verdict:
        if proposal == "patch-v1":
            return Verdict(False, "test_failed: expected 4, got 12")
        return Verdict(True, "all required checks passed")

    state = run_loop("issue-42", act, verify, state_file, max_attempts=3)

    assert state["status"] == "completed"
    assert state["attempts"] == 2
    assert state["artifact"] == "patch-v2"
    assert calls[1][0] == "test_failed: expected 4, got 12"
    assert state_file.exists()


def test_loop_stops_when_attempt_budget_is_exhausted(tmp_path: Path):
    def act(feedback: str, attempt: int) -> str:
        return f"candidate-{attempt}"

    state = run_loop(
        "issue-43",
        act,
        lambda proposal: Verdict(False, "test still fails"),
        tmp_path / "state.json",
        max_attempts=2,
    )

    assert state["status"] == "budget_exhausted"
    assert state["attempts"] == 2
    assert state["artifact"] is None


def test_loop_escalates_instead_of_retrying_unsafe_change(tmp_path: Path):
    calls = []

    def act(feedback: str, attempt: int) -> str:
        calls.append(attempt)
        return "migration"

    state = run_loop(
        "issue-44",
        act,
        lambda proposal: Verdict(False, "destructive migration requires approval", True),
        tmp_path / "state.json",
        max_attempts=5,
    )

    assert state["status"] == "needs_human"
    assert state["attempts"] == 1
    assert calls == [1]


def test_terminal_state_is_not_executed_twice(tmp_path: Path):
    state_file = tmp_path / "state.json"
    first = run_loop(
        "issue-45",
        lambda feedback, attempt: "accepted",
        lambda proposal: Verdict(True),
        state_file,
    )

    def must_not_run(feedback: str, attempt: int) -> str:
        pytest.fail("terminal task must not execute again")

    second = run_loop("issue-45", must_not_run, lambda p: Verdict(False), state_file)
    assert second == first


def test_state_file_cannot_be_reused_for_another_task(tmp_path: Path):
    state_file = tmp_path / "state.json"
    run_loop("issue-46", lambda f, n: "ok", lambda p: Verdict(True), state_file)
    with pytest.raises(ValueError, match="different task_id"):
        run_loop("issue-47", lambda f, n: "ok", lambda p: Verdict(True), state_file)
