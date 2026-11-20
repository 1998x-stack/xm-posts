"""One-dimensional deterministic decision-stump examples. Standard library only.

This is NOT a complete CART, ID3, or C4.5 implementation.
Python 3.11+; no dataset or third-party dependencies.
"""
from __future__ import annotations
from math import log2, isfinite, isclose
from typing import Sequence

X = (1., 2., 3., 4., 5., 6., 7., 8.)
Y = (0, 0, 1, 0, 1, 1, 1, 1)

def _check(x: Sequence[float], y: Sequence[float]) -> None:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Need at least two paired observations")
    if not all(isfinite(float(v)) for v in x):
        raise ValueError("Features must be finite")

def gini(labels: Sequence[int]) -> float:
    if not labels: raise ValueError("Empty node")
    counts = {c: labels.count(c) for c in set(labels)}
    return 1.0 - sum((v/len(labels))**2 for v in counts.values())

def entropy(labels: Sequence[int]) -> float:
    if not labels: raise ValueError("Empty node")
    counts = {c: labels.count(c) for c in set(labels)}
    return -sum((v/len(labels))*log2(v/len(labels)) for v in counts.values())

def midpoints(x: Sequence[float]) -> list[float]:
    unique = sorted(set(float(v) for v in x))
    return [(a+b)/2 for a,b in zip(unique,unique[1:])]

def best_gini_split(x: Sequence[float], y: Sequence[int]) -> dict:
    _check(x,y)
    best=[]
    for t in midpoints(x):
        left=[v for xx,v in zip(x,y) if xx<=t]
        right=[v for xx,v in zip(x,y) if xx>t]
        if left and right:
            score=(len(left)*gini(left)+len(right)*gini(right))/len(y)
            best.append((score,t,len(left),len(right)))
    if not best: raise ValueError("Constant feature")
    weighted,t,nl,nr=min(best)
    return {"threshold":t,"parent_gini":gini(y),"weighted_gini":weighted,
            "gain":gini(y)-weighted,"left_size":nl,"right_size":nr}

def squared_error(values: Sequence[float]) -> float:
    if not values: raise ValueError("Empty leaf")
    mean=sum(values)/len(values)
    return sum((v-mean)**2 for v in values)

def best_sse_split(x: Sequence[float], y: Sequence[float]) -> dict:
    _check(x,y)
    if not all(isfinite(float(v)) for v in y):
        raise ValueError("Labels must be finite")
    all_scores=[]
    for t in midpoints(x):
        left=[v for xx,v in zip(x,y) if xx<=t]
        right=[v for xx,v in zip(x,y) if xx>t]
        if left and right:
            all_scores.append((squared_error(left)+squared_error(right),t,
                               sum(left)/len(left),sum(right)/len(right)))
    if not all_scores: raise ValueError("Constant feature")
    loss,t,ml,mr=min(all_scores)
    return {"threshold":t,"sse":loss,"left_mean":ml,"right_mean":mr,
            "parent_sse":squared_error(y)}

def complexity_cost(risk: float, leaves: int, alpha: float) -> float:
    if leaves < 1 or alpha < 0: raise ValueError("Invalid leaf count or alpha")
    return risk+alpha*leaves

def smoke_test() -> None:
    m=best_gini_split(X,Y)
    assert m["threshold"]==4.5
    assert isclose(m["parent_gini"],0.46875)
    assert isclose(m["weighted_gini"],0.1875)
    assert isclose(m["gain"],0.28125)
    assert gini([0,0,0])==0 and isclose(entropy([0,1]),1)
    r=best_sse_split([1,2,3,4],[2,2,8,8])
    assert r["threshold"]==2.5 and r["sse"]==0 and r["parent_sse"]==36
    assert isclose(complexity_cost(0.1875,2,0.28125),complexity_cost(0.46875,1,0.28125))
    print("Decision tree toy assertions passed.")

if __name__=="__main__":
    smoke_test()
