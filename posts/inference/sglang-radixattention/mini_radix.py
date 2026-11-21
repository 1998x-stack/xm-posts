"""Compact token radix tree for education; no KV tensors or concurrency."""
from dataclasses import dataclass, field


@dataclass
class Node:
    edges: list = field(default_factory=list)  # (tuple of tokens, child node)
    terminal: bool = False


class RadixTree:
    def __init__(self):
        self.root = Node()

    @staticmethod
    def _lcp(a, b):
        k = 0
        while k < min(len(a), len(b)) and a[k] == b[k]:
            k += 1
        return k

    def longest_prefix(self, tokens):
        tokens = tuple(tokens)
        node, matched = self.root, 0
        while matched < len(tokens):
            found = False
            for edge, child in node.edges:
                n = self._lcp(edge, tokens[matched:])
                if n:
                    matched += n
                    if n < len(edge):
                        return matched
                    node, found = child, True
                    break
            if not found:
                break
        return matched

    def insert(self, tokens):
        tokens = tuple(tokens)
        node, remaining = self.root, tokens
        while remaining:
            for index, (edge, child) in enumerate(node.edges):
                n = self._lcp(remaining, edge)
                if not n:
                    continue
                if n == len(edge):
                    node, remaining = child, remaining[n:]
                    break
                branch = Node(edges=[(edge[n:], child)])
                node.edges[index] = (edge[:n], branch)
                remaining = remaining[n:]
                node = branch
                break
            else:
                node.edges.append((remaining, Node(terminal=True)))
                return
        node.terminal = True

    def contains(self, tokens):
        tokens = tuple(tokens)
        node, remaining = self.root, tokens
        while remaining:
            for edge, child in node.edges:
                if remaining[:len(edge)] == edge:
                    remaining = remaining[len(edge):]
                    node = child
                    break
            else:
                return False
        return node.terminal


if __name__ == "__main__":
    t = RadixTree()
    for x in [('SYS', 'A', 'Q1'), ('SYS', 'A', 'Q2')]:
        print('match', x, t.longest_prefix(x))
        t.insert(x)
    print('new branch match', t.longest_prefix(('SYS', 'A', 'Q3')))
