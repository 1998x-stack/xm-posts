"""Deterministic, one-state Bellman backups (standard library only).

S has two actions:
 stop: reward 1, transition to terminal with continuation value 0;
 loop: reward 0.3, transition to S.
Discount 0 <= gamma < 1. p is the fixed policy's loop probability.
This is a mathematics check, NOT a reinforcement-learning benchmark.
"""
from math import isclose


def _check(gamma: float, p: float | None = None) -> None:
    if not (0 <= gamma < 1):
        raise ValueError("discount gamma must be in [0, 1)")
    if p is not None and not (0 <= p <= 1):
        raise ValueError("policy loop probability must be in [0, 1]")


def optimal_backup(v: float, gamma: float) -> float:
    _check(gamma)
    return max(1.0, 0.3 + gamma * v)


def policy_backup(v: float, gamma: float, p: float) -> float:
    _check(gamma, p)
    return (1 - p) * 1.0 + p * (0.3 + gamma * v)


def exact_policy(gamma: float, p: float) -> float:
    _check(gamma, p)
    return (1 - 0.7 * p) / (1 - gamma * p)


def exact_optimal(gamma: float) -> float:
    _check(gamma)
    return max(1.0, 0.3 / (1 - gamma))


def value_iteration(gamma: float, start: float = 0.0,
                    tolerance: float = 1e-11, limit: int = 10000) -> tuple[float, int]:
    _check(gamma)
    v = float(start)
    for step in range(1, limit + 1):
        updated = optimal_backup(v, gamma)
        if abs(updated - v) < tolerance * (1 - gamma):
            return updated, step
        v = updated
    raise RuntimeError("value iteration did not converge within limit")


def self_test() -> None:
    for gamma, expected in ((0.0, 1.0), (0.5, 1.0),
                            (0.7, 1.0), (0.9, 3.0), (0.95, 6.0)):
        assert isclose(exact_optimal(gamma), expected, abs_tol=1e-10)
        for initial in (-10.0, 0.0, 100.0):
            estimated, n = value_iteration(gamma, start=initial)
            assert n > 0 and isclose(estimated, expected, abs_tol=1e-8)
        for p in (0.0, 0.25, 0.5, 0.75, 1.0):
            v = exact_policy(gamma, p)
            assert isclose(policy_backup(v, gamma, p), v, abs_tol=1e-11)
            for a, b in ((-4.0, 5.0), (1.0, 2.0)):
                assert abs(policy_backup(a, gamma, p) - policy_backup(b, gamma, p)) <= gamma * abs(a - b) + 1e-12
                assert abs(optimal_backup(a, gamma) - optimal_backup(b, gamma)) <= gamma * abs(a - b) + 1e-12
    assert optimal_backup(100, 0) == 1.0  # stop action is terminal: no bootstrap
    try:
        exact_optimal(1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("gamma=1 needs separate convergence assumptions")


if __name__ == "__main__":
    self_test()
    print("Bellman example: deterministic assertions passed")
