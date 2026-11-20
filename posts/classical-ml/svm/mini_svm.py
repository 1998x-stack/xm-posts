"""A tiny, exact, one-dimensional hard-margin SVM calculation.

This is a restricted educational solver, not a general SVM optimizer.
Only supports linearly separable 1D classes with negatives to the left.
Requires Python >=3.11, no third-party packages.
"""
from __future__ import annotations
from math import exp, isclose
from typing import Iterable

def solve_hard_margin_1d(negatives: Iterable[float], positives: Iterable[float]) -> dict:
    neg = sorted(float(v) for v in negatives)
    pos = sorted(float(v) for v in positives)
    if not neg or not pos:
        raise ValueError("Both classes need at least one point")
    a, b = neg[-1], pos[0]
    if not a < b:
        raise ValueError("Toy solver requires all negatives left of all positives")
    w = 2.0 / (b - a)
    bias = -(a + b) / (b - a)
    alpha = w / (b - a)  # both support points have the same alpha
    assert alpha > 0
    assert all(-1.0 * (w*x+bias) >= 1-1e-12 for x in neg)
    assert all(w*x+bias >= 1-1e-12 for x in pos)
    assert isclose(alpha*(-1)*a+alpha*(+1)*b, w, rel_tol=1e-12)
    return {"w": w, "b": bias, "support": (a, b),
            "alpha": (alpha, alpha), "geometric_margin": 1.0/abs(w)}

def hinge(y: int, score: float) -> float:
    if y not in (-1,1): raise ValueError("y must be -1 or +1")
    return max(0.0, 1.0-y*score)

def rbf(x: float, z: float, gamma: float) -> float:
    if gamma <= 0: raise ValueError("gamma must be positive")
    return exp(-gamma*(x-z)**2)

def predict(model: dict, x: float) -> int:
    score=model["w"]*x+model["b"]
    if score == 0: raise ValueError("Toy decision exactly on the boundary")
    return 1 if score > 0 else -1

def smoke_test() -> None:
    m=solve_hard_margin_1d([-2,-1],[1,2])
    assert m["w"] == 1.0 and m["b"] == 0.0
    assert m["support"] == (-1.0,1.0)
    assert m["alpha"] == (0.5,0.5)
    assert m["geometric_margin"] == 1.0
    assert predict(m,0.4)==1 and predict(m,-0.4)==-1
    assert hinge(+1,0.4)==0.6
    assert isclose(rbf(0,1,0.75),0.4723665527410147)
    assert isclose(rbf(-1,2,0.5),rbf(2,-1,0.5))
    print("Educational 1D SVM assertions passed.")

if __name__=="__main__":
    smoke_test()
