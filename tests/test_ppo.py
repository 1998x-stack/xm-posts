"""Verify the standalone educational PPO maths example deterministically."""
import importlib.util
import math
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/'posts/reinforcement-learning/ppo/mini_ppo.py'

def load():
    spec=importlib.util.spec_from_file_location('ppo_example',PATH)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_policy_ratio_sign_cases():
    m=load()
    m.check()
    assert math.isclose(m.clipped_objective(1.5,2),2.4)
    assert math.isclose(m.clipped_objective(0.5,-2),-1.6)
    assert math.isclose(m.clipped_objective(1.5,-2),-3)
    assert math.isclose(m.clipped_objective(0.5,2),1.0)

def test_gae_terminal_and_bootstrap():
    m=load()
    assert m.gae([1.0],[0,500],[True])==[1.0]
    assert m.gae([1.0],[0,2],[False],1.0,1.0)==[3.0]

def test_reject_invalid_probabilities():
    m=load()
    with pytest.raises(ValueError):
        m.clipped_objective(0,1.0)
    with pytest.raises(ValueError):
        m.clipped_objective(1.0,1.0,eps=1.0)
