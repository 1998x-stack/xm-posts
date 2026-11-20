"""Numerical invariants for the educational AdamW implementation."""
from __future__ import annotations
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import sys

FILE = Path(__file__).resolve().parents[1] / "posts/foundations/adamw/mini_adamw.py"
spec = spec_from_file_location("mini_adamw", FILE)
module = module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def test_adamw_never_puts_decay_in_moments():
    coupled, adamw = module.demo()
    assert adamw.m == [0.0, 0.0]
    assert adamw.v == [0.0, 0.0]
    assert coupled.m != adamw.m
    assert coupled.v != adamw.v


def test_two_coordinate_fixed_preconditioner_derivation():
    alpha = 0.1
    penalty = 0.1
    s = [1, 5]
    coupled = [1 - alpha * penalty / x for x in s]
    decoupled = [1 - alpha * penalty] * 2
    assert abs(coupled[0] - 0.99) < 1e-12
    assert abs(coupled[1] - 0.998) < 1e-12
    assert decoupled == [0.99, 0.99]


def test_longer_trajectory_no_decay_is_identical():
    state = module.State([1.0, -2.0], [0.0, 0.0], [0.0, 0.0])
    for grad in ([0.4, -0.2], [0.0, 0.1], [-0.3, 0.3]):
        coupled = module.update(state, list(grad), weight_decay=0, decoupled=False)
        decoupled = module.update(state, list(grad), weight_decay=0, decoupled=True)
        assert coupled == decoupled
        state = coupled
