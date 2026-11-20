"""Verify the independent Bellman classroom MDP without external RL packages."""
import importlib.util
from pathlib import Path


def test_bellman_classroom_invariants():
    file = Path(__file__).resolve().parents[1] / "posts" / "reinforcement-learning" / "bellman-equations" / "mini_bellman.py"
    spec = importlib.util.spec_from_file_location("bellman_math", file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.self_test()
