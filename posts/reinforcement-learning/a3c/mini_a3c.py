"""Deterministic A3C mathematical core, not an asynchronous trainer.

Original formulation: Mnih et al., ICML 2016, §4 and Supplementary Algorithm S2.
Only Python standard library is required. In a real worker, gradient updates
and the shared RMSProp accumulator require concurrency-aware implementation.
"""
from __future__ import annotations
import math


def n_step_returns(rewards, bootstrap, gamma=0.99, terminated=False):
    """Return targets for each position of one rollout.

    If terminated, the *final* transition reaches a true terminal state.
    Otherwise the rollout is truncated and must bootstrap from V(s_end).
    An episode boundary must never occur inside this input rollout.
    """
    if not (0.0 <= gamma <= 1.0):
        raise ValueError("gamma must be in [0, 1]")
    if not rewards:
        raise ValueError("rollout cannot be empty")
    if not all(math.isfinite(x) for x in [*rewards, bootstrap]):
        raise ValueError("rewards and bootstrap must be finite")
    target = 0.0 if terminated else float(bootstrap)
    result = [0.0] * len(rewards)
    for i in range(len(rewards) - 1, -1, -1):
        target = rewards[i] + gamma * target
        result[i] = target
    return result


def advantage(returns, predicted_values):
    """Actor sample weights: n-step return minus a value baseline."""
    if len(returns) != len(predicted_values):
        raise ValueError("length mismatch")
    return [r - v for r, v in zip(returns, predicted_values)]


def softmax(logits):
    if not logits or not all(math.isfinite(x) for x in logits):
        raise ValueError("logits must be finite and nonempty")
    shift = max(logits)
    z = [math.exp(x - shift) for x in logits]
    total = sum(z)
    return [x / total for x in z]


def entropy(logits):
    """Entropy of a categorical actor, in natural units."""
    p = softmax(logits)
    return -sum(x * math.log(x) for x in p if x > 0.0)


def policy_logprob_gradient(logits, chosen_action, sample_advantage):
    """Exact gradient in logit space of A * log pi(a|s).

    The advantage is treated as a detached sample weight. This is NOT a
    gradient with respect to neural-network parameters.
    """
    p = softmax(logits)
    if not 0 <= chosen_action < len(p):
        raise ValueError("action index out of range")
    return [sample_advantage * ((1.0 if i == chosen_action else 0.0) - q)
            for i, q in enumerate(p)]


def rmsprop_coordinate(param, gradient, moment, eta=0.01, alpha=0.99, eps=1e-8):
    """One coordinate of non-centred RMSProp (ICML 2016 Eq. 1)."""
    if not (0 <= alpha < 1 and eta > 0 and eps > 0):
        raise ValueError("invalid RMSProp hyperparameters")
    next_moment = alpha * moment + (1 - alpha) * gradient ** 2
    next_param = param - eta * gradient / math.sqrt(next_moment + eps)
    return next_param, next_moment


def check():
    close = lambda a, b: math.isclose(a, b, rel_tol=0, abs_tol=1e-10)
    assert all(map(lambda z: close(*z), zip(
        n_step_returns([1.0, 0.5], 2.0, gamma=0.9), [3.07, 2.3])))
    assert all(map(lambda z: close(*z), zip(
        n_step_returns([1.0, 0.5], 999, gamma=0.9, terminated=True), [1.45, 0.5])))
    assert advantage([3.07], [1.2]) == [1.8699999999999999] or close(
        advantage([3.07], [1.2])[0], 1.87)
    assert close(sum(policy_logprob_gradient([0.0, 0.0], 0, 2.0)), 0)
    assert policy_logprob_gradient([0.0, 0.0], 0, 2.0) == [1.0, -1.0]
    assert policy_logprob_gradient([0.0, 0.0], 0, -2.0) == [-1.0, 1.0]
    assert close(entropy([0.0, 0.0]), math.log(2))
    assert entropy([9.0, -9.0]) < entropy([0.0, 0.0])
    par, mom = rmsprop_coordinate(1.0, 2.0, 0.0, eta=0.1, alpha=0.5)
    assert close(mom, 2.0)
    assert close(par, 1.0 - 0.2 / math.sqrt(2.0 + 1e-8))
    print("A3C return / advantage / policy / entropy / RMSProp invariants passed")


if __name__ == "__main__":
    check()
