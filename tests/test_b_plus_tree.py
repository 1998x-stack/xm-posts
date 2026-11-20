"""Deterministic regression tests for the B+ tree teaching implementation."""
from pathlib import Path
import importlib.util
import random

FILE = Path(__file__).resolve().parents[1] / "posts/storage-indexing/b-plus-tree/mini_b_plus_tree.py"
spec = importlib.util.spec_from_file_location("mini_b_plus_tree", FILE)
import sys
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
BPlusTree = module.BPlusTree

def test_small_split_and_chain():
    tree = BPlusTree(max_keys=3)
    for k in [5, 10, 15, 20, 25, 30, 40, 45, 50, 35, 37, 38]:
        tree.insert(k, str(k))
        tree.assert_invariants()
    assert [k for k, _ in tree.range_query(25, 45)] == [25, 30, 35, 37, 38, 40, 45]
    assert tree.find(27) is None

def test_orders_and_updates():
    for values in [list(range(120)), list(range(119, -1, -1)),
                   random.Random(11).sample(range(120), 120)]:
        tree = BPlusTree(3)
        for k in values:
            tree.insert(k, str(k))
            tree.assert_invariants()
        tree.insert(73, "new")
        assert tree.find(73) == "new"
        tree.assert_invariants()
        assert len(tree.range_query(0, 119)) == 120
        assert tree.range_query(200, 100) == []
