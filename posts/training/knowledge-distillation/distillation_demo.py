#!/usr/bin/env python3
"""Small, deterministic numerical checks for temperature-based knowledge distillation."""
from __future__ import annotations
from math import exp, log
from typing import Sequence


def _check_temperature(temperature: float) -> None:
    if temperature <= 0:
        raise ValueError("temperature must be positive")


def softmax(logits: Sequence[float], temperature: float = 1.0) -> list[float]:
    """Return a numerically stable temperature-softmax distribution."""
    _check_temperature(temperature)
    if not logits:
        raise ValueError("logits must not be empty")
    scaled = [value / temperature for value in logits]
    peak = max(scaled)
    exps = [exp(value - peak) for value in scaled]
    normalizer = sum(exps)
    return [value / normalizer for value in exps]


def kl_divergence(target: Sequence[float], predicted: Sequence[float]) -> float:
    """Compute D_KL(target || predicted) for two probability vectors."""
    if len(target) != len(predicted) or not target:
        raise ValueError("probability vectors must have the same non-zero length")
    if any(p < 0 for p in target) or any(q <= 0 for q in predicted):
        raise ValueError("target must be non-negative and predicted must be positive")
    return sum(p * log(p / q) for p, q in zip(target, predicted) if p > 0)


def distillation_loss(student_logits: Sequence[float], teacher_logits: Sequence[float], temperature: float = 2.0) -> float:
    """Return T^2 * KL(teacher_T || student_T)."""
    if len(student_logits) != len(teacher_logits):
        raise ValueError("teacher and student logits must have the same length")
    teacher = softmax(teacher_logits, temperature)
    student = softmax(student_logits, temperature)
    return temperature**2 * kl_divergence(teacher, student)


def distillation_gradient(student_logits: Sequence[float], teacher_logits: Sequence[float], temperature: float = 2.0) -> list[float]:
    """Analytic gradient of T^2 * KL(teacher_T || student_T) w.r.t. student logits."""
    if len(student_logits) != len(teacher_logits):
        raise ValueError("teacher and student logits must have the same length")
    teacher = softmax(teacher_logits, temperature)
    student = softmax(student_logits, temperature)
    return [temperature * (s - t) for s, t in zip(student, teacher)]


def main() -> None:
    teacher_logits = [2.2, 1.2, -0.2]
    student_logits = [1.7, 1.1, -0.1]
    temperature = 2.0
    teacher = softmax(teacher_logits, temperature)
    student = softmax(student_logits, temperature)
    loss = distillation_loss(student_logits, teacher_logits, temperature)
    gradient = distillation_gradient(student_logits, teacher_logits, temperature)
    print("teacher_T =", [round(value, 4) for value in teacher])
    print("student_T =", [round(value, 4) for value in student])
    print("T^2 * KL =", round(loss, 6))
    print("dL/d(student_logits) =", [round(value, 6) for value in gradient])


if __name__ == "__main__":
    main()
