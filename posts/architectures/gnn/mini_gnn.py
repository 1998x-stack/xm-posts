"""A deterministic four-node teaching example, not a reproduction of a trained GCN."""
from __future__ import annotations
from math import isclose, sqrt

EDGES = ((0, 1), (1, 2), (2, 3))
INPUT = (2.0, 4.0, 8.0, 6.0)


def undirected_neighbors(n: int, edges: tuple[tuple[int, int], ...]):
    adj = [set() for _ in range(n)]
    for a, b in edges:
        if not (0 <= a < n and 0 <= b < n) or a == b:
            raise ValueError("Provide distinct endpoints within range; self-loops are added separately.")
        adj[a].add(b)
        adj[b].add(a)
    return adj


def mean_with_self(values, edges=EDGES):
    """Row-normalized (D+I)^-1(A+I) without trainable weights."""
    adj = undirected_neighbors(len(values), edges)
    return tuple((values[v] + sum(values[u] for u in adj[v])) / (1 + len(adj[v]))
                 for v in range(len(values)))


def symmetric_gcn(values, edges=EDGES):
    """One scalar Kipf-Welling-style symmetric propagation (W=1, activation=identity)."""
    adj = undirected_neighbors(len(values), edges)
    deg = [1 + len(ns) for ns in adj]
    return tuple(sum(values[u] / sqrt(deg[v] * deg[u]) for u in (adj[v] | {v}))
                 for v in range(len(values)))


def demo():
    h0 = INPUT
    h1 = mean_with_self(h0)
    h2 = mean_with_self(h1)
    gcn = symmetric_gcn(h0)
    assert all(isclose(x, y, rel_tol=0, abs_tol=1e-12) for x, y in zip(h1, (3, 14/3, 6, 7)))
    assert isclose(h2[1], 41/9, abs_tol=1e-12)
    assert isclose(gcn[1], 2/sqrt(6) + 4/3 + 8/3, abs_tol=1e-12)
    # A node two hops away cannot influence B after one synchronous layer,
    # but does influence B after two layers.
    changed = (*h0[:3], 100.0)
    assert isclose(mean_with_self(changed)[1], h1[1], abs_tol=1e-12)
    assert not isclose(mean_with_self(mean_with_self(changed))[1], h2[1], abs_tol=1e-12)
    return {"input": h0, "mean_1": h1, "mean_2": h2, "gcn_1": gcn}


if __name__ == "__main__":
    for key, value in demo().items():
        print(key, tuple(round(x, 4) for x in value))
