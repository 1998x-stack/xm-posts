"""WordPiece teaching model: score-based vocabulary growth + exact-style MaxMatch.

Training below is a transparent, deterministic *approximation* from Hugging
Face's educational explanation, NOT the unpublished Google WordPiece trainer.
Encoding follows the greedy longest-match BERT tokenizer logic on one
pre-tokenized word; it is not a replacement for BasicTokenizer.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction

CORPUS = {"hug": 10, "pug": 5, "pun": 12, "bun": 4, "hugs": 5}
PREFIX = "##"
UNK = "[UNK]"

def initial(word: str) -> list[str]:
    if not word:
        raise ValueError("word must be nonempty")
    return [word[0]] + [PREFIX + char for char in word[1:]]

def adjacent_counts(states: dict[str, list[str]], frequencies: dict[str, int]):
    symbols: Counter[str] = Counter()
    pairs: Counter[tuple[str, str]] = Counter()
    for word, units in states.items():
        weight = frequencies[word]
        symbols.update({unit: units.count(unit) * weight for unit in set(units)})
        for pair in zip(units, units[1:]):
            pairs[pair] += weight
    return symbols, pairs

def scores(states, frequencies):
    symbols, pairs = adjacent_counts(states, frequencies)
    return {p: Fraction(count, symbols[p[0]] * symbols[p[1]])
            for p, count in pairs.items()}

def combined(a: str, b: str):
    return a + (b[len(PREFIX):] if b.startswith(PREFIX) else b)

def merge(symbols: list[str], pair: tuple[str, str]) -> list[str]:
    result = []
    i = 0
    while i < len(symbols):
        if i + 1 < len(symbols) and (symbols[i], symbols[i+1]) == pair:
            result.append(combined(*pair))
            i += 2
        else:
            result.append(symbols[i])
            i += 1
    return result

def learn_demo(corpus=CORPUS, steps: int = 8):
    if not corpus or steps < 0 or any(not w or n <= 0 for w, n in corpus.items()):
        raise ValueError("nonempty words and positive frequencies are required")
    states = {w: initial(w) for w in corpus}
    vocabulary = {UNK} | {x for units in states.values() for x in units}
    rules = []
    for _ in range(steps):
        score_table = scores(states, corpus)
        if not score_table:
            break
        pair = min(score_table, key=lambda p: (-score_table[p], p))
        rules.append((pair, score_table[pair]))
        vocabulary.add(combined(*pair))
        states = {w: merge(units, pair) for w, units in states.items()}
    return vocabulary, rules, states

DEMO_VOCAB = {
    "[UNK]", "un", "##aff", "##able", "hug", "##s",
    "b", "##u", "##gs", "m",
}

def encode_word(word: str, vocab=DEMO_VOCAB, max_chars: int = 200):
    """BERT-style greedy longest-match-first; failed word -> single [UNK]."""
    if not word or len(word) > max_chars:
        return [UNK]
    output = []
    start = 0
    while start < len(word):
        found = None
        found_end = start
        for end in range(len(word), start, -1):
            part = (PREFIX if start > 0 else "") + word[start:end]
            if part in vocab:
                found = part
                found_end = end
                break
        if found is None:
            return [UNK]
        output.append(found)
        start = found_end
    return output

def detokenize_word(tokens: list[str]):
    if tokens == [UNK]:
        raise ValueError("UNK loses the original surface form")
    return "".join(x.removeprefix(PREFIX) for x in tokens)

def self_test():
    state = {w: initial(w) for w in CORPUS}
    values = scores(state, CORPUS)
    assert values[("##u", "##g")] == Fraction(1, 36)
    assert values[("##g", "##s")] == Fraction(1, 20)
    assert learn_demo(steps=1)[1][0][0] == ("##g", "##s")
    assert encode_word("unaffable") == ["un", "##aff", "##able"]
    assert encode_word("hugs") == ["hug", "##s"]
    assert encode_word("bugs") == ["b", "##u", "##gs"]
    assert encode_word("mug") == [UNK]
    assert detokenize_word(encode_word("bugs")) == "bugs"
    return True

if __name__ == "__main__":
    assert self_test()
    print("WordPiece toy checks passed")
