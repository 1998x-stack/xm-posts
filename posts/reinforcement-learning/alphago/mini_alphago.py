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


def two_stream_q(value_sum: float, value_visits: int,
                 rollout_sum: float, rollout_visits: int,
                 lam: float) -> float:
    """APV-MCTS uses separately accumulated value and rollout means."""
    if not 0 <= lam <= 1 or value_visits < 0 or rollout_visits < 0:
        raise ValueError("Invalid lambda or visit count")
    if lam < 1 and value_visits == 0:
        raise ValueError("Missing value sample")
    if lam > 0 and rollout_visits == 0:
        raise ValueError("Missing rollout sample")
    value_mean = value_sum / value_visits if value_visits else 0.0
    rollout_mean = rollout_sum / rollout_visits if rollout_visits else 0.0
    return (1 - lam) * value_mean + lam * rollout_mean


def apply_virtual_loss(visits: int, reward_sum: float,
                       virtual_visits: int) -> tuple[int, float]:
    """Temporarily penalize a path while a search thread is computing."""
    if visits < 0 or virtual_visits < 0:
        raise ValueError("Visit counts must be nonnegative")
    return visits + virtual_visits, reward_sum - virtual_visits


def resolve_virtual_loss(visits: int, reward_sum: float,
                         virtual_visits: int, outcome: float) -> tuple[int, float]:
    """Undo virtual loss, then count one actual rollout outcome."""
    if virtual_visits < 0 or visits < virtual_visits:
        raise ValueError("Invalid pending search state")
    return visits - virtual_visits + 1, reward_sum + virtual_visits + outcome


def sampled_value_state(u: int, total_moves: int) -> int:
    """Select s_(U+1) after the paper's random action, not all game states."""
    if not 1 <= u <= 450 or total_moves <= u:
        raise ValueError("Invalid sampled timestep or unfinished game")
    return u + 1

def _self_test() -> None:
    assert mixed_value(0.6, -1.0, 0.5) == -0.2 or abs(mixed_value(0.6, -1.0, 0.5) + 0.2) < 1e-12
    assert mixed_value(0.6, -1.0, 0.0) == 0.6
    assert mixed_value(0.6, -1.0, 1.0) == -1.0
    assert abs(puct_score(0.2, 0.5, 3, 16, 2) - 1.2) < 1e-12
    assert select_most_visited({"A": 13, "B": 24, "C": 2}) == "B"
    assert backup_alternating_players(["root-A", "A-B"], 0.75) == {"A-B": -0.75, "root-A": 0.75}
    assert abs(two_stream_q(2, 4, 9, 10, .5) - .7) < 1e-12
    pending = apply_virtual_loss(10, 4., 3)
    assert pending == (13, 1.)
    assert resolve_virtual_loss(*pending, 3, 1.) == (11, 5.)
    assert sampled_value_state(100, 200) == 101
    print("AlphaGo teaching arithmetic checks passed")

if __name__ == "__main__":
    _self_test()
