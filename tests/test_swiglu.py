"""Deterministic tests for the published SwiGLU educational kernel."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "posts" / "architectures" / "swiglu" / "mini_swiglu.py"


def test_swiglu_mechanism_and_parameter_budget():
    spec = importlib.util.spec_from_file_location("mini_swiglu", SRC)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.self_test()
    assert module.weight_counts(768, 3072, 2048)[0] == 4_718_592
