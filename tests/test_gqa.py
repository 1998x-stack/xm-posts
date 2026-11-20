"""Deterministic group mapping and numerical tests for the GQA teaching post."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "posts/architectures/gqa/mini_gqa.py"
spec = importlib.util.spec_from_file_location("mini_gqa", MODULE)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def test_gqa_endpoints_and_memory():
    module.self_test()


def test_group_error_handling():
    import pytest
    with pytest.raises(ValueError):
        module.group_index(0, 8, 3)
    with pytest.raises(ValueError):
        module.group_index(8, 8, 2)
    with pytest.raises(ValueError):
        module.gqa_step([[1.0]], [], [])
    with pytest.raises(ValueError):
        module.kv_cache_bytes(1, 1, 0, 1, 1, 2)


def test_gqa_individual_query_heads_stay_distinct():
    q = [[1.0, 0.0], [0.0, 1.0]]
    keys = [[[1.0, 0.0], [0.0, 1.0]]]
    vals = [[[10.0, 0.0], [0.0, 10.0]]]
    outputs = module.gqa_step(q, keys, vals)
    assert len(outputs) == 2
    assert outputs[0] != outputs[1]
