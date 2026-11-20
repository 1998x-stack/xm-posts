"""Deterministic Seq2Seq probability and decoding checks (Python >= 3.11).

This intentionally does not implement or reproduce the 2014 deep-LSTM training
system, its BLEU metric, or learned attention. Pure-standard-library tests for
the mathematical interfaces used in the accompanying article.
"""
from __future__ import annotations

import math
from typing import Callable, Mapping, Sequence


def shifted_targets(tokens: Sequence[str], *, bos: str = "BOS",
                    eos: str = "EOS") -> tuple[list[str], list[str]]:
    """Return teacher-forced decoder inputs and next-token labels."""
    if any(token in {bos, eos} for token in tokens):
        raise ValueError("tokens should not include BOS or EOS")
    return [bos, *tokens], [*tokens, eos]


def masked_nll(target_probabilities: Sequence[float],
               valid: Sequence[bool]) -> float:
    """Mean token negative log likelihood, ignoring padding positions."""
    if len(target_probabilities) != len(valid):
        raise ValueError("probabilities and mask must have the same shape")
    count = sum(valid)
    if count == 0:
        raise ValueError("at least one non-padding target is required")
    total = 0.0
    for p, use in zip(target_probabilities, valid):
        if not use:
            continue
        if not math.isfinite(p) or not (0.0 < p <= 1.0):
            raise ValueError("unmasked probability must be finite in (0,1]")
        total -= math.log(p)
    return total / count


def masked_softmax(scores: Sequence[float],
                   allowed: Sequence[bool]) -> list[float]:
    """Source-position softmax; True means a visible source position."""
    if len(scores) != len(allowed) or not any(allowed):
        raise ValueError("need matching nonempty scores and visible positions")
    visible = [s for s, keep in zip(scores, allowed) if keep]
    if not all(math.isfinite(s) for s in visible):
        raise ValueError("scores must be finite for visible positions")
    peak = max(visible)
    exp = [math.exp(s - peak) if keep else 0.0
           for s, keep in zip(scores, allowed)]
    denom = sum(exp)
    return [value / denom for value in exp]


def weighted_context(weights: Sequence[float],
                     annotations: Sequence[Sequence[float]]) -> list[float]:
    """Compute sum_i alpha_i h_i; h has shape [source_length, d]."""
    if not annotations or len(weights) != len(annotations):
        raise ValueError("weights and source annotations must align")
    dim = len(annotations[0])
    if dim == 0 or any(len(h) != dim for h in annotations):
        raise ValueError("each annotation must have the same positive width")
    if any(w < 0 or not math.isfinite(w) for w in weights):
        raise ValueError("weights must be finite and non-negative")
    if not math.isclose(sum(weights), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("attention weights must sum to one")
    return [sum(w * h[d] for w, h in zip(weights, annotations))
            for d in range(dim)]


NextProb = Callable[[tuple[str, ...]], Mapping[str, float]]


def _check_next_probs(dist: Mapping[str, float]) -> None:
    if not dist or any(not math.isfinite(p) or p <= 0.0 or p > 1.0
                       for p in dist.values()):
        raise ValueError("probabilities must be positive and finite")
    if not math.isclose(sum(dist.values()), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("distribution must sum to one")


def greedy_decode(next_probs: NextProb, *, bos: str = "BOS",
                  eos: str = "EOS", max_steps: int = 8) -> tuple[str, ...]:
    if max_steps < 1:
        raise ValueError("max_steps must be positive")
    seq = (bos,)
    for _ in range(max_steps):
        dist = next_probs(seq)
        _check_next_probs(dist)
        token = sorted(dist, key=lambda word: (-dist[word], word))[0]
        seq += (token,)
        if token == eos:
            break
    return seq


def beam_search(next_probs: NextProb, *, width: int = 2, bos: str = "BOS",
                eos: str = "EOS", max_steps: int = 8) -> tuple[str, ...]:
    """Small exhaustive-per-step beam; no length normalization."""
    if width < 1 or max_steps < 1:
        raise ValueError("beam width and max_steps must be positive")
    beams: list[tuple[tuple[str, ...], float]] = [((bos,), 0.0)]
    for _ in range(max_steps):
        candidate: list[tuple[tuple[str, ...], float]] = []
        for seq, score in beams:
            if seq[-1] == eos:
                candidate.append((seq, score))
                continue
            dist = next_probs(seq)
            _check_next_probs(dist)
            candidate.extend((seq + (token,), score + math.log(p))
                             for token, p in dist.items())
        beams = sorted(candidate, key=lambda row: (-row[1], row[0]))[:width]
        if all(seq[-1] == eos for seq, _ in beams):
            break
    return beams[0][0]


def toy_probs(prefix: tuple[str, ...]) -> Mapping[str, float]:
    """Constructed example where beam width 2 beats local greedy."""
    if prefix == ("BOS",):
        return {"A": 0.6, "B": 0.4}
    if prefix == ("BOS", "A"):
        return {"C": 0.6, "EOS": 0.4}
    if prefix == ("BOS", "B"):
        return {"EOS": 0.99, "C": 0.01}
    return {"EOS": 1.0}


if __name__ == "__main__":
    assert shifted_targets(["je", "suis"]) == (
        ["BOS", "je", "suis"], ["je", "suis", "EOS"])
    assert greedy_decode(toy_probs) == ("BOS", "A", "C", "EOS")
    assert beam_search(toy_probs, width=2) == ("BOS", "B", "EOS")
    assert masked_softmax([0, 2, 99], [True, True, False])[-1] == 0.0
    print("All deterministic Seq2Seq teaching assertions passed")
