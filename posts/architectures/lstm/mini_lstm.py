"""A single modern, no-peephole, no-projection LSTM step.

Educational standard-library implementation, not the 1997 truncated-gradient
training algorithm and not a full training loop. Shapes: x[D], h/c[H],
weights[4H][D+H]; gate order input, forget, candidate, output.
"""
from __future__ import annotations
import math
from typing import Sequence

def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1 / (1 + z)
    z = math.exp(x)
    return z / (1 + z)

def step(x: Sequence[float], h_prev: Sequence[float],
         c_prev: Sequence[float], weights: Sequence[Sequence[float]],
         bias: Sequence[float]) -> tuple[list[float], list[float]]:
    d, h = len(x), len(h_prev)
    assert d >= 1 and h >= 1 and len(c_prev) == h
    assert len(weights) == 4 * h and len(bias) == 4 * h
    z = list(x) + list(h_prev)
    assert all(len(row) == d + h for row in weights)
    a = [sum(w * v for w, v in zip(row, z)) + b
         for row, b in zip(weights, bias)]
    i = [sigmoid(v) for v in a[:h]]
    f = [sigmoid(v) for v in a[h:2 * h]]
    g = [math.tanh(v) for v in a[2 * h:3 * h]]
    o = [sigmoid(v) for v in a[3 * h:]]
    c = [ff * cc + ii * gg for ff, cc, ii, gg in zip(f, c_prev, i, g)]
    hidden = [oo * math.tanh(cc) for oo, cc in zip(o, c)]
    return hidden, c

def retention(forget: float, steps: int) -> float:
    assert 0 <= forget <= 1 and steps >= 0
    return forget ** steps

def self_check() -> None:
    # H=1, D=1, all gate preactivations are 0: i=f=o=0.5, g=0.
    weights = [[0.0, 0.0] for _ in range(4)]
    hidden, cell = step([2.0], [0.0], [1.0], weights, [0.0] * 4)
    assert math.isclose(cell[0], 0.5, abs_tol=1e-12)
    assert math.isclose(hidden[0], 0.5 * math.tanh(0.5), abs_tol=1e-12)
    assert math.isclose(retention(0.99, 100), 0.3660323412732292, abs_tol=1e-12)
    # Input gate and candidate can write: g=tanh(2), i≈1, f≈0, o≈1
    _, cell = step([1.0], [0.0], [1.0], weights, [20,-20,2,20])
    assert math.isclose(cell[0], math.tanh(2), rel_tol=1e-8)

if __name__ == "__main__":
    self_check()
    print("mini LSTM step: deterministic assertions passed")
