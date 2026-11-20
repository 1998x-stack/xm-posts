"""Deterministic checks for the Teacher Forcing teaching example."""
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "posts/training/teacher-forcing/mini_teacher_forcing.py"
spec = spec_from_file_location("teacher_forcing_toy", SOURCE)
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_shifted_pairs_aligns_previous_token_with_next_target():
    tokens = ["<bos>", "我", "爱", "机器", "学习", "<eos>"]
    assert module.shifted_pairs(tokens) == [
        ("<bos>", "我"), ("我", "爱"), ("爱", "机器"),
        ("机器", "学习"), ("学习", "<eos>")
    ]


def test_invalid_sequence_is_not_silently_shifted():
    with pytest.raises(ValueError):
        module.shifted_pairs(["我", "爱", "<eos>"])


def test_cross_entropy_uses_log_probability_and_token_mean():
    assert isclose(module.token_cross_entropy([0.8, 0.7, 0.6]), 0.3635480, abs_tol=1e-6)
    assert module.token_cross_entropy([1.0, 1.0]) == 0.0
    with pytest.raises(ValueError):
        module.token_cross_entropy([0.8, 0.0])
    with pytest.raises(ValueError):
        module.token_cross_entropy([])


def test_teacher_and_self_feedback_differ_on_identical_rule():
    paths = module.demo_rollouts()
    assert paths["teacher_inputs"] == ["<bos>", "I", "love"]
    assert paths["teacher_outputs"] == ["We", "love", "cats"]
    assert paths["free_inputs"] == ["<bos>", "We", "like"]
    assert paths["free_outputs"] == ["We", "like", "dogs"]
