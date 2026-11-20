"""Deterministic embedding math primitives. Educational example, not a trained model."""
from __future__ import annotations
from math import sqrt, isfinite
from collections.abc import Mapping, Sequence

def _vec(xs: Sequence[float]) -> list[float]:
    if not xs:
        raise ValueError("empty vector")
    result = [float(x) for x in xs]
    if not all(isfinite(x) for x in result):
        raise ValueError("non-finite vector")
    return result

def lookup(ids: Sequence[int], matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    if not matrix:
        raise ValueError("empty lookup table")
    rows = [_vec(row) for row in matrix]
    d = len(rows[0])
    if any(len(r) != d for r in rows):
        raise ValueError("inconsistent embedding dimensions")
    if any(type(i) is not int or not 0 <= i < len(rows) for i in ids):
        raise ValueError("token id out of range")
    return [rows[i][:] for i in ids]

def masked_mean(hidden: Sequence[Sequence[float]], mask: Sequence[int]) -> list[float]:
    if not hidden or len(hidden) != len(mask):
        raise ValueError("hidden and mask must be aligned and nonempty")
    rows = [_vec(row) for row in hidden]
    d = len(rows[0])
    if any(len(row) != d for row in rows):
        raise ValueError("dimension mismatch")
    if any(type(m) is not int or m not in (0, 1) for m in mask):
        raise ValueError("mask values must be 0 or 1")
    count = sum(mask)
    if count == 0:
        raise ValueError("all padding has no mean")
    return [sum(mask[i] * rows[i][j] for i in range(len(rows))) / count for j in range(d)]

def normalize(xs: Sequence[float]) -> list[float]:
    vec = _vec(xs)
    norm = sqrt(sum(x*x for x in vec))
    if norm == 0:
        raise ValueError("zero vector has no cosine direction")
    return [x / norm for x in vec]

def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    u, v = normalize(a), normalize(b)
    if len(u) != len(v):
        raise ValueError("dimension mismatch")
    return sum(x*y for x,y in zip(u,v))

def topk(query: Sequence[float], corpus: Mapping[str, Sequence[float]], k: int) -> list[tuple[str,float]]:
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    pairs = [(key,cosine(query,vector)) for key,vector in corpus.items()]
    return sorted(pairs,key=lambda x:(-x[1],x[0]))[:k]

if __name__ == "__main__":
    states = lookup([0,1,2], [[1.,0.],[0.,1.],[0.,0.]])
    q = masked_mean(states,[1,1,0])
    assert abs(cosine(q,[1.,1.])-1.) < 1e-12
    assert topk(q,{"B":[-1.,0.],"A":[1.,1.]},2)[0][0] == "A"
    print("embedding examples passed")
