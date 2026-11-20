"""Deterministic SAC equation checks. Not an RL agent or benchmark."""
from __future__ import annotations
from math import exp, isfinite, log, log1p, pi

def soft_target(reward: float, gamma: float, terminated: bool,
                q1_next: float, q2_next: float,
                next_logprob: float, alpha: float) -> float:
    """Modern twin-Q soft Bellman target for a single transition."""
    if not 0 <= gamma <= 1 or alpha < 0:
        raise ValueError("gamma in [0,1] and alpha nonnegative required")
    if terminated:
        return reward
    return reward + gamma * (min(q1_next, q2_next) - alpha * next_logprob)

def actor_loss(logprob: float, q1_action: float,
               q2_action: float, alpha: float) -> float:
    if alpha < 0:
        raise ValueError("alpha must be nonnegative")
    return alpha * logprob - min(q1_action, q2_action)

def softplus(x: float) -> float:
    """Numerically stable log(1+exp(x))."""
    return max(x, 0.0) + log1p(exp(-abs(x)))

def tanh_gaussian_logprob(u: float, mu: float, sigma: float) -> float:
    """One-dimensional density for a=tanh(u). Excludes action rescaling."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    gaussian = -0.5 * ((u - mu) / sigma) ** 2 - log(sigma) - 0.5 * log(2 * pi)
    log_jacobian = 2 * (log(2.0) - u - softplus(-2.0 * u))
    return gaussian - log_jacobian

def temperature_objective(alpha: float, logprob: float,
                          target_entropy: float) -> float:
    """Paper 1812.05905 Eq. (18); direct alpha parameterization."""
    if alpha < 0:
        raise ValueError("alpha must be nonnegative")
    return -alpha * (logprob + target_entropy)

def boltzmann_probs(q_values: tuple[float, ...], alpha: float) -> tuple[float, ...]:
    """Discrete teaching model, not the continuous SAC Actor."""
    if alpha <= 0 or not q_values:
        raise ValueError("alpha > 0 and nonempty Q values required")
    maximum = max(q_values)
    weights = tuple(exp((value - maximum) / alpha) for value in q_values)
    total = sum(weights)
    return tuple(x / total for x in weights)

def check() -> None:
    assert abs(soft_target(1.0, 0.9, False, 5, 3, -0.5, 0.2) - 3.79) < 1e-12
    assert soft_target(1.0, 0.9, True, 5, 3, -0.5, 0.2) == 1.0
    assert actor_loss(-0.5, 4, 3, 0.2) == -3.1
    assert abs(tanh_gaussian_logprob(0, 0, 1) + 0.5 * log(2 * pi)) < 1e-12
    assert isfinite(tanh_gaussian_logprob(50, 0, 1))
    assert abs(sum(boltzmann_probs((3, 2, 0), 0.5)) - 1) < 1e-12
    print("SAC mathematical invariants passed")

if __name__ == "__main__":
    check()
