"""Small, auditable examples of exact discrete rejection sampling and reward ranking."""
from __future__ import annotations

import random


def rejection_sample(target: list[float], proposal: list[float], n: int, seed: int = 0) -> list[int]:
    """Draw n samples from a normalized discrete target distribution.

    The proposal must cover the support of target. The minimal envelope is
    M = max_i target[i] / proposal[i], so each acceptance probability is <= 1.
    """
    if not target or len(target) != len(proposal):
        raise ValueError("target and proposal must have equal nonzero length")
    if any(p < 0 for p in target) or any(q < 0 for q in proposal):
        raise ValueError("probabilities must be non-negative")
    if abs(sum(target) - 1.0) > 1e-9 or abs(sum(proposal) - 1.0) > 1e-9:
        raise ValueError("target and proposal must each sum to one")
    if any(p > 0 and q == 0 for p, q in zip(target, proposal)):
        raise ValueError("proposal does not cover target support")
    if n <= 0:
        raise ValueError("n must be positive")

    ratios = [p / q if q > 0 else 0.0 for p, q in zip(target, proposal)]
    envelope = max(ratios)
    if envelope <= 0:
        raise ValueError("target distribution has no positive mass")

    rng = random.Random(seed)
    states = list(range(len(target)))
    accepted: list[int] = []
    while len(accepted) < n:
        candidate = rng.choices(states, weights=proposal, k=1)[0]
        q = proposal[candidate]
        accept_prob = target[candidate] / (envelope * q)
        if rng.random() < accept_prob:
            accepted.append(candidate)
    return accepted


def best_of_n(candidates: list[str], rewards: list[float]) -> str:
    """Return the highest-reward candidate; this is ranking, not exact rejection sampling."""
    if not candidates or len(candidates) != len(rewards):
        raise ValueError("candidates and rewards must have equal nonzero length")
    return candidates[max(range(len(rewards)), key=rewards.__getitem__)]
