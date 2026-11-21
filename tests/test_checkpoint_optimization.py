"""Deterministic checks for the checkpoint optimization teaching model."""
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose, sqrt
from pathlib import Path

import pytest

PATH = (
    Path(__file__).resolve().parents[1]
    / "posts/training/checkpoint-optimization/mini_checkpoint_optimization.py"
)
SPEC = spec_from_file_location("mini_checkpoint_optimization", PATH)
MODULE = module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_young_daly_interval_and_minimum():
    cost, mtbf = 30.0, 10.0 * 3600.0
    optimum = MODULE.young_daly_interval(cost, mtbf)
    assert isclose(optimum, sqrt(2.0 * cost * mtbf))
    at_optimum = MODULE.expected_overhead_fraction(cost, optimum, mtbf)
    left = MODULE.expected_overhead_fraction(cost, optimum * 0.8, mtbf)
    right = MODULE.expected_overhead_fraction(cost, optimum * 1.2, mtbf)
    assert at_optimum < left
    assert at_optimum < right


def test_optimum_scaling():
    base = MODULE.young_daly_interval(30.0, 36000.0)
    assert isclose(MODULE.young_daly_interval(60.0, 36000.0) / base, sqrt(2.0))
    assert isclose(MODULE.young_daly_interval(30.0, 72000.0) / base, sqrt(2.0))


def test_expected_lost_work():
    assert isclose(MODULE.expected_lost_work_s(1800.0), 900.0)


def test_storage_write_lower_bound():
    assert isclose(MODULE.storage_write_time_s(1000.0, 20.0), 50.0)


def test_interval_to_iterations_rounds_up():
    assert MODULE.interval_iterations(101.0, 10.0) == 11
    assert MODULE.interval_iterations(1.0, 10.0) == 1


@pytest.mark.parametrize(
    "function,args",
    [
        (MODULE.young_daly_interval, (0, 100)),
        (MODULE.young_daly_interval, (10, float("inf"))),
        (MODULE.expected_overhead_fraction, (1, 0, 100)),
        (MODULE.expected_lost_work_s, (-1,)),
        (MODULE.storage_write_time_s, (10, 0)),
        (MODULE.interval_iterations, (10, float("nan"))),
        (MODULE.expected_lost_work_s, (True,)),
    ],
)
def test_rejects_invalid_inputs(function, args):
    with pytest.raises(ValueError):
        function(*args)
