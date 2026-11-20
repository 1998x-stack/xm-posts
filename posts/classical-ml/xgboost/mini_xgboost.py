"""XGBoost KDD 2016 second-order split math: deterministic teaching demo.

Only Python standard library. Not a benchmark nor a full gradient boosting trainer.
Run: python posts/classical-ml/xgboost/mini_xgboost.py
"""
from __future__ import annotations

def leaf_weight(G: float, H: float, lam: float = 1.0) -> float:
    if lam < 0 or H + lam <= 0:
        raise ValueError("require lam >= 0 and H + lam > 0")
    return -G / (H + lam)

def split_gain(GL: float, HL: float, GR: float, HR: float,
               lam: float = 1.0, gamma: float = 0.1) -> float:
    if lam < 0 or gamma < 0 or min(HL + lam, HR + lam, HL + HR + lam) <= 0:
        raise ValueError("invalid Hessian/regularization denominator")
    return 0.5 * (GL**2/(HL+lam) + GR**2/(HR+lam)
                  - (GL+GR)**2/(HL+HR+lam)) - gamma

def scan_splits(features: list[float], gradients: list[float],
                hessians: list[float], lam: float = 1.0,
                gamma: float = 0.1) -> tuple[float, float]:
    """Best positive split at one node; ignores missing/quantile/monotonic constraints."""
    if len(features) < 2 or len(features) != len(gradients) or len(features) != len(hessians):
        raise ValueError("need two or more aligned samples")
    if any(h <= 0 for h in hessians):
        raise ValueError("demo requires positive Hessian values")
    rows = sorted(zip(features, gradients, hessians))
    gt, ht = sum(gradients), sum(hessians)
    gl = hl = 0.0
    best_threshold, best_gain = float("nan"), 0.0
    for i in range(len(rows)-1):
        x, g, h = rows[i]
        gl += g
        hl += h
        next_x = rows[i+1][0]
        if x == next_x:
            continue
        gain = split_gain(gl, hl, gt-gl, ht-hl, lam, gamma)
        if gain > best_gain:
            best_threshold, best_gain = (x+next_x)/2.0, gain
    return best_threshold, best_gain

def missing_default_gains(non_missing_left: tuple[float, float],
                          non_missing_right: tuple[float, float],
                          missing: tuple[float, float],
                          lam: float = 1.0, gamma: float = 0.1) -> dict[str, float]:
    """Score both routes at a fixed threshold, not a complete missing-value learner."""
    gl, hl = non_missing_left
    gr, hr = non_missing_right
    gm, hm = missing
    return {
        "left": split_gain(gl+gm, hl+hm, gr, hr, lam, gamma),
        "right": split_gain(gl, hl, gr+gm, hr+hm, lam, gamma),
    }

def self_test() -> None:
    assert abs(leaf_weight(1, 2)+1/3) < 1e-12
    assert abs(leaf_weight(-1, 2)-1/3) < 1e-12
    assert abs(split_gain(1, 2, -1, 2) - (1/3-0.1)) < 1e-12
    split, gain = scan_splits([1,2,3,4], [.5,.5,-.5,-.5], [1,1,1,1])
    assert split == 2.5 and abs(gain - (1/3-0.1)) < 1e-12
    assert split_gain(1, 2, -1, 2, gamma=.5) < 0
    routes = missing_default_gains((.5,1),(-.5,1),(.5,1))
    assert routes["left"] != routes["right"]
    try:
        leaf_weight(1, 0, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero denominator not rejected")
    print("XGBoost math demo: deterministic assertions passed")

if __name__ == "__main__":
    self_test()
