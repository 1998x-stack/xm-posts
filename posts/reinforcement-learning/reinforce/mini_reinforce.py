"""Minimal, deterministic REINFORCE math for a two-action Bernoulli bandit.

No environment, neural network, or learning convergence is claimed.
Run: python mini_reinforce.py
"""
from __future__ import annotations
import math
import random


def sigmoid(theta: float) -> float:
    return 1.0 / (1.0 + math.exp(-theta))


def score(a: int, p: float) -> float:
    """d log Bernoulli(a; sigmoid(theta)) / d theta = a - p."""
    if a not in (0, 1) or not 0.0 < p < 1.0:
        raise ValueError("a must be 0/1, p strictly between 0 and 1")
    return a - p


def reward_to_go(rewards: list[float]) -> list[float]:
    """Undiscounted finite-episode future reward sums."""
    acc = 0.0
    result = [0.0] * len(rewards)
    for t in range(len(rewards) - 1, -1, -1):
        acc += rewards[t]
        result[t] = acc
    return result


def gradient_sample(a: int, p: float, reward: float, baseline: float = 0.0) -> float:
    return (reward - baseline) * score(a, p)


def exact_moments(p: float, r1: float, r0: float, baseline: float) -> tuple[float, float]:
    """Exact mean and variance of one sampled score-function gradient."""
    g1 = gradient_sample(1, p, r1, baseline)
    g0 = gradient_sample(0, p, r0, baseline)
    mean = p * g1 + (1.0 - p) * g0
    variance = p * (g1 - mean) ** 2 + (1.0 - p) * (g0 - mean) ** 2
    return mean, variance


def optimal_scalar_baseline(p: float, r1: float, r0: float) -> float:
    """Variance-minimizing action-independent baseline for this 1D bandit."""
    return (1.0 - p) * r1 + p * r0


def monte_carlo_mean(p: float, r1: float, r0: float, baseline: float, n: int = 30000) -> float:
    """Illustrative reproducible sampling; not an RL experiment."""
    rng = random.Random(1992)
    total = 0.0
    for _ in range(n):
        a = 1 if rng.random() < p else 0
        total += gradient_sample(a, p, r1 if a else r0, baseline)
    return total / n


def main() -> None:
    p, r1, r0 = 0.35, 2.0, 0.0
    truth = p * (1 - p) * (r1 - r0)
    for b in (0.0, 1.3, 2.0):
        mean, variance = exact_moments(p, r1, r0, b)
        observed = monte_carlo_mean(p, r1, r0, b)
        assert math.isclose(mean, truth, abs_tol=1e-12)
        assert abs(observed - truth) < 0.03
        print(f"b={b:.1f} expected={mean:.6f} variance={variance:.6f} sample≈{observed:.6f}")
    assert reward_to_go([1, 0, 3]) == [4, 3, 3]



def discounted_weights(rewards: list[float], gamma: float) -> list[float]:
    """Absolute-time weights for the start-state discounted objective."""
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be in [0,1]")
    acc = 0.0
    out = [0.0] * len(rewards)
    for t in range(len(rewards)-1, -1, -1):
        acc = rewards[t] + gamma * acc
        out[t] = gamma**t * acc
    return out


def leave_one_out(rewards: list[float]) -> list[float]:
    k = len(rewards)
    if k < 2:
        raise ValueError("RLOO needs at least two samples")
    total = sum(rewards)
    return [r - (total-r)/(k-1) for r in rewards]


def exact_group_gradient(p: float, k: int, loo: bool) -> float:
    """Enumerate independent Bernoulli sequences; reward equals action."""
    from itertools import product
    if not 0 < p < 1 or k < 2:
        raise ValueError("invalid p or k")
    result = 0.0
    for actions in product((0, 1), repeat=k):
        n = sum(actions)
        prob = p**n * (1-p)**(k-n)
        weights = leave_one_out(list(actions)) if loo else [a-n/k for a in actions]
        result += prob * sum(w*score(a,p) for a,w in zip(actions,weights))/k
    return result

if __name__ == "__main__":
    main()
