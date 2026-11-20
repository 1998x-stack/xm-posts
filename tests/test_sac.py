"""Tests that isolate exact SAC equation invariants; no network or Gym needed."""
import importlib.util
import math
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "posts" / "reinforcement-learning" / "sac" / "mini_sac.py"
spec = importlib.util.spec_from_file_location("mini_sac", source)
sac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sac)

def test_soft_target_and_terminal():
    assert math.isclose(sac.soft_target(1, .9, False, 5, 3, -.5, .2), 3.79)
    assert sac.soft_target(1, .9, True, 5, 3, -.5, .2) == 1
    assert sac.soft_target(1, .9, False, 3, 5, -.5, .2) == sac.soft_target(1, .9, False, 5, 3, -.5, .2)

def test_actor_loss_and_alpha():
    assert math.isclose(sac.actor_loss(-.5, 4, 3, .2), -3.1)
    assert sac.temperature_objective(.2, -.2, .5) == -.2 * .3
    assert sac.temperature_objective(.2, -1.5, .5) == .2

def test_squashed_gaussian_correction():
    x = sac.tanh_gaussian_logprob(0, 0, 1)
    assert math.isclose(x, -.5 * math.log(2 * math.pi), abs_tol=1e-12)
    for u in (-100, -5, -1, 0, 1, 5, 100):
        assert math.isfinite(sac.tanh_gaussian_logprob(u, 0, 1))
    assert math.isclose(sac.tanh_gaussian_logprob(1, 0, 1), sac.tanh_gaussian_logprob(-1, 0, 1))

def test_boltzmann_is_only_toy_model():
    cold=sac.boltzmann_probs((3,2,0), .25)
    hot=sac.boltzmann_probs((3,2,0), 2.0)
    assert cold[0] > hot[0] > hot[1] > hot[2]
    assert math.isclose(sum(cold), 1)
    assert math.isclose(sum(hot), 1)

def test_invalid_coefficients():
    import pytest
    with pytest.raises(ValueError):
        sac.soft_target(1, 1.1, False, 2, 3, -1, .2)
    with pytest.raises(ValueError):
        sac.tanh_gaussian_logprob(0, 0, 0)
