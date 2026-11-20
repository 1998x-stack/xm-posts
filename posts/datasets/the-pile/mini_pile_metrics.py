"""Minimal, deterministic calculations for the The Pile tutorial.

This models byte-weighted mixture arithmetic only, NOT a reproduction of The
Pile data pipeline or 1.3B-language-model training. Python 3.11+, stdlib only.
"""
from __future__ import annotations

from math import isclose, log
from typing import Mapping


PILE_RAW_GIB = {
    "Pile-CC": 227.12,
    "PubMed Central": 90.27,
    "arXiv": 56.21,
}
PILE_EPOCHS = {"Pile-CC": 1.0, "PubMed Central": 2.0, "arXiv": 2.0}


def normalized_mixture(raw_gib: Mapping[str, float],
                       epochs: Mapping[str, float]) -> dict[str, float]:
    """Return effective byte shares, preserving dataset names."""
    if not raw_gib or set(raw_gib) != set(epochs):
        raise ValueError("raw_gib/epochs must share a nonempty key set")
    effective = {}
    for name, size in raw_gib.items():
        repeats = epochs[name]
        if size <= 0 or repeats <= 0:
            raise ValueError("sizes and repeat factors must be positive")
        effective[name] = size * repeats
    total = sum(effective.values())
    return {name: value / total for name, value in effective.items()}


def bits_per_utf8_byte(mean_nll_nats_per_token: float,
                       token_count: int, byte_count: int) -> float:
    """Convert a mean natural-log token loss to bits per UTF-8 byte."""
    if token_count <= 0 or byte_count <= 0 or mean_nll_nats_per_token < 0:
        raise ValueError("positive lengths and nonnegative loss required")
    return mean_nll_nats_per_token * token_count / (byte_count * log(2))


def paper_examples() -> None:
    p = normalized_mixture(PILE_RAW_GIB, PILE_EPOCHS)
    assert isclose(sum(p.values()), 1.0, abs_tol=1e-12)
    assert p["Pile-CC"] > p["PubMed Central"] > p["arXiv"]
    assert isclose(bits_per_utf8_byte(log(2), 4, 8), 0.5, abs_tol=1e-12)
    assert isclose(90.27 * 2, 180.54, abs_tol=1e-12)
    print("Toy mixture:", {k: round(v * 100, 2) for k, v in p.items()})
    print("Toy BPB:", bits_per_utf8_byte(log(2), 4, 8))


if __name__ == "__main__":
    paper_examples()
