"""Deterministic unit tests for group normalization, clipping and k3."""
from pathlib import Path
import sys
import math
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "posts" / "training" / "grpo"))
from mini_grpo import advantages, clipped_surrogate, kl_k3


def test_group_advantages_and_constant_rewards():
    assert advantages([1, 0, 1, 0]) == [1, -1, 1, -1]
    assert advantages([1, 1, 1, 1]) == [0, 0, 0, 0]
    with pytest.raises(ValueError):
        advantages([])


def test_uneven_reward_group():
    a = advantages([1, 1, 1, 0])
    assert abs(sum(a)) < 1e-12
    assert math.isclose(sum(x*x for x in a)/4, 1.0)


def test_clipping_with_signs():
    assert math.isclose(clipped_surrogate(1.5, 1, 0.2), 1.2)
    assert math.isclose(clipped_surrogate(0.5, -1, 0.2), -0.8)
    with pytest.raises(ValueError):
        clipped_surrogate(0.0, 1.0, 0.2)


def test_k3_positive_and_zero():
    assert kl_k3(1.0) == 0.0
    assert kl_k3(0.5) > 0
    assert kl_k3(2.0) > 0
    with pytest.raises(ValueError):
        kl_k3(-1.0)
