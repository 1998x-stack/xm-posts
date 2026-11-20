"""Teaching-only RAG-Sequence and RAG-Token probability comparison.

No DPR, BART, vector index or historical model outputs are reproduced here.
"""
from math import isclose


def probabilities(weight_a: float) -> tuple[float, float]:
    """Compute the toy two-document, two-token sequence probabilities."""
    if not 0.0 <= weight_a <= 1.0:
        raise ValueError("weight_a must be in [0, 1]")
    weights = (weight_a, 1.0 - weight_a)
    first = (0.9, 0.2)
    second = (0.3, 0.8)
    sequence = sum(w * p1 * p2 for w, p1, p2 in zip(weights, first, second))
    token = sum(w * p1 for w, p1 in zip(weights, first)) * sum(
        w * p2 for w, p2 in zip(weights, second)
    )
    return sequence, token


if __name__ == "__main__":
    seq, tok = probabilities(0.6)
    assert isclose(seq, 0.226, abs_tol=1e-12)
    assert isclose(tok, 0.310, abs_tol=1e-12)
    for w in (0.0, 1.0):
        a, b = probabilities(w)
        assert isclose(a, b, abs_tol=1e-12)
    print(f"Sequence={seq:.3f}; Token={tok:.3f}")
