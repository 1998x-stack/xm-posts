"""First-order checkpoint interval model for teaching and deterministic tests.

This module is not a production checkpoint writer. It models the classical
Young-Daly trade-off under a stationary Poisson failure approximation.
For asynchronous systems, callers should pass an empirically measured
exposed/critical-path cost and separately validate persistence completion.
"""
from __future__ import annotations

from math import ceil, isfinite, sqrt


def _positive_finite(name: str, value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a positive finite number")
    number = float(value)
    if not isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return number


def young_daly_interval(checkpoint_cost_s: float, mtbf_s: float) -> float:
    """Return the first-order optimum interval in seconds: sqrt(2*C*M)."""
    cost = _positive_finite("checkpoint_cost_s", checkpoint_cost_s)
    mtbf = _positive_finite("mtbf_s", mtbf_s)
    return sqrt(2.0 * cost * mtbf)


def expected_overhead_fraction(
    checkpoint_cost_s: float, interval_s: float, mtbf_s: float
) -> float:
    """Approximate overhead C/tau + tau/(2*M), as a fraction of runtime."""
    cost = _positive_finite("checkpoint_cost_s", checkpoint_cost_s)
    interval = _positive_finite("interval_s", interval_s)
    mtbf = _positive_finite("mtbf_s", mtbf_s)
    return cost / interval + interval / (2.0 * mtbf)


def expected_lost_work_s(interval_s: float) -> float:
    """Expected lost compute after a failure, assuming a uniform failure point."""
    interval = _positive_finite("interval_s", interval_s)
    return interval / 2.0


def storage_write_time_s(checkpoint_size_gb: float, bandwidth_gb_s: float) -> float:
    """Ideal lower bound for writing decimal GB at decimal GB/s."""
    size = _positive_finite("checkpoint_size_gb", checkpoint_size_gb)
    bandwidth = _positive_finite("bandwidth_gb_s", bandwidth_gb_s)
    return size / bandwidth


def interval_iterations(interval_s: float, step_time_s: float) -> int:
    """Convert a time interval into a whole number of training iterations."""
    interval = _positive_finite("interval_s", interval_s)
    step_time = _positive_finite("step_time_s", step_time_s)
    return max(1, ceil(interval / step_time))
