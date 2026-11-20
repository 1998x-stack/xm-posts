"""Tests for the educational embedding operators, not a model reproduction."""
import importlib.util
from pathlib import Path
from math import isclose
import pytest

FILE = Path(__file__).resolve().parents[1] / "posts/foundations/embeddings/mini_embedding.py"
spec = importlib.util.spec_from_file_location("mini_embedding", FILE)
assert spec is not None and spec.loader is not None
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_lookup_shapes_and_independent_copies():
    vectors = m.lookup([1,0,1],[[1.,0.],[0.,1.]])
    assert vectors == [[0.,1.],[1.,0.],[0.,1.]]
    vectors[0][0] = 5.
    assert vectors[2] == [0.,1.]

def test_padding_is_excluded_from_mean():
    assert m.masked_mean([[2.,0.],[0.,2.],[999.,999.]],[1,1,0]) == [1.,1.]
    with pytest.raises(ValueError):
        m.masked_mean([[1.,2.]],[0])

def test_cosine_and_zero_norm():
    assert isclose(m.cosine([1.,1.],[2.,2.]),1.0)
    assert isclose(m.cosine([1.,0.],[-1.,0.]),-1.0)
    with pytest.raises(ValueError):
        m.cosine([0.,0.],[1.,0.])
    with pytest.raises(ValueError):
        m.cosine([1.,0.],[1.])

def test_topk_ties_are_deterministic():
    assert m.topk([1.,0.],{"b":[1.,0.],"a":[1.,0.],"c":[-1.,0.]},2)==[("a",1.),("b",1.)]
