"""Deterministic WordPiece model assertions (no third-party requirements)."""
from pathlib import Path
import runpy
from fractions import Fraction
import pytest

M = runpy.run_path(str(Path(__file__).resolve().parents[1] / "posts/foundations/wordpiece/mini_wordpiece.py"))

def test_score_and_first_merge():
    states = {w: M["initial"](w) for w in M["CORPUS"]}
    score = M["scores"](states, M["CORPUS"])
    assert score[("##u","##g")] == Fraction(1,36)
    assert score[("##g","##s")] == Fraction(1,20)
    vocab, rules, result = M["learn_demo"](steps=1)
    assert rules[0][0] == ("##g","##s")
    assert "##gs" in vocab and "##g" in vocab
    assert result["hugs"] == ["h","##u","##gs"]

def test_encoding_matches_greedy_longest_match():
    expected = {
        "unaffable": ["un","##aff","##able"],
        "hugs": ["hug","##s"],
        "bugs": ["b","##u","##gs"],
        "mug": ["[UNK]"],
        "": ["[UNK]"],
    }
    for word, pieces in expected.items():
        assert M["encode_word"](word) == pieces

def test_atomic_unknown_and_char_length_guard():
    assert M["encode_word"]("mug") == ["[UNK]"]
    assert M["encode_word"]("a"*201, {"a","##a","[UNK]"}) == ["[UNK]"]
    assert M["encode_word"]("a"*200, {"a","##a","[UNK]"}) == ["a"]+["##a"]*199

def test_round_trip_of_nonunknown_words():
    for word in ("unaffable","hugs","bugs"):
        assert M["detokenize_word"](M["encode_word"](word)) == word
    with pytest.raises(ValueError):
        M["detokenize_word"](["[UNK]"])

def test_training_determinism_and_validation():
    assert M["learn_demo"](steps=7) == M["learn_demo"](steps=7)
    for bad in ({},{"x":0},{"x":-2}):
        with pytest.raises(ValueError):
            M["learn_demo"](bad,steps=1)
    with pytest.raises(ValueError):
        M["learn_demo"](steps=-1)

def test_merged_symbol_prefix_semantics():
    assert M["combined"]("h","##u") == "hu"
    assert M["combined"]("##g","##s") == "##gs"
    assert M["merge"](["h","##u","##g"],("h","##u")) == ["hu","##g"]
