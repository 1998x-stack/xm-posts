"""Deterministic educational character-level BPE, not a production tokenizer.

This reproduces frequency-weighted pair merges with an explicit </w> sentinel.
No dependency other than the Python standard library.
"""
from __future__ import annotations
from collections import Counter

CORPUS = {"low": 5, "lower": 2, "newest": 6, "widest": 3}
END = "</w>"


def merge_pair(symbols: list[str], pair: tuple[str, str]) -> list[str]:
    """Replace non-overlapping adjacent occurrences, from left to right."""
    out: list[str] = []
    i = 0
    while i < len(symbols):
        if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
            out.append(symbols[i] + symbols[i + 1])
            i += 2
        else:
            out.append(symbols[i])
            i += 1
    return out


def train(corpus: dict[str, int], steps: int = 12):
    """Return ordered merge pairs, the base alphabet, and final token sequences.

    Frequencies weight *every* adjacent occurrence; ties use lexical order.
    For simplicity this toy implementation counts the explicit end marker as a
    training symbol. It is not an output token by itself.
    """
    if not corpus or steps < 0 or any(not w or f <= 0 for w, f in corpus.items()):
        raise ValueError("corpus must be nonempty with positive word frequencies")
    alphabet = set(END for _ in [0])
    alphabet.update(c for word in corpus for c in word)
    states = {w: list(w) + [END] for w in corpus}
    merges: list[tuple[str, str]] = []
    for _ in range(steps):
        counts: Counter[tuple[str, str]] = Counter()
        for word, symbols in states.items():
            for pair in zip(symbols, symbols[1:]):
                counts[pair] += corpus[word]
        if not counts:
            break
        best = min(counts, key=lambda p: (-counts[p], p))
        merges.append(best)
        states = {w: merge_pair(symbols, best) for w, symbols in states.items()}
    return merges, alphabet, states


def encode(word: str, merges: list[tuple[str, str]], alphabet: set[str]):
    """Apply frozen merge order; reject unseen base characters in this toy."""
    if not word or any(char not in alphabet for char in word):
        raise ValueError("unseen base character; byte-level BPE uses a different alphabet")
    symbols = list(word) + [END]
    for pair in merges:
        symbols = merge_pair(symbols, pair)
    return symbols


def decode(tokens: list[str]):
    """Reverse concatenation and remove the exactly one word-end sentinel."""
    raw = "".join(tokens)
    if not raw.endswith(END) or raw.count(END) != 1:
        raise ValueError("invalid toy word-boundary encoding")
    return raw[:-len(END)]


def weighted_slots(corpus, states):
    return sum(corpus[word] * len(states[word]) for word in corpus)


def self_test():
    merges, alphabet, states = train(CORPUS)
    assert merges[:3] == [("e", "s"), ("es", "t"), ("est", END)]
    assert decode(encode("lowest", merges, alphabet)) == "lowest"
    assert decode(encode("newer", merges, alphabet)) == "newer"
    assert weighted_slots(CORPUS, states) <= weighted_slots(
        CORPUS, {w: list(w) + [END] for w in CORPUS}
    )
    try:
        encode("🙂", merges, alphabet)
    except ValueError:
        pass
    else:
        raise AssertionError("unseen character must be rejected")
    return True


if __name__ == "__main__":
    assert self_test()
    print("BPE toy checks passed")
