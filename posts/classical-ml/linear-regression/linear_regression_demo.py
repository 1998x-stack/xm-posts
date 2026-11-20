"""Dependency-free univariate OLS demonstration; educational data only."""
from __future__ import annotations


def ols(x: list[float], y: list[float]) -> tuple[float, float]:
    """Return (intercept, slope); require varied finite x."""
    from math import isfinite
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("x and y must have equal lengths >= 2")
    if not all(isfinite(float(v)) for v in x + y):
        raise ValueError("x and y must be finite")
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    denom = sum((v - mx) ** 2 for v in x)
    if denom == 0:
        raise ValueError("x must have nonzero variance")
    slope = sum((a - mx) * (b - my) for a, b in zip(x, y)) / denom
    return my - slope * mx, slope


def rss(x: list[float], y: list[float], b: float, w: float) -> float:
    return sum((yi - (b + w * xi)) ** 2 for xi, yi in zip(x, y))


def gradient_mse(x: list[float], y: list[float], b: float, w: float) -> tuple[float, float]:
    n = len(x)
    residuals = [b + w * xi - yi for xi, yi in zip(x, y)]
    return 2 * sum(residuals) / n, 2 * sum(xi * r for xi, r in zip(x, residuals)) / n


def gradient_descent(x: list[float], y: list[float], lr: float = 0.08, steps: int = 2500) -> tuple[float, float]:
    b = w = 0.0
    for _ in range(steps):
        gb, gw = gradient_mse(x, y, b, w)
        b, w = b - lr * gb, w - lr * gw
    return b, w


if __name__ == "__main__":
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 2.0, 2.0, 4.0]
    b, w = ols(x, y)
    assert abs(b - 0.9) < 1e-12 and abs(w - 0.9) < 1e-12
    residuals = [yi - (b + w * xi) for xi, yi in zip(x, y)]
    assert abs(sum(residuals)) < 1e-12
    assert abs(sum(xi * ri for xi, ri in zip(x, residuals))) < 1e-12
    assert abs(rss(x, y, b, w) - 0.7) < 1e-12
    tss = sum((yi - sum(y) / len(y)) ** 2 for yi in y)
    assert abs(tss - 4.75) < 1e-12
    assert abs((1 - rss(x, y, b, w) / tss) - (1 - 0.7 / 4.75)) < 1e-12
    gd_b, gd_w = gradient_descent(x, y)
    assert abs(gd_b - b) < 1e-7 and abs(gd_w - w) < 1e-7
    try:
        ols([2.0, 2.0], [1.0, 3.0])
    except ValueError:
        pass
    else:
        raise AssertionError("constant x should be rejected")
    print(f"OLS: intercept={b:.1f}, slope={w:.1f}, RSS={rss(x, y, b, w):.1f}")
    print("OK: normal equations, R² and gradient descent checks")
