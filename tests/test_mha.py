"""Shape and causal-mask regression tests for Multi-Head Attention."""
import importlib.util
from pathlib import Path
import math
import pytest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "posts/architectures/multi-head-attention/mini_mha.py"
spec = importlib.util.spec_from_file_location("mini_mha", SOURCE)
assert spec is not None and spec.loader is not None
mha = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mha)


def test_reference_self_check():
    mha.self_test()


@pytest.mark.parametrize("head_count", [1, 2, 4])
def test_shapes_and_causal_mask(head_count):
    x = [[float((i + j) % 4) for j in range(4)] for i in range(3)]
    w = mha.identity(4)
    y, a = mha.self_attention(x, w, w, w, w, heads=head_count, causal=True)
    assert len(y) == 3 and all(len(row) == 4 for row in y)
    assert len(a) == head_count
    for head in a:
        assert len(head) == 3 and all(len(row) == 3 for row in head)
        for i, row in enumerate(head):
            assert math.isclose(sum(row), 1.0, abs_tol=1e-12)
            assert all(v == 0.0 for v in row[i + 1:])


def test_unmasked_attention_can_see_future():
    w = mha.identity(2)
    _, weights = mha.self_attention([[1., 0.], [0., 1.]], w, w, w, w,
                                    heads=1, causal=False)
    assert weights[0][0][1] > 0


def test_invalid_shapes():
    with pytest.raises(ValueError):
        mha.project([[1., 2.]], [[1.]])
    with pytest.raises(ValueError):
        mha.self_attention([[1., 2.]], mha.identity(2), mha.identity(2),
                           mha.identity(2), mha.identity(2), heads=3, causal=True)
