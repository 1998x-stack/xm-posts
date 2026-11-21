"""Small, auditable decision-policy helpers for the Jev explainer.

This module does not call Jev. It consumes an already-returned probability
distribution and applies a caller-owned loss matrix.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class Decision:
    """Chosen action, expected risks, and the risk paid by that action."""

    action: str
    risks: dict[str, float]
    expected_loss: float


def validate_distribution(
    probabilities: Mapping[str, float], *, tolerance: float = 1e-9
) -> dict[str, float]:
    """Validate a closed-set probability distribution and return a plain dict."""
    if not isinstance(probabilities, Mapping) or not probabilities:
        raise ValueError("probabilities must be a non-empty mapping")

    normalized: dict[str, float] = {}
    for label, probability in probabilities.items():
        if not isinstance(label, str) or not label:
            raise ValueError("every outcome label must be a non-empty string")
        if isinstance(probability, bool) or not isinstance(probability, (int, float)):
            raise ValueError(f"probability for {label!r} must be numeric")
        value = float(probability)
        if not isfinite(value) or value < 0.0 or value > 1.0:
            raise ValueError(f"probability for {label!r} must be finite and in [0, 1]")
        normalized[label] = value

    total = sum(normalized.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(f"probabilities must sum to 1 (got {total:.12g})")
    return normalized


def expected_risks(
    probabilities: Mapping[str, float],
    action_costs: Mapping[str, Mapping[str, float]],
) -> dict[str, float]:
    """Compute R(a|x) = sum_y cost[a][y] * P(y|x) for each action."""
    distribution = validate_distribution(probabilities)
    if not isinstance(action_costs, Mapping) or not action_costs:
        raise ValueError("action_costs must be a non-empty mapping")

    outcome_labels = set(distribution)
    risks: dict[str, float] = {}
    for action, row in action_costs.items():
        if not isinstance(action, str) or not action:
            raise ValueError("every action name must be a non-empty string")
        if not isinstance(row, Mapping) or set(row) != outcome_labels:
            raise ValueError(
                f"cost row for {action!r} must define exactly {sorted(outcome_labels)}"
            )

        risk = 0.0
        for label, probability in distribution.items():
            cost = row[label]
            if isinstance(cost, bool) or not isinstance(cost, (int, float)):
                raise ValueError(f"cost for ({action!r}, {label!r}) must be numeric")
            value = float(cost)
            if not isfinite(value) or value < 0.0:
                raise ValueError("costs must be finite and non-negative")
            risk += probability * value
        risks[action] = risk
    return risks


def choose_with_review(
    probabilities: Mapping[str, float],
    action_costs: Mapping[str, Mapping[str, float]],
    *,
    review_cost: float,
) -> Decision:
    """Choose the lowest-risk automatic action or defer to human review.

    Ties between automatic actions are resolved lexicographically so that the
    result is deterministic. Review is chosen only when its cost is strictly
    lower than the best automatic risk; an exact tie stays with the automatic
    action and can be changed to another convention by the caller.
    """
    if isinstance(review_cost, bool) or not isinstance(review_cost, (int, float)):
        raise ValueError("review_cost must be numeric")
    review_value = float(review_cost)
    if not isfinite(review_value) or review_value < 0.0:
        raise ValueError("review_cost must be finite and non-negative")

    risks = expected_risks(probabilities, action_costs)
    best_action = min(risks, key=lambda action: (risks[action], action))
    best_risk = risks[best_action]
    if review_value < best_risk:
        return Decision("review", risks, review_value)
    return Decision(best_action, risks, best_risk)


def binary_cost_threshold(false_positive_cost: float, false_negative_cost: float) -> float:
    """Bayes threshold C_FP / (C_FP + C_FN) for a binary decision."""
    values = (false_positive_cost, false_negative_cost)
    if any(
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not isfinite(float(value))
        or float(value) < 0.0
        for value in values
    ):
        raise ValueError("error costs must be finite, numeric, and non-negative")

    fp, fn = map(float, values)
    if fp + fn == 0.0:
        raise ValueError("at least one error cost must be positive")
    return fp / (fp + fn)
