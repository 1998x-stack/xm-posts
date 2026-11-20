"""Deterministic mathematical checks for the independent Chinchilla explainer."""
from pathlib import Path
import importlib.util
from math import isclose
import pytest
PATH=Path(__file__).resolve().parents[1]/"posts/training/chinchilla/mini_chinchilla.py"
spec=importlib.util.spec_from_file_location("mini_chinchilla",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_budget_tradeoff():
    c=6*70e9*1.4e12
    assert isclose(mod.tokens_for_budget(c,35e9),2.8e12)
    assert isclose(mod.tokens_for_budget(c,280e9),0.35e12)
    with pytest.raises(ValueError):mod.tokens_for_budget(-1,20)

def test_symmetric_toy_optimum_and_scaling():
    c=6*100*100
    n,d=mod.optimum_for_toy_loss(c)
    assert isclose(n,100) and isclose(d,100)
    n4,d4=mod.optimum_for_toy_loss(c*4)
    assert isclose(n4,200) and isclose(d4,200)
    l=mod.predicted_toy_loss(n,d)
    assert l<mod.predicted_toy_loss(50,mod.tokens_for_budget(c,50))
    assert l<mod.predicted_toy_loss(200,mod.tokens_for_budget(c,200))
