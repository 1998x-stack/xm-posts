"""Tiny PPO objective/GAE mathematical checks. Standard library only."""
from math import isclose

def clipped_objective(ratio, advantage, eps=0.2):
    if ratio <= 0 or not (0 < eps < 1):
        raise ValueError("ratio must be positive; epsilon must be in (0,1)")
    clipped = max(1 - eps, min(1 + eps, ratio))
    return min(ratio * advantage, clipped * advantage)

def gae(rewards, values, terminals, gamma=0.99, lam=0.95):
    """values includes bootstrap V(s_T); terminal[t] marks a real episode end."""
    if len(values) != len(rewards) + 1 or len(terminals) != len(rewards):
        raise ValueError("length mismatch")
    result = [0.0] * len(rewards)
    running = 0.0
    for t in range(len(rewards) - 1, -1, -1):
        alive = 0.0 if terminals[t] else 1.0
        delta = rewards[t] + gamma * alive * values[t+1] - values[t]
        running = delta + gamma * lam * alive * running
        result[t] = running
    return result

def check():
    assert isclose(clipped_objective(1.5, 2), 2.4)
    assert isclose(clipped_objective(0.5, -2), -1.6)
    assert isclose(clipped_objective(1.5, -2), -3.0)
    assert isclose(clipped_objective(0.5, 2), 1.0)
    assert gae([1.0], [0, 100], [True]) == [1.0]
    assert gae([1.0, 2.0], [0, 0, 0], [False, True], 1, 1) == [3, 2]
    print("PPO surrogate and GAE invariants passed")

if __name__ == "__main__":
    check()
