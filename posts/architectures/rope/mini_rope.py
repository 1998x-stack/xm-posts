"""Minimal interleaved RoPE for understanding the relative-position identity.

Teaching implementation: Python float64-like numbers, no masking, batching or fused kernels.
Not intended as a drop-in replacement for model-specific rotary kernels.
"""
from __future__ import annotations
import math

def rotate(x: tuple[float, ...], position: int, base: float = 10000.0) -> tuple[float, ...]:
    """Rotate adjacent pairs with theta_i = base**(-2*i/d)."""
    if len(x) == 0 or len(x) % 2:
        raise ValueError("RoPE requires a nonempty even rotary dimension")
    if not isinstance(position, int) or position < 0:
        raise ValueError("position must be a nonnegative integer")
    if not math.isfinite(base) or base <= 1:
        raise ValueError("base must be finite and >1")
    d = len(x)
    result = []
    for i in range(d // 2):
        angle = position * base ** (-2 * i / d)
        c, s = math.cos(angle), math.sin(angle)
        a, b = x[2*i], x[2*i+1]
        result.extend((a*c - b*s, a*s + b*c))
    return tuple(result)

def dot(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    if len(a) != len(b):
        raise ValueError("shape mismatch")
    return sum(x*y for x,y in zip(a,b))

def score(q: tuple[float, ...], k: tuple[float, ...], m: int, n: int) -> float:
    return dot(rotate(q,m), rotate(k,n))

if __name__ == "__main__":
    q, k = (1.0,0.0,0.5,-0.2), (0.3,0.7,1.0,-0.5)
    first, shifted = score(q,k,2,5), score(q,k,12,15)
    assert math.isclose(first,shifted,rel_tol=0.0,abs_tol=1e-12)
    print("score(2,5) =",first)
    print("score(12,15) =",shifted)
