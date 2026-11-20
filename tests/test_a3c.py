"""Deterministic source-level checks for the A3C paper explainer."""
import importlib.util
from pathlib import Path
import math

SOURCE = Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/a3c/mini_a3c.py"
spec = importlib.util.spec_from_file_location("mini_a3c", SOURCE)
a3c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a3c)


def test_a3c_examples_and_policy_properties():
    a3c.check()


def test_a3c_truncation_is_not_terminal():
    x = a3c.n_step_returns([0.0, 0.0], 10.0, 0.5, terminated=False)
    y = a3c.n_step_returns([0.0, 0.0], 10.0, 0.5, terminated=True)
    assert x == [2.5, 5.0]
    assert y == [0.0, 0.0]


def test_a3c_entropy_and_logit_gradient():
    logits = [1.0, -1.0, 0.0]
    probs = a3c.softmax(logits)
    assert math.isclose(sum(probs), 1.0)
    grad = a3c.policy_logprob_gradient(logits, 1, 2.0)
    assert math.isclose(sum(grad), 0.0, abs_tol=1e-12)
    assert grad[1] > 0 and grad[0] < 0 and grad[2] < 0
