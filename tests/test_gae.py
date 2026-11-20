"""Verify the standalone GAE article's mathematical kernel."""
from pathlib import Path
import runpy

SOURCE = Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/gae/gae.py"

def test_gae_numerical_invariants():
    runpy.run_path(str(SOURCE))["self_test"]()

def test_gae_bootstrap_at_rollout_boundary():
    f = runpy.run_path(str(SOURCE))["gae"]
    assert f([2.], [1., 3.], [False], gamma=.5, lam=.8) == [2.5]

def test_gae_cut_at_true_terminal():
    f = runpy.run_path(str(SOURCE))["gae"]
    assert f([1., 2.], [0., 0., 0.], [True, True], gamma=1, lam=1) == [1., 2.]
