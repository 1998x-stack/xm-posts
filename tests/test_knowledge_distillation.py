"""Numerical invariants for the knowledge-distillation teaching example."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts/training/knowledge-distillation"))
from distillation_demo import (  # noqa: E402
    distillation_gradient, distillation_loss, kl_divergence, softmax,
)


def test_temperature_softmax_is_a_probability_distribution():
    logits = [2.2, 1.2, -0.2]
    for temperature in (1.0, 2.0, 4.0):
        probabilities = softmax(logits, temperature)
        assert sum(probabilities) == pytest.approx(1.0)
        assert all(0.0 < value < 1.0 for value in probabilities)
        assert probabilities[0] > probabilities[1] > probabilities[2]


def test_higher_temperature_softens_the_distribution():
    logits = [2.2, 1.2, -0.2]
    cold, warm, hot = (softmax(logits, t) for t in (1.0, 2.0, 4.0))
    assert cold[0] > warm[0] > hot[0]
    assert cold[2] < warm[2] < hot[2]


def test_kl_is_non_negative_and_zero_for_identical_distributions():
    p = softmax([2.2, 1.2, -0.2], 2.0)
    q = softmax([1.7, 1.1, -0.1], 2.0)
    assert kl_divergence(p, p) == pytest.approx(0.0, abs=1e-12)
    assert kl_divergence(p, q) >= 0.0


def test_t_squared_kl_matches_the_documented_toy_example():
    teacher, student = [2.2, 1.2, -0.2], [1.7, 1.1, -0.1]
    assert softmax(teacher, 2.0) == pytest.approx(
        [0.5241846, 0.3179340, 0.1578814], abs=1e-6
    )
    assert distillation_loss(student, teacher, 2.0) == pytest.approx(
        0.0295583, abs=1e-6
    )


def test_analytic_gradient_matches_finite_difference():
    teacher, student, temperature = [2.2, 1.2, -0.2], [1.7, 1.1, -0.1], 2.0
    analytic = distillation_gradient(student, teacher, temperature)
    epsilon, numeric = 1e-6, []
    for index in range(len(student)):
        plus, minus = student.copy(), student.copy()
        plus[index] += epsilon
        minus[index] -= epsilon
        numeric.append(
            (distillation_loss(plus, teacher, temperature)
             - distillation_loss(minus, teacher, temperature)) / (2 * epsilon)
        )
    assert analytic == pytest.approx(numeric, abs=1e-8)


def test_invalid_temperature_and_mismatched_logits_fail_clearly():
    with pytest.raises(ValueError, match="positive"):
        softmax([1.0, 2.0], 0.0)
    with pytest.raises(ValueError, match="same length"):
        distillation_loss([1.0], [1.0, 2.0])
    with pytest.raises(ValueError, match="same length"):
        distillation_gradient([1.0], [1.0, 2.0])
