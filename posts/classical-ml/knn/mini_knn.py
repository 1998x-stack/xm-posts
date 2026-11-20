"""A deterministic, stdlib-only kNN classroom implementation.

This is not a benchmark or a reproduction of Cover & Hart's experiments.
Run: python posts/classical-ml/knn/mini_knn.py
"""
from __future__ import annotations
from math import dist, isclose
from typing import Sequence

POINTS = (
    (1.0, 1.0), (2.0, 1.0), (2.0, 2.0), (3.0, 2.0), (3.0, 4.0),
    (6.0, 4.0), (7.0, 4.0), (6.0, 5.0), (7.0, 6.0), (8.0, 5.0),
)
LABELS = ("A", "A", "A", "A", "A", "B", "B", "B", "B", "B")
QUERY = (4.4, 4.1)


def neighbors(train: Sequence[Sequence[float]],
              query: Sequence[float], k: int) -> list[tuple[int, float]]:
    if not train or not 1 <= k <= len(train):
        raise ValueError("k must be between 1 and the number of training points")
    if any(len(p) != len(query) for p in train):
        raise ValueError("all points must have the same dimension")
    return sorted(((i, dist(p, query)) for i, p in enumerate(train)),
                  key=lambda item: (item[1], item[0]))[:k]


def vote_scores(train: Sequence[Sequence[float]],
                labels: Sequence[str],
                query: Sequence[float],
                k: int = 3,
                weights: str = "uniform") -> dict[str, float]:
    if len(labels) != len(train):
        raise ValueError("labels must match the number of training points")
    if weights not in ("uniform", "distance"):
        raise ValueError("weights must be uniform or distance")
    chosen = neighbors(train, query, k)
    # Exact duplicates: vote among zero-distance neighbors, avoiding infinite weights.
    if weights == "distance" and any(d == 0.0 for _, d in chosen):
        chosen = [(i, d) for i, d in chosen if d == 0.0]
    scores = {c: 0.0 for c in sorted(set(labels))}
    for i, d in chosen:
        weight = 1.0 if weights == "uniform" or d == 0.0 else 1.0 / (d + 1e-9)
        scores[labels[i]] += weight
    return scores


def classify(train: Sequence[Sequence[float]],
             labels: Sequence[str],
             query: Sequence[float], k: int = 3,
             weights: str = "uniform") -> str:
    scores = vote_scores(train, labels, query, k, weights)
    # Deterministic tie-break by lexicographic class label.
    return sorted(scores, key=lambda c: (-scores[c], c))[0]


def regress(train: Sequence[Sequence[float]],
            targets: Sequence[float],
            query: Sequence[float], k: int = 3) -> float:
    if len(targets) != len(train):
        raise ValueError("targets must match the number of training points")
    return sum(targets[i] for i, _ in neighbors(train, query, k)) / k


def self_test() -> None:
    assert [i for i, _ in neighbors(POINTS, QUERY, 3)] == [4, 5, 7]
    assert classify(POINTS, LABELS, QUERY, k=1) == "A"
    assert classify(POINTS, LABELS, QUERY, k=3) == "B"
    assert classify(POINTS, LABELS, QUERY, k=5) == "B"
    score = vote_scores(POINTS, LABELS, QUERY, k=3, weights="distance")
    assert isclose(score["A"], 0.712470499371482, abs_tol=1e-10)
    assert isclose(score["B"], 1.1685175715688079, abs_tol=1e-10)
    assert classify(POINTS, LABELS, QUERY, k=3, weights="distance") == "B"
    assert regress(((0.0,), (1.0,), (2.0,)), (2.0, 4.0, 6.0), (1.0,), 3) == 4.0
    assert classify(((0.0,), (0.0,), (2.0,)), ("A", "A", "B"), (0.0,), 3, "distance") == "A"
    try:
        classify(POINTS, LABELS, QUERY, k=0)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid k must fail")


if __name__ == "__main__":
    self_test()
    print("KNN TOY OK")
