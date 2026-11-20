#!/usr/bin/env python3
"""BERT MLM/NSP teaching invariants. Standard library only; not a pretrained model."""
from __future__ import annotations
from dataclasses import dataclass
from math import isclose, log
from random import Random

SPECIAL = {"[CLS]", "[SEP]", "[PAD]"}

@dataclass(frozen=True)
class Replacement:
    input_token: str
    target_token: str
    branch: str

def replace_selected(token: str, draw: int, random_token: str = "apple") -> Replacement:
    """Conditioned on a chosen MLM position, apply the paper's 80/10/10 rule."""
    if token in SPECIAL:
        raise ValueError("special tokens should not be masked")
    if not isinstance(draw, int) or not 0 <= draw < 100:
        raise ValueError("draw must be an integer in [0, 99]")
    if draw < 80:
        return Replacement("[MASK]", token, "mask")
    if draw < 90:
        return Replacement(random_token, token, "random")
    return Replacement(token, token, "unchanged")

def toy_mask(tokens: list[str], seed: int = 7) -> tuple[list[str], dict[int, str]]:
    """Approximate 15% over eligible tokens; not the paper's full input pipeline."""
    rng = Random(seed)
    eligible = [i for i, tok in enumerate(tokens) if tok not in SPECIAL]
    if not eligible:
        return tokens[:], {}
    count = max(1, round(0.15 * len(eligible)))
    inputs = tokens[:]
    labels: dict[int, str] = {}
    for idx in rng.sample(eligible, count):
        replacement = replace_selected(tokens[idx], rng.randrange(100))
        inputs[idx] = replacement.input_token
        labels[idx] = replacement.target_token
    return inputs, labels

def visible_positions(length: int, index: int, causal: bool, padding: set[int] | None = None) -> tuple[int, ...]:
    if index < 0 or index >= length:
        raise IndexError(index)
    pad = padding if padding is not None else set()
    return tuple(j for j in range(length) if j not in pad and (not causal or j <= index))

def selected_cross_entropy(correct_probabilities: list[float]) -> float:
    if not correct_probabilities or any(p <= 0 or p > 1 for p in correct_probabilities):
        raise ValueError("nonempty probabilities in (0,1] required")
    return -sum(log(p) for p in correct_probabilities) / len(correct_probabilities)

def self_test() -> None:
    sequence = [replace_selected("hairy", i) for i in range(100)]
    assert [sum(r.branch == b for r in sequence) for b in ("mask", "random", "unchanged")] == [80, 10, 10]
    assert all(r.target_token == "hairy" for r in sequence)
    tokens = ["[CLS]", "my", "dog", "is", "hairy", "[SEP]"]
    masked, labels = toy_mask(tokens)
    assert labels and all(tokens[i] == label for i, label in labels.items())
    assert masked[0] == "[CLS]" and masked[-1] == "[SEP]"
    assert visible_positions(5, 2, causal=False) == (0, 1, 2, 3, 4)
    assert visible_positions(5, 2, causal=True) == (0, 1, 2)
    assert visible_positions(5, 2, causal=False, padding={4}) == (0, 1, 2, 3)
    assert isclose(selected_cross_entropy([.5, .25]), (log(2) + log(4)) / 2)
    print("BERT objective invariants: OK")

if __name__ == "__main__":
    self_test()
