"""Minimal standard-library educational MoE operations, not a GPU reproduction."""
from __future__ import annotations
from math import exp, ceil, isclose, isfinite


def route_topk(logits: list[float], k: int) -> list[float]:
    n = len(logits)
    if not 1 <= k <= n or any(not isfinite(x) for x in logits):
        raise ValueError("bad logits/k")
    chosen = sorted(range(n), key=lambda i: (-logits[i], i))[:k]
    maximum = max(logits[i] for i in chosen)
    terms = [exp(logits[i] - maximum) for i in chosen]
    normalizer = sum(terms)
    result = [0.0] * n
    for i, value in zip(chosen, terms):
        result[i] = value / normalizer
    return result


def combine_scalar(x: float, gate: list[float], experts: list[tuple[float, float]]) -> float:
    if not experts or len(gate) != len(experts) or not isclose(sum(gate), 1.0, abs_tol=1e-12):
        raise ValueError("invalid expert/gate configuration")
    return sum(w * (a*x+b) for w, (a,b) in zip(gate, experts) if w)


def dispatch(scores: list[list[float]], k: int, capacity_factor: float = 1.0) -> dict:
    if not scores or not scores[0] or not isfinite(capacity_factor) or capacity_factor <= 0:
        raise ValueError("invalid batch/capacity")
    n, t = len(scores[0]), len(scores)
    if any(len(row) != n for row in scores):
        raise ValueError("ragged scores")
    cap = ceil(capacity_factor*t*k/n)
    counts = [0]*n
    overflow = 0
    assigned = []
    for row in scores:
        gate = route_topk(row, k)
        for i, weight in enumerate(gate):
            if weight:
                if counts[i] >= cap:
                    gate[i] = 0.0  # dropped, not rerouted/renormalized
                    overflow += 1
                else:
                    counts[i] += 1
        assigned.append(gate)
    return {"capacity": cap, "counts": counts, "overflow": overflow,
            "candidates": t*k, "gates": assigned}


def importance(gates: list[list[float]]) -> list[float]:
    if not gates or not gates[0] or any(len(g) != len(gates[0]) for g in gates):
        raise ValueError("inconsistent gates")
    return [sum(g[i] for g in gates) for i in range(len(gates[0]))]


def cv_squared(values: list[float]) -> float:
    if not values or any(x < 0 or not isfinite(x) for x in values):
        raise ValueError("invalid values")
    mean = sum(values)/len(values)
    if mean == 0:
        raise ValueError("zero mean")
    return sum((x-mean)**2 for x in values)/len(values)/mean**2


def self_test() -> None:
    g = route_topk([2., 1.5, .1, -.4], 2)
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in
               zip(g,[.6224593312018546,.37754066879814546,0.,0.]))
    assert route_topk([1.,1.,0.],1) == [1.,0.,0.]
    assert isclose(combine_scalar(3.,g,[(1.,0.),(.5,1.),(2.,0.),(-1.,0.)]),
                   g[0]*3 + g[1]*2.5)
    scores = [[3,2,1,0],[2.8,2.5,0,0],[2.5,1,2.1,0],[3,.2,2.1,0],
              [.1,2.6,2.4,0],[1,2.7,.2,0]]
    r = dispatch(scores,2,1)
    assert sum(r["counts"])+r["overflow"] == 12
    assert max(r["counts"]) <= r["capacity"] == 3
    assert cv_squared([4,0,0,0]) == 3.
    assert cv_squared([1,1,1,1]) == 0.
    assert route_topk([100000.,0.,-100000.],1) == [1.,0.,0.]


if __name__ == "__main__":
    self_test()
    print("MoE educational checks passed; no GPU throughput claim.")
