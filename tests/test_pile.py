"""Deterministic tests of the The Pile educational arithmetic."""
import importlib.util
import math
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "posts/datasets/the-pile/mini_pile_metrics.py"
spec = importlib.util.spec_from_file_location("mini_pile_metrics", P)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_weighted_mixture_normalizes():
    shares = module.normalized_mixture(module.PILE_RAW_GIB, module.PILE_EPOCHS)
    assert math.isclose(sum(shares.values()), 1.0)
    assert math.isclose(shares["PubMed Central"],
                        (90.27 * 2) / (227.12 + 90.27 * 2 + 56.21 * 2))


def test_epoch_shift_changes_mixture():
    p = module.normalized_mixture({"a": 100.0, "b": 20.0}, {"a": 1.0, "b": 1.0})
    q = module.normalized_mixture({"a": 100.0, "b": 20.0}, {"a": 1.0, "b": 3.0})
    assert q["b"] > p["b"]
    assert math.isclose(sum(q.values()), 1.0)


def test_bpb_converts_nats_per_token_to_bits_per_byte():
    assert math.isclose(module.bits_per_utf8_byte(math.log(2), 4, 8), 0.5)
    assert math.isclose(module.bits_per_utf8_byte(0.0, 1, 10), 0.0)


def test_invalid_inputs_fail_closed():
    import pytest
    with pytest.raises(ValueError):
        module.normalized_mixture({"a": 1}, {"b": 1})
    with pytest.raises(ValueError):
        module.normalized_mixture({"a": 1}, {"a": 0})
    with pytest.raises(ValueError):
        module.bits_per_utf8_byte(1.0, 3, 0)
