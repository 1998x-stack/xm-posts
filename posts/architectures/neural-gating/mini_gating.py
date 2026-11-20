"""Small deterministic scalar gating examples; no framework dependency.
This is not a reproduction of LSTM/GRU/GLU paper experiments.
"""
from __future__ import annotations
import math

def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    z = math.exp(x)
    return z / (1.0 + z)

def highway(x: float, candidate: float, transform_gate: float) -> float:
    assert 0.0 <= transform_gate <= 1.0
    return transform_gate * candidate + (1.0 - transform_gate) * x

def gru_mix(previous: float, candidate: float, keep_gate: float) -> float:
    return highway(candidate, previous, keep_gate)

def glu(a: float, b: float) -> float:
    return a * sigmoid(b)

def silu(x: float) -> float:
    return x * sigmoid(x)

def swiglu(a: float, b: float) -> float:
    return silu(a) * b

def finite_difference(f, x: float, eps: float = 1e-6) -> float:
    return (f(x + eps) - f(x - eps)) / (2.0 * eps)

def self_check() -> None:
    assert sigmoid(-1e3) == 0.0
    assert sigmoid(1e3) == 1.0
    assert math.isclose(sigmoid(0.0), 0.5, abs_tol=1e-15)
    assert highway(0.8, -0.4, 0.0) == 0.8
    assert highway(0.8, -0.4, 1.0) == -0.4
    assert math.isclose(highway(0.8, -0.4, 0.35), 0.38, abs_tol=1e-12)
    assert math.isclose(gru_mix(0.8, -0.4, 0.65), 0.38, abs_tol=1e-12)
    assert silu(-1.0) < 0.0 and silu(3.0) > 1.0
    assert math.isclose(glu(3.0, 0.0), 1.5, abs_tol=1e-12)
    assert math.isclose(swiglu(0.0, 100.0), 0.0, abs_tol=1e-12)
    # y(x) = sigmoid(x) * x; product rule gives g+x*g*(1-g).
    x = 0.7
    g = sigmoid(x)
    analytic = g + x * g * (1.0 - g)
    assert math.isclose(finite_difference(lambda t: t * sigmoid(t), x), analytic, abs_tol=1e-9)

if __name__ == "__main__":
    self_check()
    print("neural gating: deterministic assertions passed")
