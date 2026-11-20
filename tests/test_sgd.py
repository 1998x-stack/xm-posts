"""Regression tests for standalone SGD study code (no external arrays)."""
from pathlib import Path
import importlib.util
import itertools
import math
import pytest

P = Path(__file__).resolve().parents[1] / "posts/foundations/sgd/mini_sgd.py"
spec = importlib.util.spec_from_file_location("mini_sgd", P)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def test_batch_average_and_exact_step():
    theta = [2.0, -1.0]
    grads = [[1.0, -3.0], [3.0, 1.0]]
    before = [g[:] for g in grads]
    assert module.mean_gradient(grads) == [2.0, -1.0]
    assert module.sgd_step(theta, grads, 0.1) == pytest.approx([1.8, -0.9])
    assert theta == [2.0, -1.0] and grads == before


def test_unbiased_uniform_one_sample_gradient():
    g = [3.0, -1.0, -3.0, -7.0]
    # All four equally likely outcomes at fixed theta=0.
    expected = sum(g) / len(g)
    assert expected == -2.0
    assert module.mean_gradient([[x] for x in g]) == [expected]
    assert module.sgd_step([0.0], [[g[0]]], 0.1)[0] == pytest.approx(-0.3)
    assert module.sgd_step([0.0], [[x] for x in g], 0.1)[0] == pytest.approx(0.2)


def test_minibatch_two_samples_expectation_equals_full_gradient():
    grad = [3.0, -1.0, -3.0, -7.0]
    # Enumerate all 2-sample combinations drawn without replacement at
    # fixed theta. Each pair is equally likely by this toy sampling scheme.
    means = [(grad[i] + grad[j]) / 2 for i, j in itertools.combinations(range(4), 2)]
    assert sum(means) / len(means) == pytest.approx(sum(grad) / 4)


def test_full_batch_quadratic_converges_under_small_step():
    a = [-3.0, 1.0, 3.0, 7.0]  # optimizer theta*=mean(a)=2
    theta = [0.0]
    for _ in range(100):
        grads = [[theta[0] - target] for target in a]
        theta = module.sgd_step(theta, grads, 0.1)
    assert theta[0] == pytest.approx(2.0, abs=1e-4)


def test_harmonic_step_schedule():
    vals = [module.decaying_step_size(i, numerator=1.0, offset=1.0) for i in range(5)]
    assert vals == pytest.approx([1.0, 0.5, 1.0/3.0, 0.25, 0.2])
    assert all(x > y for x, y in zip(vals, vals[1:]))
    with pytest.raises(ValueError):
        module.decaying_step_size(-1)


def test_momentum_is_stateful_and_not_plain_sgd():
    opt = module.MomentumSGD(dimensions=1, momentum=0.5)
    first = opt.step([0.0], [[2.0]], 0.1)
    second = opt.step(first, [[0.0]], 0.1)
    assert first == pytest.approx([-0.2])
    assert second == pytest.approx([-0.3])
    assert module.sgd_step(first, [[0.0]], 0.1) == pytest.approx(first)


def test_invalid_shapes_and_values():
    with pytest.raises(ValueError):
        module.sgd_step([1.0], [[1.0, 2.0]], 0.1)
    with pytest.raises(ValueError):
        module.sgd_step([1.0], [], 0.1)
    with pytest.raises(ValueError):
        module.sgd_step([1.0], [[1.0]], float("nan"))
    with pytest.raises(ValueError):
        module.mean_gradient([[math.nan]])
    with pytest.raises(ValueError):
        module.MomentumSGD(1, momentum=1)
