"""Regression checks for the paper's standalone reference calculations."""
import importlib.util
from pathlib import Path

def test_noisynet_reference_math():
    path = Path(__file__).resolve().parents[1] / "posts" / "reinforcement-learning" / "noisynet" / "mini_noisynet.py"
    spec = importlib.util.spec_from_file_location("mini_noisynet", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module._checks()
