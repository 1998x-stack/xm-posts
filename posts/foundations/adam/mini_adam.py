#!/usr/bin/env python3
"""Minimal, deterministic Adam/AdamW/AMSGrad update for teaching.

Python 3.11+ standard library only. This module is an optimizer *step*, not a
training loop, benchmarking reproduction, or performance-optimized GPU kernel.
The equations use epsilon outside sqrt(v_hat), as in Adam Algorithm 1.
"""
from __future__ import annotations
import math


class Adam:
    """Coordinatewise first/second raw moment optimizer with explicit state."""

    def __init__(
        self,
        dimensions: int,
        *,
        lr: float = 1e-3,
        betas: tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.0,
        decoupled_weight_decay: bool = False,
        amsgrad: bool = False,
    ):
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        if lr <= 0 or eps <= 0 or weight_decay < 0:
            raise ValueError("invalid lr, eps or weight_decay")
        if len(betas) != 2 or any(not 0 <= b < 1 for b in betas):
            raise ValueError("betas must lie in [0, 1)")
        self.dimensions = dimensions
        self.lr, self.beta1, self.beta2 = lr, *betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.decoupled_weight_decay = decoupled_weight_decay
        self.amsgrad = amsgrad
        self.m = [0.0] * dimensions
        self.v = [0.0] * dimensions
        self.v_max = [0.0] * dimensions
        self.t = 0

    def step(self, parameters: list[float], gradients: list[float]) -> list[float]:
        """Return new parameters; inputs remain untouched.

        Coupled L2: add lambda*theta to g *before* moment updates.
        Decoupled AdamW: use loss gradient for moments and apply -lr*lambda*theta
        to the original parameter, separately from the adaptive step.
        AMSGrad: maximum of UNCORRECTED second-moment estimates, bias-corrected
        after taking the maximum (matching the common optimizer convention).
        """
        if len(parameters) != self.dimensions or len(gradients) != self.dimensions:
            raise ValueError("parameter/gradient dimensions differ from state")
        if any(not math.isfinite(x) for x in parameters + gradients):
            raise ValueError("all values must be finite")
        self.t += 1
        out: list[float] = []
        for i, (theta, gradient) in enumerate(zip(parameters, gradients)):
            g = gradient
            if not self.decoupled_weight_decay:
                g += self.weight_decay * theta
            self.m[i] = self.beta1 * self.m[i] + (1.0 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1.0 - self.beta2) * g * g
            m_hat = self.m[i] / (1.0 - self.beta1**self.t)
            if self.amsgrad:
                self.v_max[i] = max(self.v_max[i], self.v[i])
                raw_v = self.v_max[i]
            else:
                raw_v = self.v[i]
            v_hat = raw_v / (1.0 - self.beta2**self.t)
            adaptive_step = self.lr * m_hat / (math.sqrt(v_hat) + self.eps)
            decay_step = self.lr * self.weight_decay * theta if self.decoupled_weight_decay else 0.0
            out.append(theta - adaptive_step - decay_step)
        return out


if __name__ == "__main__":
    opt = Adam(2)
    out = opt.step([3.0, -2.0], [2.0, -4.0])
    assert math.isclose(out[0], 2.999, abs_tol=1e-8)
    assert math.isclose(out[1], -1.999, abs_tol=1e-8)
    assert opt.t == 1
    print("Adam first-step numerical assertions passed.")
