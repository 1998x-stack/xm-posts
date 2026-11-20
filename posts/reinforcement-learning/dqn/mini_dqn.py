"""DQN target and Huber checks; standard library, no Atari training."""
from math import isclose

def td_target(reward, gamma, terminal, next_q_values):
    if not 0 <= gamma <= 1 or not next_q_values:
        raise ValueError("invalid gamma or next action space")
    return reward if terminal else reward + gamma * max(next_q_values)

def huber(td_error, threshold=1.0):
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    a = abs(td_error)
    return 0.5 * a * a if a <= threshold else threshold * (a - 0.5 * threshold)

def valid_conv(n, kernel, stride):
    if n < kernel or kernel < 1 or stride < 1:
        raise ValueError("invalid convolution parameters")
    return (n - kernel) // stride + 1

def check():
    assert isclose(td_target(1, 0.99, False, [1.2, 2.0]), 2.98)
    assert isclose(td_target(1, 0.99, True, [1.2, 2.0]), 1)
    assert isclose(huber(1.58), 1.08)
    assert isclose(huber(0.5), 0.125)
    assert [valid_conv(84, 8, 4), valid_conv(20, 4, 2),
            valid_conv(9, 3, 1)] == [20, 9, 7]
    print("DQN math invariants passed")

if __name__ == "__main__":
    check()
