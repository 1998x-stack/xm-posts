#!/usr/bin/env python3
"""Minimal stochastic-gradient updates: educational, deterministic and dependency-free.

Python 3.11+ standard library. Batch gradients are assumed precomputed at
THE SAME parameter vector. Values are finite 1-D vectors, not autograd tensors.
Not a reproduction of Bottou (2010) benchmark software or training hardware.
"""
from __future__ import annotations
from math import isfinite


def _validate(theta: list[float], grads: list[list[float]], lr: float) -> None:
    if not theta or not grads or not isfinite(lr) or lr <= 0:
        raise ValueError("nonempty parameters/batch and positive finite lr required")
    if any(len(g) != len(theta) for g in grads):
        raise ValueError("gradient shapes must match parameter shape")
    if any(not isfinite(x) for x in theta):
        raise ValueError("parameters must be finite")
    if any(not isfinite(x) for g in grads for x in g):
        raise ValueError("gradients must be finite")


def mean_gradient(batch_gradients: list[list[float]]) -> list[float]:
    """Average per-example gradients: shape (batch, d) -> (d,)."""
    if not batch_gradients:
        raise ValueError("empty batch")
    d = len(batch_gradients[0])
    if d == 0 or any(len(g) != d for g in batch_gradients):
        raise ValueError("batch must contain nonempty, equal-width vectors")
    if any(not isfinite(x) for g in batch_gradients for x in g):
        raise ValueError("all gradients must be finite")
    return [sum(g[j] for g in batch_gradients) / len(batch_gradients) for j in range(d)]


def sgd_step(theta: list[float], batch_gradients: list[list[float]], lr: float) -> list[float]:
    """Vanilla SGD: theta - lr * mean_i grad_i, without momentum or decay."""
    _validate(theta, batch_gradients, lr)
    gradient = mean_gradient(batch_gradients)
    return [x - lr * g for x, g in zip(theta, gradient)]


def decaying_step_size(t: int, *, numerator: float = 0.5, offset: float = 1.0) -> float:
    """Positive harmonic schedule eta_t = numerator / (t + offset), t>=0."""
    if t < 0 or offset <= 0 or numerator <= 0:
        raise ValueError("t>=0, offset>0 and numerator>0 required")
    return numerator / (t + offset)


class MomentumSGD:
    """Separate later variant: v_t = mu*v_(t-1)+g_t, theta_t = theta_(t-1)-lr*v_t.

    This is a straightforward educational convention (no Nesterov, no dampening).
    It is NOT the plain SGD rule or a torch.optim.SGD full API clone.
    """

    def __init__(self, dimensions: int, momentum: float = 0.9):
        if dimensions <= 0 or not (0 <= momentum < 1):
            raise ValueError("invalid dimensions or momentum")
        self.momentum = momentum
        self.velocity = [0.0] * dimensions

    def step(self, theta: list[float], batch_gradients: list[list[float]], lr: float) -> list[float]:
        _validate(theta, batch_gradients, lr)
        if len(theta) != len(self.velocity):
            raise ValueError("state shape differs from parameter shape")
        g = mean_gradient(batch_gradients)
        self.velocity = [self.momentum * v + u for v, u in zip(self.velocity, g)]
        return [x - lr * v for x, v in zip(theta, self.velocity)]


if __name__ == "__main__":
    # For ell_i(theta)=1/2*(theta-a_i)^2 and a=[-3,1,3,7] at theta=0:
    gradients = [[3.0], [-1.0], [-3.0], [-7.0]]
    assert mean_gradient(gradients) == [-2.0]
    assert sgd_step([0.0], gradients, 0.1) == [0.2]
    assert sgd_step([0.0], gradients[:1], 0.1) == [-0.30000000000000004]
    print("SGD math examples passed.")
