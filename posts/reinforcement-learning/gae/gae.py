"""GAE numerical kernel: Schulman et al., ICLR 2016, Eq. (10) and (16).
Pure Python, not a reproduction of the robotics benchmarks.
"""
from math import isclose, isfinite

def gae(rewards, values, terminals, gamma=0.99, lam=0.95):
    """T rewards and true-terminal flags; T+1 values incl. truncation bootstrap.
    A time-limit truncation is NOT a true terminal; keep its bootstrap value.
    """
    n = len(rewards)
    if len(values) != n + 1 or len(terminals) != n:
        raise ValueError("expected T rewards/terminals and T+1 values")
    if not (0 <= gamma <= 1 and 0 <= lam <= 1):
        raise ValueError("gamma and lam must be in [0, 1]")
    if not all(isfinite(float(x)) for x in list(rewards) + list(values)):
        raise ValueError("non-finite reward or value")
    result = [0.] * n
    running = 0.
    for t in range(n - 1, -1, -1):
        alive = 0. if terminals[t] else 1.
        delta = rewards[t] + gamma * alive * values[t + 1] - values[t]
        running = delta + gamma * lam * alive * running
        result[t] = running
    return result

def self_test():
    r, v, end = [1., 0., 2., 1.], [1.2, 1., .9, .5, 0.], [False, False, False, True]
    residual = [.7, -.19, 1.55, .5]
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(gae(r, v, end, .9, 0), residual))
    assert isclose(gae(r, v, end, .9, .95)[0], 1.9831519375, abs_tol=1e-10)
    assert isclose(gae(r, v, end, .9, 1)[0], 2.149, abs_tol=1e-10)
    assert gae([1.], [0., 100.], [True], .9, 1) == [1.]
    assert isclose(gae([1.], [0., 100.], [False], .9, 1)[0], 91.)
    assert gae([1., 2.], [0., 0., 0.], [True, True], 1, 1) == [1., 2.]
    try:
        gae([1.], [0.], [True])
    except ValueError:
        pass
    else:
        raise AssertionError("length guard missing")
    print("GAE endpoint, recursion, termination and truncation checks passed")

if __name__ == "__main__":
    self_test()
