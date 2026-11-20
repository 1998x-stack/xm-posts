"""Deterministic minimal computations for the Weight Decay explainer.

No dependencies, optimizer state, autograd or full AdamW implementation.
"""
from __future__ import annotations


def decayed_sgd(theta, grad, lr, decay):
    """Standard SGD with direct weight shrinkage."""
    assert len(theta) == len(grad)
    assert 0 <= lr * decay < 1
    return [(1 - lr * decay) * w - lr * g for w, g in zip(theta, grad)]


def l2_sgd(theta, grad, lr, penalty):
    """Standard SGD on f + penalty/2 * squared Euclidean norm."""
    assert len(theta) == len(grad)
    return [w - lr * (g + penalty * w) for w, g in zip(theta, grad)]


def preconditioned(theta, grad, lr, decay, inverse_scales, coupled):
    """Educational fixed diagonal P=diag(1/inverse_scales), not Adam."""
    assert len(theta) == len(grad) == len(inverse_scales)
    assert all(s > 0 for s in inverse_scales)
    if coupled:
        return [w - lr * (g + decay * w) / s for w, g, s
                in zip(theta, grad, inverse_scales)]
    return [(1 - lr * decay) * w - lr * g / s for w, g, s
            in zip(theta, grad, inverse_scales)]


def retention(lr, decay, steps):
    assert 0 <= lr * decay < 1 and isinstance(steps, int) and steps >= 0
    return (1 - lr * decay) ** steps


def demo():
    a = decayed_sgd([2., -1.], [.5, -.25], .1, .2)
    b = l2_sgd([2., -1.], [.5, -.25], .1, .2)
    assert all(abs(x - y) < 1e-12 for x, y in zip(a, b))
    coupled = preconditioned([1., 1.], [0., 0.], .1, .1, [1., 5.], True)
    decoupled = preconditioned([1., 1.], [0., 0.], .1, .1, [1., 5.], False)
    assert all(abs(x-y) < 1e-12 for x,y in zip(coupled,[.99,.998]))
    assert all(abs(x-y) < 1e-12 for x,y in zip(decoupled,[.99,.99]))
    assert abs(retention(.1,.2,50)-.98**50)<1e-14
    return a, coupled, decoupled


if __name__ == "__main__":
    print(demo())
