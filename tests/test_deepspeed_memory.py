from __future__ import annotations

import math
import pytest

from posts.training.deepspeed.zero_memory import (
    all_gather,
    model_state_bytes,
    model_state_gb,
    reduce_scatter_sum,
)


def test_7_5b_64gpu_matches_zero_paper_model_state_estimates():
    parameters = 7_500_000_000
    expected_gb = [120.0, 31.40625, 16.640625, 1.875]
    actual = [model_state_gb(parameters, 64, stage) for stage in range(4)]
    for got, want in zip(actual, expected_gb):
        assert math.isclose(got, want, rel_tol=1e-10)


def test_stage_zero_is_replicated_even_when_dp_degree_changes():
    p = 1_000_000
    assert model_state_bytes(p, 1, 0) == model_state_bytes(p, 64, 0)


def test_more_ranks_reduce_stage_three_model_state_per_rank():
    p = 1_000_000
    assert model_state_bytes(p, 8, 3) == 2 * model_state_bytes(p, 16, 3)


def test_stage_progressively_partitions_more_state():
    p, n = 1_000_000, 8
    estimates = [model_state_bytes(p, n, stage) for stage in range(4)]
    assert estimates[0] > estimates[1] > estimates[2] > estimates[3]


def test_reduce_scatter_sums_then_assigns_one_shard_per_rank():
    gradients = [
        [1.0, 2.0, 3.0, 4.0],
        [10.0, 20.0, 30.0, 40.0],
        [100.0, 200.0, 300.0, 400.0],
        [1000.0, 2000.0, 3000.0, 4000.0],
    ]
    assert reduce_scatter_sum(gradients) == [
        [1111.0], [2222.0], [3333.0], [4444.0]
    ]


def test_all_gather_reconstructs_the_reduced_vector():
    shards = [[1111.0], [2222.0], [3333.0], [4444.0]]
    assert all_gather(shards) == [1111.0, 2222.0, 3333.0, 4444.0]


@pytest.mark.parametrize("parameters,degree,stage", [
    (0, 8, 1), (-1, 8, 1), (100, 0, 1), (100, -2, 2), (100, 8, 4)
])
def test_invalid_memory_inputs_are_rejected(parameters, degree, stage):
    with pytest.raises(ValueError):
        model_state_bytes(parameters, degree, stage)


def test_invalid_collective_shapes_are_rejected():
    with pytest.raises(ValueError):
        reduce_scatter_sum([])
    with pytest.raises(ValueError):
        reduce_scatter_sum([[1.0, 2.0], [3.0]])
    with pytest.raises(ValueError):
        all_gather([[1.0], [2.0, 3.0]])
