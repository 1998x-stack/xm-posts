"""Deterministic mathematical invariants for the Adam explainer."""
from pathlib import Path
import importlib.util
import math

MODULE = Path(__file__).resolve().parents[1] / "posts/foundations/adam/mini_adam.py"
spec = importlib.util.spec_from_file_location("mini_adam", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)
Adam = mod.Adam


def test_first_step_matches_algorithm_one():
    optimizer = Adam(2)
    out = optimizer.step([3.0, -2.0], [2.0, -4.0])
    assert math.isclose(optimizer.m[0], 0.2, abs_tol=1e-14)
    assert math.isclose(optimizer.v[0], 0.004, abs_tol=1e-14)
    assert math.isclose(out[0], 3 - 0.001 * 2 / (2 + 1e-8), abs_tol=1e-13)
    assert math.isclose(out[1], -2 + 0.001 * 4 / (4 + 1e-8), abs_tol=1e-13)


def test_momentum_survives_zero_current_gradient():
    optimizer = Adam(1)
    theta = optimizer.step([3.0], [2.0])
    later = optimizer.step(theta, [0.0])
    assert later[0] < theta[0]
    assert optimizer.t == 2


def test_adamw_decay_does_not_enter_moment_buffers():
    adamw = Adam(1, lr=0.1, weight_decay=0.1, decoupled_weight_decay=True)
    coupled = Adam(1, lr=0.1, weight_decay=0.1)
    a = adamw.step([2.0], [0.0])
    b = coupled.step([2.0], [0.0])
    assert math.isclose(a[0], 1.98, abs_tol=1e-12)
    assert adamw.m[0] == 0.0 and adamw.v[0] == 0.0
    assert b[0] < a[0] and coupled.m[0] > 0


def test_amsgrad_keeps_non_decreasing_raw_second_moment_upper_bound():
    optimizer = Adam(1, amsgrad=True, betas=(0.9, 0.5))
    theta = [1.0]
    values = []
    for g in [4.0, 0.0, 0.0]:
        theta = optimizer.step(theta, [g])
        values.append(optimizer.v_max[0])
    assert values == [8.0, 8.0, 8.0]


def test_shape_and_parameter_validation():
    import pytest
    with pytest.raises(ValueError):
        Adam(0)
    with pytest.raises(ValueError):
        Adam(1, betas=(0.9, 1.0))
    with pytest.raises(ValueError):
        Adam(1).step([1.0], [1.0, 2.0])
    with pytest.raises(ValueError):
        Adam(1).step([math.nan], [1.0])
