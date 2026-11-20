"""Illustrative AlphaGo 2016 search arithmetic, NOT a complete Go engine."""
from math import sqrt
from typing import Sequence

def mixed_value(network_value: float, rollout_outcome: float, lam: float) -> float:
    """Convex mix in [-1, 1], viewed by the player to move at the leaf."""
    if not 0 <= lam <= 1:
        raise ValueError("lambda must be in [0, 1]")
    return (1.0 - lam) * network_value + lam * rollout_outcome

def puct_score(q: float, prior: float, edge_rollout_visits: int,
               parent_rollout_visits: int, c_puct: float) -> float:
    """Eq. in Silver et al. (2016) Methods; counts are rollout counts N_r."""
    if edge_rollout_visits < 0 or parent_rollout_visits < 0:
        raise ValueError("visits must be nonnegative")
    return q + c_puct * prior * sqrt(parent_rollout_visits) / (1 + edge_rollout_visits)

def select_most_visited(visits: dict[str, int]) -> str:
    """2016 paper: play root move with most visits (lexical tie break for demo)."""
    if not visits:
        raise ValueError("at least one legal action required")
    return max(sorted(visits), key=lambda action: visits[action])

def backup_alternating_players(path: Sequence[str], value_at_leaf: float) -> dict[str, float]:
    """Return parent-perspective action values for one simulation on a single path."""
    result = {}
    value = value_at_leaf
    for edge in reversed(path):
        value = -value  # each parent is the opponent of its child
        result[edge] = value
    return result

def _self_test() -> None:
    assert mixed_value(0.6, -1.0, 0.5) == -0.2 or abs(mixed_value(0.6, -1.0, 0.5) + 0.2) < 1e-12
    assert mixed_value(0.6, -1.0, 0.0) == 0.6
    assert mixed_value(0.6, -1.0, 1.0) == -1.0
    assert abs(puct_score(0.2, 0.5, 3, 16, 2) - 1.2) < 1e-12
    assert select_most_visited({"A": 13, "B": 24, "C": 2}) == "B"
    assert backup_alternating_players(["root-A", "A-B"], 0.75) == {"A-B": -0.75, "root-A": 0.75}
    print("AlphaGo teaching arithmetic checks passed")

if __name__ == "__main__":
    _self_test()
