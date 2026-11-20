"""DeltaNet's matrix state update: deterministic, standard-library teaching reference.
Source: Yang et al., NeurIPS 2024 §2.2 and §3.1.
This is not the full DeltaNet architecture or a GPU-performance reproduction.
"""
from __future__ import annotations
from math import isclose


def dot(a: list[float], b: list[float]) -> float:
    if not a or len(a) != len(b):
        raise ValueError("dot dimensions must match and be nonempty")
    return sum(x * y for x, y in zip(a, b))


def validate(S: list[list[float]], k: list[float], v: list[float], beta: float) -> None:
    if not k or not v or len(S) != len(v) or any(len(row) != len(k) for row in S):
        raise ValueError("S must have shape (d_v, d_k)")
    if not 0 <= beta <= 1:
        raise ValueError("beta is a write gate in [0, 1]")


def read(S: list[list[float]], k: list[float]) -> list[float]:
    if not k or not S or any(len(row) != len(k) for row in S):
        raise ValueError("invalid read shapes")
    return [dot(row, k) for row in S]


def delta_step(S: list[list[float]], k: list[float],
               v: list[float], beta: float) -> list[list[float]]:
    """S <- S + beta*(v - S@k) outer k; no input mutation."""
    validate(S, k, v, beta)
    old = read(S, k)
    return [[S[i][j] + beta * (v[i] - old[i]) * k[j]
             for j in range(len(k))] for i in range(len(v))]


def transition_step(S: list[list[float]], k: list[float],
                    v: list[float], beta: float) -> list[list[float]]:
    """Explicit I - beta*k*k^T transition for algebraic cross-check."""
    validate(S, k, v, beta)
    n = len(k)
    M = [[float(i == j) - beta * k[i] * k[j]
          for j in range(n)] for i in range(n)]
    return [[sum(S[r][h] * M[h][c] for h in range(n)) +
             beta * v[r] * k[c] for c in range(n)]
            for r in range(len(v))]


def close(A: list[list[float]], B: list[list[float]]) -> bool:
    return len(A) == len(B) and all(
        len(a) == len(b) and all(isclose(x, y, abs_tol=1e-12)
                                 for x, y in zip(a, b))
        for a, b in zip(A, B))


def self_test() -> None:
    S = [[0.2, 0.0], [0.0, 0.3]]
    k, v = [1.0, 0.0], [1.0, -2.0]
    assert delta_step(S, k, v, 0.0) == S
    half = delta_step(S, k, v, 0.5)
    assert close(half, [[0.6, 0.0], [-1.0, 0.3]])
    full = delta_step(S, k, v, 1.0)
    assert read(full, k) == v
    assert read(full, [0.0, 1.0]) == [0.0, 0.3]
    assert close(delta_step(S, k, v, 0.6),
                 transition_step(S, k, v, 0.6))
    # Nonunit key: beta=1 is not a full overwrite.
    nonunit = [0.5, 0.0]
    assert read(delta_step([[0.0, 0.0]], nonunit, [1.0], 1.0),
                nonunit) == [0.25]
    # Two successive updates are still equivalent to transition representation.
    cases = [([1.0, 0.0], [1.0, -2.0], 0.3),
             ([0.6, 0.8], [0.5, 1.5], 0.7)]
    a = b = S
    for key, val, beta in cases:
        a = delta_step(a, key, val, beta)
        b = transition_step(b, key, val, beta)
    assert close(a, b)
    try:
        delta_step(S, [1.0], v, 0.5)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid shapes must fail")


if __name__ == "__main__":
    self_test()
    print("DeltaNet toy assertions passed; no full-model or GPU benchmark claim.")
