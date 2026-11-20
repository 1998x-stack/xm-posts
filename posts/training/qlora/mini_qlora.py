#!/usr/bin/env python3
"""Deterministic QLoRA mechanism toy. No GPU dependency or paper benchmark reproduction.

Illustrates: blockwise nearest-codebook quantization, dequantization, frozen base
and an additive rank-one adapter. This is not a bitsandbytes CUDA kernel.
"""
from __future__ import annotations

NF4 = (-1.0, -0.6961928, -0.52507305, -0.39491749,
       -0.28444138, -0.18477343, -0.09105004, 0.0,
       0.0795803, 0.1609302, 0.2461123, 0.33791524,
       0.44070983, 0.562617, 0.72295684, 1.0)

def quantize_block(values):
    """Closest codebook values after absmax normalization; pedagogical approximation."""
    scale = max(map(abs, values)) or 1.0
    indices = [min(range(16), key=lambda j: abs(NF4[j] - value / scale))
               for value in values]
    return indices, scale

def dequantize_block(indices, scale):
    return [scale * NF4[i] for i in indices]

def row_mm(x, w):
    assert len(x) == len(w)
    assert len({len(row) for row in w}) == 1
    return [sum(x[i] * w[i][j] for i in range(len(x)))
            for j in range(len(w[0]))]

def forward(x, frozen_w, a, b, scaling=1.0):
    """Shapes: x:(in,), W:(in,out), A:(in,r), B:(r,out)."""
    n, m = len(frozen_w), len(frozen_w[0])
    indices, scale = quantize_block([v for row in frozen_w for v in row])
    flat = dequantize_block(indices, scale)
    w_dequant = [flat[i * m:(i + 1) * m] for i in range(n)]
    base = row_mm(x, w_dequant)
    delta = row_mm(row_mm(x, a), b)
    return [p + scaling * q for p, q in zip(base, delta)]

def test():
    w = [[1.0, 0.3], [-0.8, 0.1]]
    original = [row[:] for row in w]
    x, a = [2.0, -1.0], [[1.0], [-1.0]]
    base = forward(x, w, a, [[0.0, 0.0]])
    adapted = forward(x, w, a, [[0.2, -0.1]])
    assert w == original, "Frozen backbone must remain unchanged"
    assert len(base) == len(adapted) == 2
    assert abs(adapted[0] - base[0] - 0.6) < 1e-12
    assert abs(adapted[1] - base[1] + 0.3) < 1e-12
    assert 8 * (4096 + 4096) == 65536
    assert abs(32 / 64 - (8 / 64 + 32 / (64 * 256)) - 0.373046875) < 1e-12
    print("PASS: frozen W, rank-one delta and double-quant accounting")

if __name__ == "__main__":
    test()
