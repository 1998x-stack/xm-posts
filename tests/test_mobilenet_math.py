"""Deterministic MobileNet V1 math tests; standalone pure Python implementation."""
from importlib import util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "posts" / "architectures" / "mobilenet" / "mini_mobilenet.py"
spec = util.spec_from_file_location("mini_mobilenet_article", PATH)
module = util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_operator_count_and_ratio():
    full, ds = module.cost(k=3, m=32, n=64, h=56, w=56)
    assert full == 57_802_752
    assert ds == 7_325_696
    assert round(full / ds, 2) == 7.89


def test_width_and_resolution_are_different_axes():
    full, ds = module.cost(k=3, m=16, n=32, h=28, w=28)
    assert full == 3_612_672
    assert ds == (9 * 16 + 16 * 32) * 28 * 28


def test_factorizable_kernel_is_equal():
    assert module.check_factorized_equivalence()


def test_invalid_shapes_are_rejected():
    import pytest
    with pytest.raises(ValueError):
        module.cost(k=3, m=0, n=64, h=56, w=56)
