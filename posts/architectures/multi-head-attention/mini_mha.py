"""Tiny multi-head self-attention reference using only the Python standard library.

Vaswani et al. 2017, §§3.2.1–3.2.3: https://arxiv.org/abs/1706.03762
No batching, biases, dropout, position encoding, training or GPU kernels.
Inputs X: [T, D], projection matrices: [D, D], returns [T, D].
"""
from __future__ import annotations
from math import exp, sqrt, isclose
from typing import Sequence

Matrix = list[list[float]]


def identity(n: int) -> Matrix:
    if n < 1:
        raise ValueError("n must be positive")
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def project(x: Sequence[Sequence[float]], w: Sequence[Sequence[float]]) -> Matrix:
    if not x or not w:
        raise ValueError("matrices must be nonempty")
    d, d_out = len(x[0]), len(w[0])
    if d < 1 or d_out < 1 or len(w) != d:
        raise ValueError("incompatible projection dimensions")
    if any(len(row) != d for row in x) or any(len(row) != d_out for row in w):
        raise ValueError("ragged matrix")
    return [[sum(row[k] * w[k][j] for k in range(d)) for j in range(d_out)]
            for row in x]


def stable_softmax(logits: Sequence[float]) -> list[float]:
    if not logits:
        raise ValueError("empty logits")
    zmax = max(logits)
    exp_scores = [exp(value - zmax) for value in logits]
    denom = sum(exp_scores)
    return [value / denom for value in exp_scores]


def self_attention(x: Matrix, wq: Matrix, wk: Matrix, wv: Matrix,
                   wo: Matrix, *, heads: int, causal: bool) -> tuple[Matrix, list[Matrix]]:
    """Return (output [T,D], attention weights [heads,T,T]).

    All Q/K/V total widths equal D; per-head width is D//heads.
    For causal attention, future positions are excluded before softmax.
    """
    if not x or not x[0]:
        raise ValueError("empty input")
    d = len(x[0])
    if heads < 1 or d % heads:
        raise ValueError("head count must divide the model width")
    q, k, v = project(x, wq), project(x, wk), project(x, wv)
    if any(len(row) != d for row in (q + k + v)):
        raise ValueError("Q/K/V total projected width must equal model width")
    t, dh = len(x), d // heads
    concat: Matrix = [[0.0] * d for _ in range(t)]
    weights: list[Matrix] = []
    for h in range(heads):
        start, end = h * dh, (h + 1) * dh
        head_weights: Matrix = []
        for i in range(t):
            allowed = list(range(i + 1)) if causal else list(range(t))
            logits = [sum(q[i][z] * k[j][z] for z in range(start, end))
                      / sqrt(dh) for j in allowed]
            probs = [0.0] * t
            for j, prob in zip(allowed, stable_softmax(logits)):
                probs[j] = prob
            head_weights.append(probs)
            for z in range(start, end):
                concat[i][z] = sum(probs[j] * v[j][z] for j in range(t))
        weights.append(head_weights)
    return project(concat, wo), weights


def self_test() -> None:
    x = [[1.0, 0.0], [0.0, 1.0]]
    w = identity(2)
    y, a = self_attention(x, w, w, w, w, heads=1, causal=True)
    assert a[0][0] == [1.0, 0.0] and y[0] == x[0]
    assert isclose(sum(a[0][1]), 1.0, abs_tol=1e-12)
    expected = exp(1 / sqrt(2)) / (1 + exp(1 / sqrt(2)))
    assert isclose(y[1][1], expected, rel_tol=1e-12)
    yfull, afull = self_attention(x, w, w, w, w, heads=1, causal=False)
    assert afull[0][0][1] > 0.0 and yfull[0][1] > 0.0
    z = [[1., 2., 3., 4.], [4., 3., 2., 1.]]
    out, heads = self_attention(z, identity(4), identity(4), identity(4),
                                identity(4), heads=2, causal=True)
    assert len(heads) == 2 and len(out) == 2 and len(out[0]) == 4
    for head in heads:
        for i, row in enumerate(head):
            assert isclose(sum(row), 1.0, abs_tol=1e-12)
            assert all(v == 0 for v in row[i + 1:])
    for invalid_heads in [0, 3]:
        try:
            self_attention(z, identity(4), identity(4), identity(4),
                           identity(4), heads=invalid_heads, causal=True)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid head count was accepted")


if __name__ == "__main__":
    self_test()
    print("MHA deterministic tests passed")
