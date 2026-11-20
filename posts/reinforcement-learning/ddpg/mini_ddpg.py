"""Deterministic DDPG math checks; not a MuJoCo training reproduction.

No third-party dependencies. In a real agent, Q_phi and mu_theta are neural
networks; these small scalar functions make Bellman, gradients and EMA auditable.
"""
from __future__ import annotations

import math
import random


def bellman_target(reward: float, gamma: float, q_target: float, terminal: bool) -> float:
    """One-step TD target with terminal mask (modern explicit-done convention)."""
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must be in [0, 1]")
    return reward + gamma * (0.0 if terminal else q_target)


def critic_mse(predictions: list[float], targets: list[float]) -> float:
    if not predictions or len(predictions) != len(targets):
        raise ValueError("matching nonempty prediction and target batches required")
    return sum((p - t) ** 2 for p, t in zip(predictions, targets)) / len(predictions)


def polyak_update(target: float, online: float, tau: float) -> float:
    """DDPG paper convention: small tau multiplies the online parameter."""
    if not 0 <= tau <= 1:
        raise ValueError("tau must be in [0, 1]")
    return tau * online + (1.0 - tau) * target


def actor(s: float, theta: float) -> float:
    """Toy one-dimensional deterministic policy; no action clipping."""
    return theta * s


def critic(s: float, action: float) -> float:
    """Toy action-value landscape, Q(s,a) = -(a - 0.5s)^2."""
    return -(action - 0.5 * s) ** 2


def actor_gradient(s: float, theta: float) -> float:
    """dQ/da * da/dtheta, with critic parameters held fixed."""
    a = actor(s, theta)
    return -2.0 * (a - 0.5 * s) * s


def ou_next(x: float, mean: float, kappa: float, sigma: float,
            dt: float, standard_normal: float) -> float:
    """Euler-Maruyama step, a teaching discretization of OU noise."""
    if kappa < 0 or sigma < 0 or dt <= 0:
        raise ValueError("kappa, sigma >= 0 and dt > 0 required")
    return x + kappa * (mean - x) * dt + sigma * math.sqrt(dt) * standard_normal


def replay_sample(buffer: list[tuple], batch_size: int, seed: int = 0) -> list[tuple]:
    """Uniform sampling without replacement for this small educational example."""
    if not 0 < batch_size <= len(buffer):
        raise ValueError("invalid mini-batch size")
    return random.Random(seed).sample(buffer, batch_size)


def check() -> None:
    assert math.isclose(bellman_target(1.0, 0.99, 4.0, False), 4.96)
    assert bellman_target(1.0, 0.99, 4.0, True) == 1.0
    assert math.isclose(critic_mse([1.0, 3.0], [2.0, 1.0]), 2.5)
    assert math.isclose(polyak_update(0.0, 10.0, 0.01), 0.1)
    s, theta, h = 2.0, 0.2, 1e-6
    finite_diff = (critic(s, actor(s, theta + h))
                   - critic(s, actor(s, theta - h))) / (2.0 * h)
    assert math.isclose(actor_gradient(s, theta), finite_diff, rel_tol=1e-7)
    assert ou_next(1.0, 0.0, 0.5, 0.0, 0.1, 4.2) == 0.95
    assert replay_sample([(i,) for i in range(6)], 3, seed=8) == replay_sample(
        [(i,) for i in range(6)], 3, seed=8)


if __name__ == "__main__":
    check()
    print("DDPG toy math assertions passed")
