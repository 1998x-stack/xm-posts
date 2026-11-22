"""Deterministic scalar teaching models, NOT a trained Mamba implementation."""
from __future__ import annotations

def gated_step(previous: float, token: float, gate: float) -> float:
    """Convex update for 0 <= gate <= 1, from Mamba Theorem 1 special case."""
    if not 0.0 <= gate <= 1.0:
        raise ValueError("gate must be in [0,1]")
    return (1.0 - gate) * previous + gate * token

def affine_combine(left: tuple[float,float], right: tuple[float,float]) -> tuple[float,float]:
    """Compose right after left: (a,b) maps h -> a*h+b."""
    a1,b1 = left
    a2,b2 = right
    return (a2*a1, a2*b1+b2)

def scan_sequential(states: list[tuple[float,float]], initial: float=0.0) -> list[float]:
    out: list[float] = []
    state=initial
    for a,b in states:
        state=a*state+b
        out.append(state)
    return out

def scan_from_prefix(states: list[tuple[float,float]], initial: float=0.0) -> list[float]:
    # Pedagogical prefix composition; not a parallel GPU implementation.
    out=[]
    prefix=(1.0,0.0)
    for pair in states:
        prefix=affine_combine(prefix,pair)
        a,b=prefix
        out.append(a*initial+b)
    return out
