#!/usr/bin/env python3
"""Tiny deterministic *logical* paged KV cache simulator, not a vLLM kernel.

Run: python posts/inference/pagedattention/mini_paged_cache.py
No external dependencies. Each stored integer stands in for a token's KV pair.
"""
from __future__ import annotations

class PagedCache:
    def __init__(self, block_size: int = 4):
        if block_size < 1:
            raise ValueError("block_size must be positive")
        self.block_size = block_size
        self.pages: dict[int, list[int | None]] = {}
        self.refs: dict[int, int] = {}
        self.tables: dict[str, list[int]] = {}
        self.lengths: dict[str, int] = {}
        self.next_id = 1

    def _new(self, values: list[int | None] | None = None) -> int:
        page_id = self.next_id
        self.next_id += 1
        self.pages[page_id] = list(values) if values is not None else [None] * self.block_size
        self.refs[page_id] = 1
        return page_id

    def new_request(self, request: str) -> None:
        if request in self.tables:
            raise ValueError("duplicate request")
        self.tables[request] = []
        self.lengths[request] = 0

    def append(self, request: str, token: int) -> None:
        length = self.lengths[request]
        offset = length % self.block_size
        if offset == 0:
            self.tables[request].append(self._new())
        else:
            old_id = self.tables[request][-1]
            if self.refs[old_id] > 1:
                new_id = self._new(self.pages[old_id])
                self.refs[old_id] -= 1
                self.tables[request][-1] = new_id
        page_id = self.tables[request][-1]
        self.pages[page_id][offset] = token
        self.lengths[request] += 1

    def fork(self, source: str, target: str) -> None:
        if target in self.tables:
            raise ValueError("duplicate request")
        self.tables[target] = self.tables[source].copy()
        self.lengths[target] = self.lengths[source]
        for page_id in self.tables[target]:
            self.refs[page_id] += 1

    def read(self, request: str) -> list[int]:
        result: list[int] = []
        for index in range(self.lengths[request]):
            page_id = self.tables[request][index // self.block_size]
            value = self.pages[page_id][index % self.block_size]
            assert value is not None
            result.append(value)
        return result

    def release(self, request: str) -> None:
        for page_id in self.tables.pop(request):
            self.refs[page_id] -= 1
            if self.refs[page_id] == 0:
                del self.refs[page_id]
                del self.pages[page_id]
        del self.lengths[request]

    def assert_consistent(self) -> None:
        from collections import Counter
        observed = Counter(page_id for table in self.tables.values() for page_id in table)
        assert dict(observed) == self.refs
        assert set(self.refs) == set(self.pages)
        for request, table in self.tables.items():
            length = self.lengths[request]
            assert len(table) == (length + self.block_size - 1) // self.block_size

def demo() -> None:
    cache = PagedCache(block_size=4)
    cache.new_request("prompt")
    for token in range(6):
        cache.append("prompt", token)
    assert cache.read("prompt") == list(range(6))
    original_last = cache.tables["prompt"][-1]
    cache.fork("prompt", "candidate")
    assert cache.refs[original_last] == 2
    cache.append("candidate", 99)  # copy-on-write: shared partial page
    assert cache.tables["candidate"][-1] != original_last
    assert cache.read("prompt") == list(range(6))
    assert cache.read("candidate") == list(range(6)) + [99]
    cache.assert_consistent()
    cache.release("candidate")
    cache.release("prompt")
    assert not cache.pages and not cache.refs
    print("paged cache demo: all invariants passed")

if __name__ == "__main__":
    demo()
