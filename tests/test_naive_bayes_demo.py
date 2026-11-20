"""Regression checks for independent educational Naive Bayes example."""
import importlib.util
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "posts/classical-ml/naive-bayes/naive_bayes_demo.py"
spec = importlib.util.spec_from_file_location("nb_demo", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_vocab_and_normalization():
    assert len(mod.VOCAB) == 8
    for mode in ("multinomial", "bernoulli"):
        for query in ("free offer", "free meeting", "unknown", "project meeting"):
            p = mod.probabilities(query, model=mode)
            assert all(0 < value < 1 for value in p.values())
            assert abs(sum(p.values()) - 1) < 1e-12

def test_hand_derived_multinomial():
    p = mod.probabilities("free offer")
    assert abs(p["promo"] - 12/13) < 1e-12
    assert mod.probabilities("project meeting")["work"] > 0.9

def test_bernoulli_discards_repetitions_and_unknown():
    assert mod.probabilities("free meeting", model="bernoulli") == mod.probabilities(
        "free free meeting", model="bernoulli")
    assert mod.probabilities("free offer unknown") == mod.probabilities("free offer")

def test_validation():
    import pytest
    with pytest.raises(ValueError):
        mod.probabilities("free", alpha=0)
    with pytest.raises(ValueError):
        mod.probabilities("free", model="other")
