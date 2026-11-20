"""Deterministic tests for the educational TD3 math kernel."""
from pathlib import Path
import importlib.util
import math
import pytest

FILE = Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/td3/mini_td3.py"


def module():
    spec = importlib.util.spec_from_file_location("td3_minimal", FILE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_td3_targets_and_delay():
    m = module()
    m.check()
    assert m.clipped_double_target(1, .9, 10, 6, True) == 1
    assert math.isclose(m.clipped_double_target(1, .9, 10, 6, False), 6.4)
    assert m.policy_and_target_update(4, 2)
    assert not m.policy_and_target_update(3, 2)


def test_target_policy_noise_and_action_limits():
    m = module()
    assert m.target_action(.8, .9, .5, -1, 1) == 1
    assert math.isclose(m.target_action(.2, -.3, .5, -1, 1), -.1)
    with pytest.raises(ValueError):
        m.target_action(0, 0, -1, -1, 1)
    with pytest.raises(ValueError):
        m.clipped_double_target(0, 1.01, 1, 2, False)
    with pytest.raises(ValueError):
        m.policy_and_target_update(0)
    with pytest.raises(ValueError):
        m.polyak(10, 0, -0.1)
    with pytest.raises(ValueError):
        m.twin_critic_mse([], [], [])


def test_actor_first_critic_gradient():
    m = module()
    s, phi, h = 1.5, -.1, 1e-6
    numerical = (m.toy_first_critic(s, m.toy_actor(s, phi+h))
                 - m.toy_first_critic(s, m.toy_actor(s, phi-h))) / (2*h)
    assert math.isclose(numerical, m.actor_gradient(s, phi), rel_tol=1e-8)
