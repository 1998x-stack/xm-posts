"""Smoke tests for the explanatory UCT code. No benchmark performance claims."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/mcts"))
from mini_mcts import check, search, ucb1

def test_uct_minimal_example():
    check()

def test_reproducible_tree():
    a,b=search(300,c=1.0,seed=9),search(300,c=1.0,seed=9)
    assert a.visits==b.visits==300
    assert [(x.state,x.visits,x.total) for x in a.children] == [(x.state,x.visits,x.total) for x in b.children]
