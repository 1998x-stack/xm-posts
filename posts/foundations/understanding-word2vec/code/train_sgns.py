#!/usr/bin/env python3
"""Minimal deterministic Word2Vec Skip-gram + Negative Sampling (SGNS).

Educational implementation, not a reproduction of the original speed/quality benchmarks.
No sub-sampling, dynamic window, phrase learning, or hierarchical softmax.
Dependency: numpy. Run: python code/train_sgns.py --epochs 30
"""
from __future__ import annotations

import argparse
import collections
import math
from dataclasses import dataclass

import numpy as np

CORPUS = [
    "the cat drinks fresh milk",
    "a small cat drinks milk",
    "the kitten drinks fresh milk",
    "the cat and kitten drink milk",
    "the dog eats tasty food",
    "a small dog eats food",
    "the puppy eats tasty food",
    "the dog and puppy eat food",
    "paris is the capital of france",
    "france has paris as the capital",
    "rome is the capital of italy",
    "italy has rome as the capital",
    "dogs and cats are friendly pets",
    "a kitten is a young cat",
    "a puppy is a young dog",
]


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    # Stable sigmoid: avoid exponential overflow for large logits.
    z = np.asarray(x, dtype=np.float64)
    result = np.exp(-np.logaddexp(0.0, -z))
    return float(result) if result.ndim == 0 else result


@dataclass
class Grads:
    center: np.ndarray
    positive: np.ndarray
    negatives: np.ndarray


def sgns_loss_and_grads(
    center: np.ndarray,
    positive: np.ndarray,
    negatives: np.ndarray,
) -> tuple[float, Grads]:
    """Exact SGNS loss and grads for a single center/positive/k negatives.

    center/positive: shape (dim,). negatives: shape (k, dim).
    All args are input vectors and not mutated by this function.
    """
    s_pos = float(positive @ center)
    s_neg = negatives @ center
    p_pos = float(sigmoid(s_pos))
    p_neg = np.asarray(sigmoid(s_neg))
    loss = float(np.logaddexp(0.0, -s_pos) + np.logaddexp(0.0, s_neg).sum())
    grad_c = (p_pos - 1.0) * positive + (p_neg[:, None] * negatives).sum(axis=0)
    grad_p = (p_pos - 1.0) * center
    grad_n = p_neg[:, None] * center[None, :]
    return loss, Grads(grad_c, grad_p, grad_n)


def pairs_from_sentences(
    sentences: list[list[int]], window: int
) -> list[tuple[int, int]]:
    """Fixed left/right window, sentence-aware; no padding / crossing boundaries."""
    if window < 1:
        raise ValueError("window must be >= 1")
    return [
        (sentence[i], sentence[j])
        for sentence in sentences
        for i in range(len(sentence))
        for j in range(max(0, i - window), min(len(sentence), i + window + 1))
        if i != j
    ]


def toy_corpus() -> tuple[list[str], list[list[int]], np.ndarray]:
    lines = [line.lower().split() for line in CORPUS]
    counts = collections.Counter(w for line in lines for w in line)
    vocab = sorted(counts)
    ids = {w: i for i, w in enumerate(vocab)}
    encoded = [[ids[w] for w in line] for line in lines]
    frequency = np.array([counts[w] for w in vocab], dtype=np.float64)
    return vocab, encoded, frequency


def sample_negatives(
    rng: np.random.Generator, probs: np.ndarray, k: int, positive_id: int
) -> np.ndarray:
    """Sample with replacement from p_n ~ f^0.75, rejecting positive target.

    Repeated negative token IDs remain possible; the training update below
    handles them with np.add.at (rather than incorrect fancy-index +=).
    """
    if len(probs) < 2 or not 0 <= positive_id < len(probs):
        raise ValueError("need at least two token IDs and a valid positive_id")
    if k < 1:
        raise ValueError("k must be >= 1")
    out = rng.choice(len(probs), size=k, replace=True, p=probs)
    bad = out == positive_id
    while np.any(bad):
        out[bad] = rng.choice(len(probs), size=int(bad.sum()), replace=True, p=probs)
        bad = out == positive_id
    return out


def train(
    *,
    epochs: int = 30,
    dim: int = 24,
    window: int = 2,
    negative: int = 3,
    lr: float = 0.025,
    seed: int = 7,
    verbose: bool = True,
) -> tuple[list[str], np.ndarray, np.ndarray, list[float]]:
    if epochs < 1 or dim < 1 or window < 1 or negative < 1 or lr <= 0:
        raise ValueError("epochs, dim, window, negative, lr must be positive")
    rng = np.random.default_rng(seed)
    vocab, encoded, freq = toy_corpus()
    pairs = pairs_from_sentences(encoded, window)
    probs = freq ** 0.75
    probs /= probs.sum()
    V = rng.normal(0, 0.13, size=(len(vocab), dim))
    U = np.zeros((len(vocab), dim), dtype=np.float64)
    history = []
    for epoch in range(epochs):
        total = 0.0
        for ix in rng.permutation(len(pairs)):
            c, p = pairs[int(ix)]
            ns = sample_negatives(rng, probs, negative, p)
            # Snapshots matter: gradient for each factor must be from same state.
            loss, grad = sgns_loss_and_grads(V[c].copy(), U[p].copy(), U[ns].copy())
            total += loss
            V[c] -= lr * grad.center
            U[p] -= lr * grad.positive
            # Supports repeated sampled IDs safely.
            np.add.at(U, ns, -lr * grad.negatives)
        avg_loss = total / len(pairs)
        history.append(avg_loss)
        if verbose and (epoch == 0 or (epoch + 1) % 5 == 0 or epoch + 1 == epochs):
            print(f"epoch={epoch+1:03d}  mean_sgns_loss={avg_loss:.5f}")
    return vocab, V, U, history


def nearest(vocab: list[str], embeddings: np.ndarray, word: str, topk: int = 4):
    idx = vocab.index(word)
    norms = np.maximum(np.linalg.norm(embeddings, axis=1), 1e-12)
    scores = (embeddings @ embeddings[idx]) / (norms * norms[idx])
    candidates = [(w, float(scores[j])) for j, w in enumerate(vocab) if j != idx]
    return sorted(candidates, key=lambda x: x[1], reverse=True)[:topk]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--dim", type=int, default=24)
    parser.add_argument("--window", type=int, default=2)
    parser.add_argument("--negative", type=int, default=3)
    parser.add_argument("--lr", type=float, default=0.025)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    vocab, V, _U, hist = train(**vars(args))
    print(f"vocab={len(vocab)}  first_loss={hist[0]:.4f}  last_loss={hist[-1]:.4f}")
    for word in ("cat", "dog", "paris", "rome"):
        print(word, "=>", nearest(vocab, V, word))
    print("Note: This tiny toy corpus does not validate paper-level semantics or analogy scores.")


if __name__ == "__main__":
    main()
