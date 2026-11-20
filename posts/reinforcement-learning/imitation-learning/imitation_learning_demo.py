"""Small deterministic teaching functions for imitation learning.

This module illustrates definitions; it is not a robot simulator or a paper
benchmark reproduction.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence


def continuous_bc_mse(predicted: Sequence[float], expert: Sequence[float]) -> float:
    """Mean squared error between predicted and demonstrated scalar actions."""
    if len(predicted) != len(expert) or not predicted:
        raise ValueError("predicted and expert must be equal-length non-empty sequences")
    return sum((float(p) - float(e)) ** 2 for p, e in zip(predicted, expert)) / len(expert)


def dagger_aggregate(
    dataset: Sequence[tuple[float, float]],
    learner_states: Iterable[float],
    expert_policy: Callable[[float], float],
) -> list[tuple[float, float]]:
    """Append expert labels for states visited by the current learner policy."""
    aggregated = list(dataset)
    aggregated.extend((float(state), float(expert_policy(float(state)))) for state in learner_states)
    return aggregated


def at_least_one_error_probability(epsilon: float, horizon: int) -> float:
    """P(at least one error) under independent, constant per-step error probability."""
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError("epsilon must be between 0 and 1")
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    return 1.0 - (1.0 - epsilon) ** horizon


def expected_error_count(epsilon: float, horizon: int) -> float:
    """Expected number of errors under the same independent-error toy model."""
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError("epsilon must be between 0 and 1")
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    return epsilon * horizon
