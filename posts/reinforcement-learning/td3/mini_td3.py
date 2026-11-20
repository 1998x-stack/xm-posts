"""Minimal TD3 math invariants (no Gym, MuJoCo or training dependencies).

The numeric examples test equations, not policy quality or paper benchmark scores.
"""
from __future__ import annotations

import math


def clip(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("invalid clipping bounds")
    return min(high, max(low, value))


def target_action(actor_target_output: float, sampled_noise: float,
                  noise_clip: float, action_low: float, action_high: float) -> float:
    """Clip noise first, then clip the resulting action (common TD3 implementation)."""
    if noise_clip < 0:
        raise ValueError("noise_clip must be nonnegative")
    return clip(actor_target_output + clip(sampled_noise, -noise_clip, noise_clip),
                action_low, action_high)


def clipped_double_target(reward: float, gamma: float, q1: float, q2: float,
                          terminated: bool) -> float:
    if not 0 <= gamma <= 1:
        raise ValueError("gamma must lie in [0,1]")
    return reward if terminated else reward + gamma * min(q1, q2)


def twin_critic_mse(q1_predictions: list[float], q2_predictions: list[float],
                    targets: list[float]) -> tuple[float, float]:
    if not targets or len(q1_predictions) != len(targets) or len(q2_predictions) != len(targets):
        raise ValueError("nonempty equally sized batches required")
    return (sum((p - y) ** 2 for p, y in zip(q1_predictions, targets)) / len(targets),
            sum((p - y) ** 2 for p, y in zip(q2_predictions, targets)) / len(targets))


def policy_and_target_update(critic_gradient_steps: int, policy_delay: int = 2) -> bool:
    if critic_gradient_steps <= 0 or policy_delay <= 0:
        raise ValueError("steps and delay must be positive")
    return critic_gradient_steps % policy_delay == 0


def polyak(online: float, target: float, tau: float = .005) -> float:
    """PMLR paper convention: target <- tau * online + (1-tau) * target."""
    if not 0 <= tau <= 1:
        raise ValueError("invalid tau")
    return tau * online + (1.0 - tau) * target


def toy_actor(state: float, phi: float) -> float:
    return phi * state


def toy_first_critic(state: float, action: float) -> float:
    return -((action - state / 2.0) ** 2)


def actor_gradient(state: float, phi: float) -> float:
    """d Q_1(s, pi_phi(s)) / d phi with first critic held fixed."""
    return -2.0 * (toy_actor(state, phi) - state / 2.0) * state


def check() -> None:
    assert math.isclose(clipped_double_target(1, .9, 10, 6, False), 6.4)
    assert clipped_double_target(1, .9, 10, 6, True) == 1.0
    assert clipped_double_target(-2, 1, -4, 3, False) == -6
    assert math.isclose(target_action(.9, .8, .5, -1, 1), 1.0)
    assert math.isclose(target_action(-.8, -.8, .5, -1, 1), -1.0)
    assert twin_critic_mse([2, 4], [3, 1], [3, 3]) == (.5, 2.0)
    assert [policy_and_target_update(t, 2) for t in range(1, 7)] == [False, True] * 3
    assert math.isclose(polyak(10, 0, .005), .05)
    s, phi, h = 2., .2, 1e-6
    difference = (toy_first_critic(s, toy_actor(s, phi + h)) -
                  toy_first_critic(s, toy_actor(s, phi - h))) / (2 * h)
    assert math.isclose(difference, actor_gradient(s, phi), abs_tol=1e-8)


if __name__ == "__main__":
    check()
    print("TD3 minimal math checks passed")
