"""Regression checks for the self-contained neural gating educational example."""
import importlib.util
from pathlib import Path
import math

MODULE_PATH = Path(__file__).resolve().parents[1] / "posts" / "architectures" / "neural-gating" / "mini_gating.py"
spec = importlib.util.spec_from_file_location("mini_gating", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_gating_self_check():
    module.self_check()


def test_sigmoid_and_gru_retention():
    assert module.sigmoid(-1000) == 0.0
    assert module.sigmoid(1000) == 1.0
    assert math.isclose(module.gru_mix(0.8, -0.4, 1.0), 0.8)
    assert math.isclose(module.gru_mix(0.8, -0.4, 0.0), -0.4)


def test_swiglu_not_probability_gate():
    assert module.silu(-1.0) < 0
    assert module.silu(3.0) > 1
    x = 0.7
    f = lambda t: t * module.sigmoid(t)
    g = module.sigmoid(x)
    assert math.isclose(module.finite_difference(f, x), g + x * g * (1-g), abs_tol=1e-9)
