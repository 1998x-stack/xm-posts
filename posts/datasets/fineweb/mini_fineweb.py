#!/usr/bin/env python3
"""Teaching-only FineWeb math checks; not a DataTrove or paper-training reproduction.

Original research: Penedo et al. (NeurIPS 2024), §3.4 and §4.
The LSH probability formula assumes ideal independent hash functions.
"""
from __future__ import annotations
from collections import Counter
from math import isclose


def shingles(text: str, n: int = 5) -> set[tuple[str, ...]]:
    """Simplified whitespace tokenizer, NOT the paper's English word tokenizer."""
    words = text.lower().split()
    if n < 1:
        raise ValueError("n must be positive")
    return {tuple(words[i:i+n]) for i in range(max(0, len(words)-n+1))}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0  # Explicit teaching convention; actual implementation can differ.
    return len(a & b) / len(a | b)


def band_hit_probability(similarity: float, bands: int = 14, rows: int = 8) -> float:
    """Idealized LSH recall proxy P(at least one matching band)."""
    if not (0 <= similarity <= 1 and bands > 0 and rows > 0):
        raise ValueError("invalid LSH arguments")
    return 1 - (1 - similarity ** rows) ** bands


def score_threshold(scores: list[int], minimum: int) -> list[int]:
    return [score for score in scores if score >= minimum]


def remove_duplicate_exact_within_snapshots(snapshots: dict[str, list[str]]) -> dict[str, list[str]]:
    """Exact duplicate toy example; separate snapshots deliberately remain independent."""
    result = {}
    for snapshot, texts in snapshots.items():
        seen = set()
        result[snapshot] = []
        for text in texts:
            if text not in seen:
                result[snapshot].append(text)
                seen.add(text)
    return result


def toy_fraction_repeated_lines(lines: list[str]) -> float:
    """Illustrative ratio; not the production FineWeb filter definition."""
    if not lines:
        return 0.0
    count = Counter(lines)
    repeated_chars = sum(len(line) for line in lines if count[line] > 1)
    return repeated_chars / max(1, sum(map(len, lines)))


def self_test() -> None:
    a, b = shingles("a b c d e f"), shingles("a b c d e g")
    assert 0 <= jaccard(a, b) < 1
    assert jaccard(a, a) == 1
    assert band_hit_probability(0) == 0
    assert band_hit_probability(1) == 1
    assert 0 < band_hit_probability(.75) < 1
    assert band_hit_probability(.8) > band_hit_probability(.6)
    assert isclose(band_hit_probability(.75), 1 - (1 - .75 ** 8) ** 14)
    scores = [0, 2, 3, 4, 5, 1, 3, 2]
    assert len(score_threshold(scores, 2)) == 6
    assert len(score_threshold(scores, 3)) == 4
    assert len(score_threshold(scores, 4)) == 2
    snaps = {"new":["A","B","A"], "old":["A","C","C"]}
    out = remove_duplicate_exact_within_snapshots(snaps)
    assert out == {"new":["A","B"],"old":["A","C"]}
    assert toy_fraction_repeated_lines(["hi","hi","end"]) > 0


if __name__ == "__main__":
    self_test()
    print("fineweb teaching checks: passed (no paper reproduction)")
