"""Pure-Python FlashAttention forward *concept* demo (no GPU kernel or speed claim).

The routines use one attention head, rows of Python floats, and optional causal
self-attention. This is intentionally transparent, not an optimized implementation.
"""
from __future__ import annotations
from math import exp, sqrt
from typing import Sequence

Matrix = Sequence[Sequence[float]]


def _shape(q: Matrix, k: Matrix, v: Matrix, causal: bool) -> tuple[int, int, int, int]:
    if not q or not k or not v:
        raise ValueError("Q, K, V must contain nonempty rows")
    n_q, n_k, d, d_v = len(q), len(k), len(q[0]), len(v[0])
    if d == 0 or d_v == 0 or len(v) != n_k:
        raise ValueError("invalid head dimensions")
    if any(len(row) != d for row in q) or any(len(row) != d for row in k):
        raise ValueError("Q/K feature dimensions must match")
    if any(len(row) != d_v for row in v):
        raise ValueError("V rows must have a consistent dimension")
    if causal and n_q != n_k:
        raise ValueError("toy causal mode requires aligned self-attention")
    return n_q, n_k, d, d_v


def reference_attention(q: Matrix, k: Matrix, v: Matrix, causal: bool = False) -> list[list[float]]:
    n_q, n_k, d, d_v = _shape(q, k, v, causal)
    scale = 1.0 / sqrt(d)
    result = []
    for i in range(n_q):
        visible = range(i + 1 if causal else n_k)
        scores = [sum(q[i][t] * k[j][t] for t in range(d)) * scale for j in visible]
        m = max(scores)  # max-subtraction makes the reference stable too
        weights = [exp(s - m) for s in scores]
        z = sum(weights)
        result.append([sum(weight * v[j][t] for j, weight in zip(visible, weights)) / z
                       for t in range(d_v)])
    return result


def streaming_attention(
    q: Matrix, k: Matrix, v: Matrix, block_size: int = 2, causal: bool = False
) -> list[list[float]]:
    n_q, n_k, d, d_v = _shape(q, k, v, causal)
    if block_size <= 0:
        raise ValueError("block_size must be positive")
    scale = 1.0 / sqrt(d)
    result = []
    for i in range(n_q):
        m = float("-inf")
        denom = 0.0
        acc = [0.0] * d_v
        for start in range(0, n_k, block_size):
            indices = [j for j in range(start, min(n_k, start + block_size))
                       if not causal or j <= i]
            if not indices:
                continue
            scores = [sum(q[i][t] * k[j][t] for t in range(d)) * scale
                      for j in indices]
            new_m = max(m, max(scores))
            alpha = exp(m - new_m) if denom else 0.0
            weights = [exp(s - new_m) for s in scores]
            denom = alpha * denom + sum(weights)
            acc = [alpha * acc[t] + sum(weight * v[j][t]
                   for j, weight in zip(indices, weights)) for t in range(d_v)]
            m = new_m
        if denom == 0:
            raise ValueError("all scores masked for a query")
        result.append([x / denom for x in acc])
    return result


def _self_check() -> None:
    q = [[1., 0.], [0., 1.], [1., 1.], [-2., 3.]]
    k = [[0., 1.], [1., 0.], [1., 1.], [2., -1.]]
    v = [[2., 7.], [6., 5.], [10., 3.], [-1., 9.]]
    for causal in (False, True):
        expected = reference_attention(q, k, v, causal)
        for block in (1, 2, 3, 5):
            actual = streaming_attention(q, k, v, block, causal)
            assert all(abs(a - b) < 1e-11 for x, y in zip(expected, actual)
                       for a, b in zip(x, y))
    print("PASS: streaming attention matches the reference for tested masks and tiles")


if __name__ == "__main__":
    _self_check()
