#!/usr/bin/env python3
"""Minimal, deterministic one-step Adam+L2 vs AdamW comparison.

Python >= 3.11; standard library only. Educational calculation, not
a reproduction of Loshchilov & Hutter's benchmark training.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt


@dataclass
class State:
    theta: list[float]
    m: list[float]
    v: list[float]
    step: int = 0


def update(
    state: State,
    grad: list[float],
    *,
    lr: float = 0.1,
    weight_decay: float = 0.1,
    beta1: float = 0.9,
    beta2: float = 0.999,
    eps: float = 1e-8,
    decoupled: bool = True,
) -> State:
    """Return one Adam(W) step. Use a common old theta for both branches."""
    assert len(state.theta) == len(grad) == len(state.m) == len(state.v)
    assert lr > 0 and weight_decay >= 0 and eps > 0
    assert 0 <= beta1 < 1 and 0 <= beta2 < 1
    t = state.step + 1
    new_theta, new_m, new_v = [], [], []
    for theta, g, m, v in zip(state.theta, grad, state.m, state.v):
        effective_g = g if decoupled else g + weight_decay * theta
        m1 = beta1 * m + (1 - beta1) * effective_g
        v1 = beta2 * v + (1 - beta2) * effective_g**2
        m_hat = m1 / (1 - beta1**t)
        v_hat = v1 / (1 - beta2**t)
        adaptive = lr * m_hat / (sqrt(v_hat) + eps)
        decay = lr * weight_decay * theta if decoupled else 0.0
        new_theta.append(theta - adaptive - decay)
        new_m.append(m1)
        new_v.append(v1)
    return State(new_theta, new_m, new_v, t)


def demo() -> tuple[State, State]:
    zero = State([1.0, 2.0], [0.0, 0.0], [0.0, 0.0])
    coupled = update(zero, [0.0, 0.0], decoupled=False)
    decoupled = update(zero, [0.0, 0.0], decoupled=True)
    assert decoupled.m == [0.0, 0.0]
    assert decoupled.v == [0.0, 0.0]
    assert abs(decoupled.theta[0] - 0.99) < 1e-12
    assert abs(decoupled.theta[1] - 1.98) < 1e-12
    assert coupled.m != decoupled.m
    assert coupled.v != decoupled.v
    assert coupled.theta != decoupled.theta
    # With zero decay the two algorithms have identical trajectories.
    baseline = State([1.0, 2.0], [0.0, 0.0], [0.0, 0.0])
    for gradient in ([0.2, -0.3], [-0.1, 0.05], [0.0, 0.0]):
        left = update(baseline, list(gradient), weight_decay=0, decoupled=False)
        right = update(baseline, list(gradient), weight_decay=0, decoupled=True)
        assert left == right
        baseline = left
    return coupled, decoupled


if __name__ == "__main__":
    coupled, adamw = demo()
    print("Adam + L2:", coupled.theta)
    print("AdamW:    ", adamw.theta)
