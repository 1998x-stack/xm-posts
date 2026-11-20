"""Deterministic checks for the DeltaNet NeurIPS 2024 teaching post."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "posts/architectures/deltanet/mini_deltanet.py"
spec = importlib.util.spec_from_file_location("mini_deltanet", MODULE)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_deltanet_toy_cases():
    mod.self_test()


def test_beta_zero_and_unit_overwrite():
    s = [[0.2, 0.0]]
    assert mod.delta_step(s, [1.0, 0.0], [1.0], 0) == s
    assert mod.read(mod.delta_step(s, [1.0, 0.0], [1.0], 1), [1.0, 0.0]) == [1.0]


def test_nonorthogonal_keys_interfere():
    from math import sqrt
    s = mod.delta_step([[0.0, 0.0]], [1.0, 0.0], [1.0], 1)
    later = mod.delta_step(s, [1/sqrt(2), 1/sqrt(2)], [0.0], 1)
    assert mod.read(later, [1.0, 0.0])[0] < 1.0


def test_reject_bad_shapes_and_beta():
    import pytest
    with pytest.raises(ValueError):
        mod.delta_step([[0.0, 0.0]], [1.0], [1.0], 0.5)
    with pytest.raises(ValueError):
        mod.delta_step([[0.0, 0.0]], [1.0, 0.0], [1.0], 1.2)
