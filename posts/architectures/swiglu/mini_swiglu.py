"""Minimal bias-free SwiGLU mathematics: standard-library only, not a T5 replication."""
from __future__ import annotations
from math import exp, isclose


def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + exp(-z)) if z >= 0 else exp(z) / (1.0 + exp(z))


def silu(z: float) -> float:
    return z * sigmoid(z)


def silu_derivative(z: float) -> float:
    s = sigmoid(z)
    return s + z * s * (1.0 - s)


def dot(x: list[float], w: list[float]) -> float:
    assert len(x) == len(w)
    return sum(a * b for a, b in zip(x, w))


def swiglu(x: list[float], gate: list[list[float]],
           up: list[list[float]], down: list[list[float]]) -> list[float]:
    """Weights are lists of columns; gate/up: (d, m), down: (m, d)."""
    d, m = len(x), len(gate)
    assert len(up) == m and all(len(col) == d for col in gate + up)
    h = [silu(dot(x, gate[j])) * dot(x, up[j]) for j in range(m)]
    assert len(down) == d and all(len(col) == m for col in down)
    return [dot(h, down[k]) for k in range(d)]


def weight_counts(d: int, regular_width: int, gated_width: int) -> tuple[int, int]:
    return 2 * d * regular_width, 3 * d * gated_width


def self_test() -> None:
    assert silu(0) == 0
    assert silu(-1) < 0  # unlike a sigmoid gate, SwiGLU can have a negative gate
    assert silu(2) > 1    # and the gate is not bounded above by one
    eps = 1e-5
    for z in (-4.0, -1.0, 0.0, 2.0, 5.0):
        numeric = (silu(z + eps) - silu(z - eps)) / (2 * eps)
        assert isclose(numeric, silu_derivative(z), rel_tol=1e-8, abs_tol=1e-8)
    x = [1.0, -2.0]
    gate = [[1.0, 0.0], [0.0, 1.0], [1.0, -1.0]]
    up = [[1.0, 1.0], [2.0, 0.0], [0.0, -1.0]]
    down = [[1.0, 0.0, 1.0], [0.0, 1.0, -1.0]]
    got = swiglu(x, gate, up, down)
    hidden = [silu(1.0) * -1.0, silu(-2.0) * 2.0, silu(3.0) * 2.0]
    assert isclose(got[0], hidden[0] + hidden[2], rel_tol=1e-12)
    assert isclose(got[1], hidden[1] - hidden[2], rel_tol=1e-12)
    assert weight_counts(768, 3072, 2048) == (4718592, 4718592)


if __name__ == "__main__":
    self_test()
    print("SwiGLU assertions passed (shapes, parameter counts, SiLU gradient).")
