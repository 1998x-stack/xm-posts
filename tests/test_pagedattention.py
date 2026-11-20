"""Logical mapping, partial-block CoW, fork and release semantics."""
import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "posts/inference/pagedattention/mini_paged_cache.py"
spec = importlib.util.spec_from_file_location("mini_paged_cache", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
PagedCache = module.PagedCache

def test_append_and_cross_block_order():
    cache = PagedCache(4)
    cache.new_request("x")
    for i in range(10):
        cache.append("x", i)
    assert cache.read("x") == list(range(10))
    assert len(cache.tables["x"]) == 3
    cache.assert_consistent()

def test_copy_on_write_preserves_prefix():
    cache = PagedCache(4)
    cache.new_request("a")
    for i in range(6):
        cache.append("a", i)
    first, second = cache.tables["a"]
    cache.fork("a", "b")
    assert cache.refs[first] == cache.refs[second] == 2
    cache.append("b", 60)
    assert cache.tables["b"][0] == first
    assert cache.tables["b"][1] != second
    assert cache.read("a") == list(range(6))
    assert cache.read("b") == list(range(6)) + [60]
    cache.assert_consistent()
    cache.release("a")
    assert cache.read("b")[-1] == 60
    cache.release("b")
    assert not cache.pages

def test_full_block_allocation_does_not_copy():
    cache = PagedCache(2)
    cache.new_request("a")
    cache.append("a", 1)
    cache.append("a", 2)
    old = cache.tables["a"][0]
    cache.fork("a", "b")
    cache.append("b", 3)
    assert cache.tables["b"] == [old, old + 1]
    assert cache.refs[old] == 2
    cache.assert_consistent()

def test_invalid_block_size_and_duplicate():
    import pytest
    with pytest.raises(ValueError):
        PagedCache(0)
    c = PagedCache()
    c.new_request("q")
    with pytest.raises(ValueError):
        c.new_request("q")
