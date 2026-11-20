"""A tiny, dependency-free front-to-back NeRF volume compositor.

Each sample is (density sigma, RGB color, interval length delta).
This is a teaching implementation of the discrete alpha-compositing rule,
not a reproduction of the full NeRF training pipeline.
"""
from __future__ import annotations

from math import expm1, isfinite
from typing import Sequence

Color = tuple[float, float, float]
Sample = tuple[float, Color, float]


def _validate_color(color: Color, label: str) -> None:
    if len(color) != 3 or not all(isfinite(channel) for channel in color):
        raise ValueError(f"{label} must contain three finite RGB values")
    if any(channel < 0.0 or channel > 1.0 for channel in color):
        raise ValueError(f"{label} channels must be in [0, 1]")


def render_ray(
    samples: Sequence[Sample],
    background: Color = (1.0, 1.0, 1.0),
) -> tuple[Color, list[float], float]:
    """Composite ordered ray samples and return (RGB, weights, residual T).

    The caller must order samples from near to far. Density and interval
    length must be non-negative. expm1 is used for numerical stability
    when opacity is small.
    """
    _validate_color(background, "background")

    accumulated = [0.0, 0.0, 0.0]
    transmittance = 1.0
    weights: list[float] = []

    for index, (sigma, color, delta) in enumerate(samples):
        if not isfinite(sigma) or not isfinite(delta):
            raise ValueError(f"sample {index}: sigma and delta must be finite")
        if sigma < 0.0 or delta < 0.0:
            raise ValueError(f"sample {index}: sigma and delta must be non-negative")
        _validate_color(color, f"sample {index} color")

        alpha = -expm1(-sigma * delta)
        weight = transmittance * alpha
        weights.append(weight)

        for channel in range(3):
            accumulated[channel] += weight * color[channel]

        transmittance *= 1.0 - alpha

    rgb = tuple(
        accumulated[channel] + transmittance * background[channel]
        for channel in range(3)
    )
    return rgb, weights, transmittance  # type: ignore[return-value]


if __name__ == "__main__":
    demo_samples: list[Sample] = [
        (0.15, (0.90, 0.30, 0.20), 0.25),
        (0.35, (0.95, 0.65, 0.25), 0.25),
        (1.20, (0.20, 0.65, 0.85), 0.25),
        (0.50, (0.25, 0.55, 0.80), 0.25),
        (0.12, (0.80, 0.30, 0.60), 0.25),
    ]
    rgb, weights, residual = render_ray(demo_samples)
    print("rendered RGB:", tuple(round(value, 4) for value in rgb))
    print("sample weights:", [round(value, 4) for value in weights])
    print("remaining transmittance:", round(residual, 4))
    assert abs(sum(weights) + residual - 1.0) < 1e-12
