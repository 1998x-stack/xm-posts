"""Deterministic CPU-level correctness checks for the FlashAttention tutorial."""
import importlib.util
from pathlib import Path
import math
import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "posts/systems/flashattention/mini_attention.py"
spec = importlib.util.spec_from_file_location("flashattention_toy", SRC)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize("causal", [False, True])
@pytest.mark.parametrize("block_size", [1, 2, 3, 9])
def test_streaming_matches_reference(causal, block_size):
    q = [[1., 0.], [0., 1.], [1., 1.], [-2., 3.]]
    k = [[0., 1.], [1., 0.], [1., 1.], [2., -1.]]
    v = [[2., 7.], [6., 5.], [10., 3.], [-1., 9.]]
    a = module.reference_attention(q, k, v, causal)
    b = module.streaming_attention(q, k, v, block_size, causal)
    for x, y in zip(a, b):
        assert y == pytest.approx(x, rel=1e-12, abs=1e-12)


def test_large_logits_remain_finite():
    q = [[1000.], [1001.], [-1000.]]
    k = [[1000.], [-1000.], [999.]]
    v = [[1.], [4.], [-2.]]
    for causal in (False, True):
        a = module.reference_attention(q, k, v, causal)
        b = module.streaming_attention(q, k, v, 2, causal)
        assert all(math.isfinite(x) for row in b for x in row)
        for x, y in zip(a, b):
            assert y == pytest.approx(x, abs=1e-12)


@pytest.mark.parametrize("block_size", [0, -1])
def test_reject_bad_block(block_size):
    with pytest.raises(ValueError):
        module.streaming_attention([[1.]], [[1.]], [[1.]], block_size)


def test_causal_cannot_peek_future():
    q = [[1.], [1.], [1.]]
    k = [[1.], [1.], [1.]]
    v = [[2.], [4.], [1000.]]
    out = module.streaming_attention(q, k, v, 2, causal=True)
    assert out[0] == pytest.approx([2.])
    assert out[1] == pytest.approx([3.])
    assert out[2] == pytest.approx([(2. + 4. + 1000.) / 3.])


def test_toy_online_example():
    scores = [1., 2., 0.]
    values = [2., 6., 10.]
    weights = [math.exp(s - 2.) for s in scores]
    full = sum(w * v for w, v in zip(weights, values)) / sum(weights)
    assert full == pytest.approx(5.381208408462331)
