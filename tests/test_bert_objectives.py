"""Deterministic mathematical checks; not a claim of BERT benchmark reproduction."""
from pathlib import Path
import importlib.util
import sys

p = Path(__file__).resolve().parents[1] / "posts/training/bert/mini_bert_objectives.py"
spec = importlib.util.spec_from_file_location("mini_bert_objectives", p)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

def test_mlm_target_and_sampling():
    m.self_test()

def test_special_tokens_not_selected():
    for token in ("[CLS]", "[SEP]", "[PAD]"):
        try:
            m.replace_selected(token, 50)
        except ValueError:
            continue
        raise AssertionError(f"special token {token} should be excluded")

def test_boundary_probabilities():
    assert m.replace_selected("hairy", 79).branch == "mask"
    assert m.replace_selected("hairy", 80).branch == "random"
    assert m.replace_selected("hairy", 89).branch == "random"
    assert m.replace_selected("hairy", 90).branch == "unchanged"
    assert abs(0.15 * 0.8 - 0.12) < 1e-12
    assert abs(0.15 * 0.1 - 0.015) < 1e-12
