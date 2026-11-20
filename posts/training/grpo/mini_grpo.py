"""Dependency-free numerical kernels to teach GRPO, not a training reproduction."""
from __future__ import annotations
from math import log, sqrt, isclose
from typing import Sequence


def advantages(rewards: Sequence[float]) -> list[float]:
    """Population-std per-prompt normalization; zero-variance group -> zero."""
    if not rewards:
        raise ValueError("a prompt group must contain at least one reward")
    mu = sum(rewards) / len(rewards)
    sigma = sqrt(sum((r - mu) ** 2 for r in rewards) / len(rewards))
    if sigma == 0:
        return [0.0] * len(rewards)
    return [(r - mu) / sigma for r in rewards]


def clipped_surrogate(ratio: float, advantage: float, eps: float) -> float:
    """min(ratio*A, clip(ratio,1-eps,1+eps)*A), maximization term."""
    if ratio <= 0 or not 0 <= eps < 1:
        raise ValueError("ratio > 0 and 0 <= eps < 1 required")
    clipped = min(max(ratio, 1.0 - eps), 1.0 + eps)
    return min(ratio * advantage, clipped * advantage)


def kl_k3(reference_over_current: float) -> float:
    """k3(u)=u-log(u)-1; sample-wise non-negative, KL only in expectation."""
    if reference_over_current <= 0:
        raise ValueError("probability ratio must be positive")
    value = reference_over_current - log(reference_over_current) - 1.0
    return max(0.0, value)  # guard tiny floating-point roundoff


if __name__ == "__main__":
    assert advantages([1.0, 0.0, 1.0, 0.0]) == [1.0, -1.0, 1.0, -1.0]
    assert advantages([1, 1, 1, 1]) == [0.0] * 4
    assert isclose(clipped_surrogate(1.5, 1.0, 0.2), 1.2)
    assert isclose(clipped_surrogate(0.5, -1.0, 0.2), -0.8)
    assert isclose(kl_k3(1.0), 0.0)
    print("GRPO teaching checks passed")
