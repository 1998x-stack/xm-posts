"""Deterministic minimal LSTM tests; no stochastic training claims."""
from pathlib import Path
import importlib.util
import math

FILE = Path(__file__).resolve().parents[1] / "posts" / "architectures" / "lstm" / "mini_lstm.py"
spec = importlib.util.spec_from_file_location("mini_lstm_article", FILE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

def test_deterministic_step():
    mod.self_check()
    assert mod.retention(1.0, 100) == 1
    assert mod.retention(0.0, 100) == 0

def test_gate_order_and_dimensions():
    w = [[0.0,0.0,0.0] for _ in range(8)] # H=2, D=1
    h, c = mod.step([1.0],[0.0,0.0],[2.0,4.0],w,[0.0]*8)
    assert c == [1.0,2.0]
    assert all(math.isclose(a,0.5*math.tanh(b)) for a,b in zip(h,c))

def test_invalid_dimensions():
    try:
        mod.step([1.0],[0.0],[0.0],[[1.0]] * 4,[0.0]*4)
    except AssertionError:
        pass
    else:
        raise AssertionError("Expected shape validation")
