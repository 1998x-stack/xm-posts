from pathlib import Path
import importlib.util

MODULE = Path(__file__).resolve().parents[1] / "posts/evaluation/llm-as-a-judge/judge_metrics.py"
SPEC = importlib.util.spec_from_file_location("judge_metrics", MODULE)
judge_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(judge_metrics)


def test_agreement_rate_and_kappa_are_not_the_same_measure():
    human = ["yes", "yes", "no", "no"]
    judge = ["yes", "no", "no", "no"]
    assert judge_metrics.agreement_rate(human, judge) == 0.75
    assert round(judge_metrics.cohens_kappa(human, judge), 6) == 0.5


def test_swap_audit_separates_candidate_preference_from_position_bias():
    assert judge_metrics.position_swap_audit("A", "B") == "candidate_a"
    assert judge_metrics.position_swap_audit("B", "A") == "candidate_b"
    assert judge_metrics.position_swap_audit("A", "A") == "first_position"
    assert judge_metrics.position_swap_audit("B", "B") == "second_position"
    assert judge_metrics.position_swap_audit("tie", "tie") == "tie_consistent"
    assert judge_metrics.position_swap_audit("A", "tie") == "unstable"


def test_position_consistency_rate_uses_candidate_identity_after_swap():
    pairs = [("A", "B"), ("A", "A"), ("B", "A"), ("B", "B")]
    assert judge_metrics.position_consistency_rate(pairs) == 0.5


def test_invalid_or_empty_inputs_fail_closed():
    import pytest
    with pytest.raises(ValueError):
        judge_metrics.agreement_rate([], [])
    with pytest.raises(ValueError):
        judge_metrics.position_swap_audit("C", "A")
    with pytest.raises(ValueError):
        judge_metrics.position_consistency_rate([])
