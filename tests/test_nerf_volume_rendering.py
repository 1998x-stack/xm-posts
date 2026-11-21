"""Deterministic checks for the NeRF teaching compositor."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts" / "architectures" / "nerf"))

from volume_rendering import render_ray  # noqa: E402


def test_zero_density_returns_background():
    background = (0.2, 0.4, 0.8)
    rgb, weights, residual = render_ray(
        [(0.0, (1.0, 0.0, 0.0), 0.5)],
        background=background,
    )
    assert rgb == background
    assert weights == [0.0]
    assert residual == 1.0


def test_front_sample_occludes_farther_samples():
    rgb, weights, residual = render_ray(
        [
            (1000.0, (1.0, 0.0, 0.0), 1.0),
            (1000.0, (0.0, 0.0, 1.0), 1.0),
        ],
        background=(0.0, 1.0, 0.0),
    )
    assert rgb == (1.0, 0.0, 0.0)
    assert weights == [1.0, 0.0]
    assert residual == 0.0


def test_weights_and_residual_conserve_probability_mass():
    samples = [
        (0.15, (0.90, 0.30, 0.20), 0.25),
        (0.35, (0.95, 0.65, 0.25), 0.25),
        (1.20, (0.20, 0.65, 0.85), 0.25),
        (0.50, (0.25, 0.55, 0.80), 0.25),
        (0.12, (0.80, 0.30, 0.60), 0.25),
    ]
    rgb, weights, residual = render_ray(samples)
    assert len(weights) == len(samples)
    assert all(0.0 <= weight <= 1.0 for weight in weights)
    assert 0.0 <= residual <= 1.0
    assert sum(weights) + residual == pytest.approx(1.0, abs=1e-12)
    assert all(0.0 <= channel <= 1.0 for channel in rgb)


@pytest.mark.parametrize("sigma,delta", [(-0.1, 0.2), (0.1, -0.2)])
def test_negative_density_or_interval_is_rejected(sigma, delta):
    with pytest.raises(ValueError):
        render_ray([(sigma, (0.2, 0.3, 0.4), delta)])


def test_invalid_rgb_is_rejected():
    with pytest.raises(ValueError):
        render_ray([(0.2, (1.2, 0.0, 0.0), 0.3)])
