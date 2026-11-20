#!/usr/bin/env python3
"""Deterministic, dependency-free checks for a rearrangement-inequality explainer.

This is a small teaching example, not a solver for large assignment problems.
Run: python posts/foundations/rearrangement-inequalities/mini_rearrangement.py
"""
from itertools import permutations
from math import prod


def dot(a, b):
    assert len(a) == len(b)
    return sum(x * y for x, y in zip(a, b))


def triple(a, b, c):
    assert len(a) == len(b) == len(c)
    return sum(x * y * z for x, y, z in zip(a, b, c))


def trace_three_rank_one(u, v, w):
    # tr((uu^T)(vv^T)(ww^T)) = (u.v)(v.w)(w.u).
    return dot(u, v) * dot(v, w) * dot(w, u)


def main():
    a = (3, 2, 1)
    b = (3, 2, 1)
    c = (3, 2, 1)
    pair_vals = [dot(a, p) for p in permutations(b)]
    assert min(pair_vals) == 10
    assert max(pair_vals) == 14
    assert dot(a, (2, 3, 1)) == 13

    scores = {(pb, pc): triple(a, pb, pc)
              for pb in permutations(b) for pc in permutations(c)}
    assert len(scores) == 36
    assert min(scores.values()) == 18
    assert max(scores.values()) == 36
    assert scores[((3, 2, 1), (3, 2, 1))] == 36
    assert scores[((3, 2, 1), (1, 2, 3))] == 20
    assert scores[((2, 1, 3), (1, 3, 2))] == 18
    assert sum(1 for s in scores.values() if s == 18) == 2

    # Three positive-semidefinite 2x2 rank-one matrices:
    # A = uu^T, B = vv^T, C = ww^T; their triple trace is negative.
    u, v, w = (1, 0), (1, 1), (-1, 2)
    assert trace_three_rank_one(u, v, w) == -1

    # Negatives are allowed in the *two*-sequence rearrangement theorem.
    x, y = (3, -1, -4), (5, 0, -2)
    rearranged = [dot(x, p) for p in permutations(y)]
    assert min(rearranged) == dot(x, tuple(reversed(y)))
    assert max(rearranged) == dot(x, y)
    assert prod(a) * prod(b) * prod(c) == 216  # independent of permutations
    print("PASS: two sequences, all 36 triple pairings, and PSD trace counterexample")


if __name__ == "__main__":
    main()
