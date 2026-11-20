"""Deterministic verification for the BPE paper post."""
import runpy
from pathlib import Path

API = runpy.run_path(str(Path(__file__).resolve().parents[1] / "posts/foundations/bpe/mini_bpe.py"))

def test_weighted_pairs_and_reproducibility():
    train = API["train"]
    rules, alphabet, states = train(API["CORPUS"], 12)
    assert rules[:3] == [("e", "s"), ("es", "t"), ("est", "</w>")]
    assert train(API["CORPUS"], 12) == (rules, alphabet, states)

def test_nonoverlapping_merge():
    assert API["merge_pair"](["a", "a", "a"], ("a", "a")) == ["aa", "a"]

def test_round_trip_and_unknown_char():
    rules, alphabet, _ = API["train"](API["CORPUS"], 12)
    for word in ("low", "lowest", "lower", "newer", "widest"):
        assert API["decode"](API["encode"](word, rules, alphabet)) == word
    try:
        API["encode"]("🙂", rules, alphabet)
    except ValueError:
        pass
    else:
        assert False, "expected unknown base character to fail"

def test_empty_merge_budget_and_counts():
    corpus = API["CORPUS"]
    rules, alphabet, states = API["train"](corpus, 0)
    assert not rules
    expected = sum(freq * (len(w) + 1) for w, freq in corpus.items())
    assert API["weighted_slots"](corpus, states) == expected
    merged, _, final = API["train"](corpus, 12)
    assert merged
    assert API["weighted_slots"](corpus, final) <= expected

def test_bad_training_counts():
    for bad in ({}, {"hello": 0}, {"a": -1}):
        try:
            API["train"](bad, 2)
        except ValueError:
            pass
        else:
            assert False, "invalid corpus should fail"
