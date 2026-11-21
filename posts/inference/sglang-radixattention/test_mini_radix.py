import importlib.util
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location("radix_demo", Path(__file__).with_name("mini_radix.py"))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
RadixTree = module.RadixTree


def test_insert_branch_and_longest_prefix():
    t = RadixTree()
    t.insert(["SYS", "A", "Q1"])
    assert t.contains(["SYS", "A", "Q1"])
    assert t.longest_prefix(["SYS", "A", "Q2"]) == 2
    t.insert(["SYS", "A", "Q2"])
    assert t.contains(["SYS", "A", "Q1"])
    assert t.contains(["SYS", "A", "Q2"])
    assert not t.contains(["SYS", "A"])
    assert t.longest_prefix(["SYS", "B"]) == 1
    assert t.longest_prefix(["OTHER"]) == 0


def test_exact_prefix_insertion_and_empty():
    t = RadixTree()
    t.insert(["a", "b", "c"])
    t.insert(["a", "b"])
    assert t.contains(["a", "b"])
    assert t.contains(["a", "b", "c"])
    t.insert([])
    assert t.contains([])
    assert t.longest_prefix(["a", "b", "c", "d"]) == 3


def test_split_in_the_middle_of_compressed_edge():
    t = RadixTree()
    t.insert(["a", "b", "c", "d"])
    t.insert(["a", "b", "x"])
    assert t.longest_prefix(["a", "b", "c", "z"]) == 3
    assert t.contains(["a", "b", "x"])
    assert t.contains(["a", "b", "c", "d"])
