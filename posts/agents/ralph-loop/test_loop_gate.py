import pytest

from loop_gate import Verification, decide


def test_complete_requires_promise_and_external_checks():
    check = Verification(completion_promise=True, tests_pass=True)
    assert decide(check, iteration=3, max_iterations=10) == "complete"


def test_promise_alone_does_not_complete():
    check = Verification(completion_promise=True, tests_pass=False)
    assert decide(check, iteration=3, max_iterations=10) == "continue"


def test_passing_tests_without_promise_is_not_automatic_completion():
    check = Verification(completion_promise=False, tests_pass=True)
    assert decide(check, iteration=3, max_iterations=10) == "continue"


def test_regression_blocks_completion():
    check = Verification(completion_promise=True, tests_pass=True, regressions=1)
    assert decide(check, iteration=3, max_iterations=10) == "continue"


def test_blocker_blocks_completion():
    check = Verification(completion_promise=True, tests_pass=True, blockers=1)
    assert decide(check, iteration=3, max_iterations=10) == "continue"


def test_iteration_budget_is_a_hard_stop():
    check = Verification(completion_promise=False, tests_pass=False)
    assert decide(check, iteration=10, max_iterations=10) == "budget_exhausted"


@pytest.mark.parametrize("iteration,max_iterations", [(0, 10), (1, 0), (-1, 5)])
def test_invalid_iteration_budget_is_rejected(iteration, max_iterations):
    with pytest.raises(ValueError):
        decide(Verification(False, False), iteration, max_iterations)


def test_negative_diagnostic_counts_are_rejected():
    with pytest.raises(ValueError):
        decide(Verification(False, False, blockers=-1), 1, 5)
