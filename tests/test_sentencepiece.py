"""Regression tests for the independent SentencePiece Unigram teaching kernel."""
from pathlib import Path
import importlib.util
import math
import pytest

MODULE = Path(__file__).resolve().parents[1] / "posts/foundations/sentencepiece/mini_unigram_dp.py"
spec = importlib.util.spec_from_file_location("mini_unigram_dp", MODULE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_three_valid_segmentations():
    assert set(m.paths("aba")) == {
        ("ab", "a"), ("a", "ba"), ("a", "b", "a")
    }
    assert m.weight(("ab", "a")) == pytest.approx(0.1134)
    assert m.weight(("a", "ba")) == pytest.approx(0.0462)
    assert m.weight(("a", "b", "a")) == pytest.approx(0.03528)

def test_viterbi_matches_enumeration():
    for text in ("a", "b", "aba", "abba", "baba", "aabb"):
        score, result = m.best_path(text)
        assert "".join(result) == text
        assert math.exp(score) == pytest.approx(max(map(m.weight, m.paths(text))))
    assert m.best_path("aba")[1] == ("ab", "a")

def test_unreachable_and_alpha_normalization():
    assert m.best_path("abc") == (-math.inf, ())
    for alpha in (.2, 1., 3.):
        d = m.distribution("aba", alpha)
        assert sum(d.values()) == pytest.approx(1.)
        assert d[("ab", "a")] > d[("a", "ba")]
    assert m.distribution("aba", 3.)[("ab", "a")] > m.distribution("aba", .2)[("ab", "a")]
    with pytest.raises(ValueError):
        m.distribution("aba", 0)
