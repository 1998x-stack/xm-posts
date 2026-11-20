"""Deterministic educational DDPG assertions, no Gym or MuJoCo needed."""
from pathlib import Path
import importlib.util
import math
import pytest

PATH = Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/ddpg/mini_ddpg.py"


def module():
    spec = importlib.util.spec_from_file_location("ddpg_math", PATH)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_core_math():
    m = module()
    m.check()
    assert math.isclose(m.bellman_target(-2.0, 0.9, 10.0, False), 7.0)
    assert m.bellman_target(-2.0, 0.9, 10.0, True) == -2.0
    assert math.isclose(m.polyak_update(3.0, 11.0, .05), 3.4)


def test_gradient_direction_with_chain_rule():
    m = module()
    assert math.isclose(m.actor_gradient(2.0, .2), 2.4)
    h = 1e-6
    numerical = (m.critic(2, m.actor(2, .2 + h))
                 - m.critic(2, m.actor(2, .2 - h))) / (2 * h)
    assert math.isclose(numerical, m.actor_gradient(2, .2), rel_tol=1e-7)


def test_invalid_bounds_and_replay():
    m = module()
    with pytest.raises(ValueError):
        m.bellman_target(1, -0.1, 2, False)
    with pytest.raises(ValueError):
        m.polyak_update(0, 1, 2)
    with pytest.raises(ValueError):
        m.critic_mse([1], [1, 2])
    with pytest.raises(ValueError):
        m.replay_sample([(1,)], 2)
    with pytest.raises(ValueError):
        m.ou_next(0, 0, 1, .1, 0, 0)
