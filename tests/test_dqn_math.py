"""DQN mathematics smoke regression; no network or Atari dependencies."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/dqn/mini_dqn.py"
spec = importlib.util.spec_from_file_location("mini_dqn", MODULE)
dqn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dqn)

def test_dqn_invariants():
    dqn.check()

def test_terminal_bootstrap_mask():
    assert dqn.td_target(-1, .99, True, [100, 200]) == -1

def test_negative_td_huber_symmetry():
    assert dqn.huber(-1.58) == dqn.huber(1.58)
