"""Deterministic checks for the REINFORCE explainer's teaching kernel."""
from pathlib import Path
import importlib.util
import math

P = Path(__file__).with_name("mini_reinforce.py")
spec = importlib.util.spec_from_file_location("mini_reinforce", P)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_reward_to_go_and_empty():
    assert m.reward_to_go([1, 0, 3]) == [4, 3, 3]
    assert m.reward_to_go([]) == []
    assert m.reward_to_go([2, -5, 1]) == [-2, -4, 1]


def test_expected_gradient_independent_of_action_free_baseline():
    p, r1, r0 = .35, 2., 0.
    truth = p * (1. - p) * (r1 - r0)
    for b in (-2, 0, 1, 1.3, 2, 8):
        mean, variance = m.exact_moments(p, r1, r0, b)
        assert math.isclose(mean, truth, abs_tol=1e-12)
        assert variance >= 0.


def test_variance_optimum_not_always_average_reward():
    p, r1, r0 = .35, 2., 0.
    b = m.optimal_scalar_baseline(p, r1, r0)
    assert math.isclose(b, 1.3)
    assert math.isclose(m.exact_moments(p, r1, r0, b)[1], 0., abs_tol=1e-12)
    assert m.exact_moments(p, r1, r0, 0)[1] > 0.3


def test_logit_score_matches_finite_difference():
    theta, eps = -.6, 1e-6
    p = m.sigmoid(theta)
    for a in (0, 1):
        logprob = lambda x: math.log(m.sigmoid(x) if a else 1-m.sigmoid(x))
        numeric = (logprob(theta + eps) - logprob(theta - eps)) / (2*eps)
        assert abs(numeric - m.score(a, p)) < 1e-9


def test_seeded_sampling_near_exact_mean():
    for b in (0., 1.3, 2.):
        assert abs(m.monte_carlo_mean(.35, 2., 0., b) - .455) < .03
