import pytest

from imitation_learning_demo import (
    at_least_one_error_probability,
    continuous_bc_mse,
    dagger_aggregate,
    expected_error_count,
)


def test_continuous_bc_mse_matches_hand_calculation():
    assert continuous_bc_mse([0.5, -0.2], [1.0, 0.0]) == pytest.approx(0.145)


def test_continuous_bc_mse_rejects_empty_or_mismatched_batches():
    with pytest.raises(ValueError):
        continuous_bc_mse([], [])
    with pytest.raises(ValueError):
        continuous_bc_mse([0.0], [0.0, 1.0])


def test_dagger_aggregate_keeps_old_data_and_queries_expert_on_learner_states():
    original = [(0.0, 0.0)]
    aggregated = dagger_aggregate(original, [2.0, -3.0], lambda state: -state)
    assert aggregated == [(0.0, 0.0), (2.0, -2.0), (-3.0, 3.0)]
    assert original == [(0.0, 0.0)]


def test_dagger_aggregate_empty_rollout_returns_a_copy():
    original = [(1.0, -1.0)]
    aggregated = dagger_aggregate(original, [], lambda state: -state)
    assert aggregated == original
    assert aggregated is not original


def test_cumulative_error_probability_matches_independent_model():
    assert at_least_one_error_probability(0.05, 20) == pytest.approx(1 - 0.95**20)
    assert expected_error_count(0.05, 20) == pytest.approx(1.0)


def test_cumulative_error_probability_boundaries():
    assert at_least_one_error_probability(0.0, 20) == 0.0
    assert at_least_one_error_probability(1.0, 20) == 1.0
    assert at_least_one_error_probability(0.25, 0) == 0.0
    assert expected_error_count(0.25, 0) == 0.0


@pytest.mark.parametrize("epsilon,horizon", [(-0.1, 4), (1.1, 4), (0.1, -1)])
def test_error_model_rejects_invalid_inputs(epsilon, horizon):
    with pytest.raises(ValueError):
        at_least_one_error_probability(epsilon, horizon)


def test_error_model_rejects_invalid_expected_count_inputs():
    with pytest.raises(ValueError):
        expected_error_count(1.2, 5)
    with pytest.raises(ValueError):
        expected_error_count(0.2, -1)
