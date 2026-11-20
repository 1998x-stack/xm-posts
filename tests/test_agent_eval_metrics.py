from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "posts" / "agents" / "agent-evaluation" / "agent_eval_metrics.py"
SPEC = importlib.util.spec_from_file_location("agent_eval_metrics", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
summarize_runs = MODULE.summarize_runs


def test_repeated_runs_report_distinct_reliability_metrics() -> None:
    runs = [
        [True, True, False, True, True],
        [True, False, False, False, True],
        [False, False, False, False, False],
    ]
    result = summarize_runs(runs)

    assert result["task_count"] == 3
    assert result["attempts_per_task"] == 5
    assert result["pass_at_1"] == pytest.approx(2 / 3)
    assert result["pass_at_k"] == pytest.approx(2 / 3)
    assert result["pass_all_k"] == pytest.approx(0.0)
    assert result["mean_attempt_success"] == pytest.approx(7 / 15)


def test_all_successful_attempts_have_pass_at_k_and_pass_all_k_one() -> None:
    result = summarize_runs([[True, True], [True, True]])
    assert result["pass_at_k"] == pytest.approx(1.0)
    assert result["pass_all_k"] == pytest.approx(1.0)


def test_empty_task_collection_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one task"):
        summarize_runs([])


def test_empty_attempt_row_is_rejected() -> None:
    with pytest.raises(ValueError, match="at least one attempt"):
        summarize_runs([[]])


def test_unequal_attempt_counts_are_rejected() -> None:
    with pytest.raises(ValueError, match="expected 2"):
        summarize_runs([[True, False], [True]])


def test_non_boolean_values_are_rejected() -> None:
    with pytest.raises(TypeError, match="only bool"):
        summarize_runs([[1, 0]])  # type: ignore[list-item]
