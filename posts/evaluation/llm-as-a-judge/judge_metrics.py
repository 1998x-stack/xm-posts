"""Small, dependency-free metrics for auditing an LLM judge.

Choices in a pairwise swap audit are positional labels:
- "A": the first slot in the presented prompt
- "B": the second slot in the presented prompt
- "tie": no preferred candidate

For the swapped prompt, the candidate identities reverse. This helper maps the
second judgment back to candidate identity before checking consistency.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence

VALID_CHOICES = {"A", "B", "tie"}


def agreement_rate(reference: Sequence[str], prediction: Sequence[str]) -> float:
    """Exact agreement between two categorical label sequences."""
    if len(reference) != len(prediction) or not reference:
        raise ValueError("label sequences must have the same non-zero length")
    return sum(a == b for a, b in zip(reference, prediction)) / len(reference)


def cohens_kappa(reference: Sequence[str], prediction: Sequence[str]) -> float:
    """Cohen's kappa for two categorical raters; undefined marginals raise."""
    if len(reference) != len(prediction) or not reference:
        raise ValueError("label sequences must have the same non-zero length")
    n = len(reference)
    observed = agreement_rate(reference, prediction)
    labels = set(reference) | set(prediction)
    expected = sum(
        (reference.count(label) / n) * (prediction.count(label) / n)
        for label in labels
    )
    if expected == 1.0:
        raise ValueError("kappa is undefined when expected agreement is 1")
    return (observed - expected) / (1.0 - expected)


def position_swap_audit(original_choice: str, swapped_choice: str) -> str:
    """Classify a pair of judgments after swapping candidate order.

    Returns one of:
      candidate_a, candidate_b, first_position, second_position,
      tie_consistent, unstable
    """
    if original_choice not in VALID_CHOICES or swapped_choice not in VALID_CHOICES:
        raise ValueError("choices must be 'A', 'B', or 'tie'")

    if original_choice == "tie" and swapped_choice == "tie":
        return "tie_consistent"
    if original_choice == "A" and swapped_choice == "B":
        return "candidate_a"
    if original_choice == "B" and swapped_choice == "A":
        return "candidate_b"
    if original_choice == "A" and swapped_choice == "A":
        return "first_position"
    if original_choice == "B" and swapped_choice == "B":
        return "second_position"
    return "unstable"


def position_consistency_rate(pairs: Iterable[tuple[str, str]]) -> float:
    """Fraction of swap pairs retaining the same candidate identity or tie."""
    results = [position_swap_audit(a, b) for a, b in pairs]
    if not results:
        raise ValueError("at least one swap pair is required")
    stable = {"candidate_a", "candidate_b", "tie_consistent"}
    return sum(result in stable for result in results) / len(results)
