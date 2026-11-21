from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "posts"
    / "training"
    / "reward-hacking"
    / "toy_demo.py"
)
SPEC = importlib.util.spec_from_file_location("reward_hacking_toy", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_baseline_matches_true_objective_optimum() -> None:
    result = MODULE.evaluate(0.0)
    assert result["x_star"] == pytest.approx(1.0)
    assert result["proxy_reward"] == pytest.approx(0.0)
    assert result["true_reward"] == pytest.approx(0.0)


def test_alpha_two_reproduces_the_article_example() -> None:
    result = MODULE.evaluate(2.0)
    assert result["x_star"] == pytest.approx(2.0)
    assert result["proxy_reward"] == pytest.approx(3.0)
    assert result["true_reward"] == pytest.approx(-1.0)


def test_stronger_proxy_pressure_increases_proxy_and_decreases_true_reward() -> None:
    low = MODULE.evaluate(1.0)
    high = MODULE.evaluate(3.0)
    assert high["proxy_reward"] > low["proxy_reward"]
    assert high["true_reward"] < low["true_reward"]


def test_negative_alpha_is_rejected() -> None:
    with pytest.raises(ValueError):
        MODULE.evaluate(-0.1)
