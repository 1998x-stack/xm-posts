"""Minimal single-agent UCT search on a deterministic two-stage reward tree.
No neural net, adversary, state transpositions, or benchmark claim.
Run: python posts/reinforcement-learning/mcts/mini_mcts.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import inf, log, sqrt
import random

ACTION_MAP = {
    (): ("L", "R"),
    ("L",): ("l1", "l2"),
    ("R",): ("r1", "r2"),
}
TERMINAL_REWARD = {
    ("L", "l1"): 0.2,
    ("L", "l2"): 0.5,
    ("R", "r1"): 0.8,
    ("R", "r2"): 1.0,
}

@dataclass
class Node:
    state: tuple[str, ...]
    parent: "Node | None" = None
    visits: int = 0
    total: float = 0.0
    children: list["Node"] = field(default_factory=list)
    untried: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.untried = list(ACTION_MAP.get(self.state, ()))

    @property
    def mean(self) -> float:
        return self.total / self.visits if self.visits else 0.0


def ucb1(parent_visits: int, child_visits: int, child_mean: float, c: float) -> float:
    """UCB on a parent whose child actions share one reward scale."""
    if c < 0:
        raise ValueError("c must be nonnegative")
    if child_visits == 0:
        return inf
    if parent_visits < child_visits or parent_visits < 1:
        raise ValueError("invalid visit counts")
    return child_mean + c * sqrt(log(parent_visits) / child_visits)


def search(iterations: int = 500, c: float = 1.0, seed: int = 17) -> Node:
    """Expand one node per iteration; random rollouts; backup observed reward."""
    if iterations < 1:
        raise ValueError("iterations must be positive")
    rng = random.Random(seed)
    root = Node(())
    for _ in range(iterations):
        node = root
        # Selection: UCT among fully expanded parents.
        while not node.untried and node.children:
            node = max(node.children,
                       key=lambda child: ucb1(node.visits, child.visits, child.mean, c))
        # Expansion: one new child, never an existing child.
        if node.untried:
            action = node.untried.pop(rng.randrange(len(node.untried)))
            child = Node(node.state + (action,), node)
            node.children.append(child)
            node = child
        # Simulation: take random actions until a terminal outcome.
        state = node.state
        while state not in TERMINAL_REWARD:
            state += (rng.choice(ACTION_MAP[state]),)
        reward = TERMINAL_REWARD[state]
        # Backprop: single-agent scalar reward, identical at every ancestor.
        while node is not None:
            node.visits += 1
            node.total += reward
            node = node.parent
    return root


def check() -> None:
    assert ucb1(20, 5, 0.5, 0.0) == 0.5
    assert ucb1(20, 0, 0.0, 0.5) == inf
    try:
        ucb1(1, 2, 0.3, 1.0)
    except ValueError:
        pass
    else:
        raise AssertionError("bad visit counts should fail")
    root = search()
    assert root.visits == 500
    assert sum(child.visits for child in root.children) == root.visits
    assert len(root.children) == 2
    winner = max(root.children, key=lambda node: node.visits)
    assert winner.state == ("R",)
    assert 0 <= winner.mean <= 1
    assert search(seed=17).total == root.total  # deterministic RNG
    print("MCTS/UCT deterministic invariants passed:", winner.state, winner.visits)


if __name__ == "__main__":
    check()
