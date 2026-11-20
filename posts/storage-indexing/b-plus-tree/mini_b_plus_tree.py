"""Minimal in-memory B+ tree: unique integer keys, insertion, lookup, range scan.

Teaching code only: not persistent, concurrent, transactional, or deletion-capable.
Internal separators use min-key-of-right-child convention.
"""
from __future__ import annotations
from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from random import Random

@dataclass
class Leaf:
    keys: list[int] = field(default_factory=list)
    values: list[str] = field(default_factory=list)
    next: "Leaf | None" = None

@dataclass
class Internal:
    keys: list[int] = field(default_factory=list)
    children: list["Node"] = field(default_factory=list)

Node = Leaf | Internal

class BPlusTree:
    def __init__(self, max_keys: int = 3):
        if max_keys < 3:
            raise ValueError("max_keys must be >= 3 for this demonstration")
        self.max_keys = max_keys
        self.root: Node = Leaf()

    def _leaf(self, key: int) -> Leaf:
        node = self.root
        while isinstance(node, Internal):
            node = node.children[bisect_right(node.keys, key)]
        return node

    def find(self, key: int) -> str | None:
        leaf = self._leaf(key)
        i = bisect_left(leaf.keys, key)
        return leaf.values[i] if i < len(leaf.keys) and leaf.keys[i] == key else None

    def range_query(self, lo: int, hi: int) -> list[tuple[int, str]]:
        if lo > hi:
            return []
        leaf: Leaf | None = self._leaf(lo)
        result: list[tuple[int, str]] = []
        first = True
        while leaf is not None:
            start = bisect_left(leaf.keys, lo) if first else 0
            first = False
            for i in range(start, len(leaf.keys)):
                if leaf.keys[i] > hi:
                    return result
                result.append((leaf.keys[i], leaf.values[i]))
            leaf = leaf.next
        return result

    def insert(self, key: int, value: str) -> None:
        split = self._insert(self.root, key, value)
        if split is not None:
            separator, right = split
            self.root = Internal([separator], [self.root, right])

    def _insert(self, node: Node, key: int, value: str) -> tuple[int, Node] | None:
        if isinstance(node, Leaf):
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) <= self.max_keys:
                return None
            cut = (len(node.keys) + 1) // 2
            right = Leaf(node.keys[cut:], node.values[cut:], node.next)
            node.keys = node.keys[:cut]
            node.values = node.values[:cut]
            node.next = right
            return right.keys[0], right
        i = bisect_right(node.keys, key)
        split = self._insert(node.children[i], key, value)
        if split is None:
            return None
        separator, right = split
        node.keys.insert(i, separator)
        node.children.insert(i + 1, right)
        if len(node.keys) <= self.max_keys:
            return None
        mid = len(node.keys) // 2
        promoted = node.keys[mid]
        right_node = Internal(node.keys[mid + 1:], node.children[mid + 1:])
        node.keys = node.keys[:mid]
        node.children = node.children[:mid + 1]
        return promoted, right_node

    def assert_invariants(self) -> None:
        depths: set[int] = set()
        leaves: list[Leaf] = []
        minimum = (self.max_keys + 1) // 2
        def visit(node: Node, depth: int, root: bool) -> tuple[int, int] | None:
            assert len(node.keys) <= self.max_keys
            assert node.keys == sorted(set(node.keys))
            if isinstance(node, Leaf):
                assert len(node.keys) == len(node.values)
                if not root:
                    assert len(node.keys) >= minimum
                depths.add(depth)
                leaves.append(node)
                return (node.keys[0], node.keys[-1]) if node.keys else None
            assert len(node.children) == len(node.keys) + 1
            if not root:
                assert len(node.children) >= (self.max_keys + 2) // 2
            ranges = [visit(child, depth + 1, False) for child in node.children]
            assert all(part is not None for part in ranges)
            for i, separator in enumerate(node.keys):
                assert ranges[i][1] < separator == ranges[i + 1][0]
            return (ranges[0][0], ranges[-1][1])
        visit(self.root, 0, True)
        assert len(depths) == 1
        for i, leaf in enumerate(leaves):
            assert leaf.next is (leaves[i + 1] if i + 1 < len(leaves) else None)

def _self_test() -> None:
    for order in (list(range(101)), list(reversed(range(101))),
                  Random(7).sample(range(101), 101)):
        tree = BPlusTree(3)
        for key in order:
            tree.insert(key, str(key))
            tree.assert_invariants()
        tree.insert(50, "updated")
        tree.assert_invariants()
        assert tree.find(50) == "updated"
        assert tree.find(102) is None
        assert [k for k, _ in tree.range_query(25, 45)] == list(range(25, 46))
        assert tree.range_query(45, 25) == []
    print("B+ tree self-tests passed")

if __name__ == "__main__":
    _self_test()
