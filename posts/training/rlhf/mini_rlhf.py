"""Minimal deterministic illustrations for RLHF math; not a PPO trainer."""
from __future__ import annotations
import math

def preference_probability(winner_score: float, loser_score: float) -> float:
    difference = winner_score - loser_score
    if difference >= 0:
        return 1.0 / (1.0 + math.exp(-difference))
    value = math.exp(difference)
    return value / (1.0 + value)

def pairwise_loss(winner_score: float, loser_score: float) -> float:
    difference = winner_score - loser_score
    return max(-difference, 0.0) + math.log1p(math.exp(-abs(difference)))

def discrete_kl(policy: list[float], reference: list[float]) -> float:
    assert len(policy) == len(reference) and policy
    assert all(p > 0 and q > 0 for p, q in zip(policy, reference))
    assert abs(sum(policy) - 1.0) < 1e-10
    assert abs(sum(reference) - 1.0) < 1e-10
    return sum(p * math.log(p / q) for p, q in zip(policy, reference))

def ppo_clipped_objective(ratio: float, advantage: float, epsilon: float = 0.2) -> float:
    """The single-token clipped surrogate (maximize this), not full PPO."""
    assert ratio > 0 and 0 < epsilon < 1
    limited = min(1 + epsilon, max(1 - epsilon, ratio))
    return min(ratio * advantage, limited * advantage)

def run_checks() -> None:
    assert math.isclose(preference_probability(2, 0), 0.8807970779778823)
    assert preference_probability(2, 0) > preference_probability(0, 2)
    assert math.isclose(pairwise_loss(0, 0), math.log(2))
    assert math.isclose(pairwise_loss(2, 0), pairwise_loss(12, 10))
    assert math.isclose(discrete_kl([0.5, 0.5], [0.5, 0.5]), 0.0)
    assert discrete_kl([0.9, 0.1], [0.5, 0.5]) > 0
    assert math.isclose(ppo_clipped_objective(1.5, 1.0), 1.2)
    assert math.isclose(ppo_clipped_objective(0.5, -1.0), -0.8)

if __name__ == "__main__":
    run_checks()
    print("RLHF toy math checks passed")
