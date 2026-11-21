"""Small, dependency-free teaching model for ZeRO state sharding.

This is an accounting/collective simulation, not a DeepSpeed implementation.
It excludes activations, temporary buffers, fragmentation, allocator overhead,
communication buckets, and hardware-specific padding.
"""
from __future__ import annotations


def model_state_bytes(parameter_count: int, dp_degree: int, stage: int) -> float:
    """Estimate per-rank model-state bytes for mixed-precision Adam.

    Assumptions from the original ZeRO paper:
      parameters: FP16 (2 bytes / parameter)
      gradients: FP16 (2 bytes / parameter)
      FP32 master parameters: 4 bytes / parameter
      Adam first and second moments: 4 + 4 bytes / parameter

    Stage 0: ordinary data parallelism, all states replicated.
    Stage 1: optimizer states partitioned.
    Stage 2: optimizer states and gradients partitioned.
    Stage 3: optimizer states, gradients, and parameters partitioned.
    """
    if isinstance(parameter_count, bool) or not isinstance(parameter_count, int):
        raise TypeError("parameter_count must be an integer")
    if isinstance(dp_degree, bool) or not isinstance(dp_degree, int):
        raise TypeError("dp_degree must be an integer")
    if parameter_count <= 0:
        raise ValueError("parameter_count must be positive")
    if dp_degree <= 0:
        raise ValueError("dp_degree must be positive")
    if stage not in (0, 1, 2, 3):
        raise ValueError("stage must be one of 0, 1, 2, 3")

    p = float(parameter_count)
    n = float(dp_degree)
    if stage == 0:
        return 16.0 * p
    if stage == 1:
        return 4.0 * p + 12.0 * p / n
    if stage == 2:
        return 2.0 * p + 14.0 * p / n
    return 16.0 * p / n


def model_state_gb(parameter_count: int, dp_degree: int, stage: int) -> float:
    """Return decimal GB per rank (1 GB = 1,000,000,000 bytes)."""
    return model_state_bytes(parameter_count, dp_degree, stage) / 1_000_000_000


def reduce_scatter_sum(rank_gradients: list[list[float]]) -> list[list[float]]:
    """Toy Reduce-Scatter: sum rank gradients, then give each rank one shard.

    This mirrors the mathematical data movement only; it does not perform
    network communication, autograd, or an optimizer update.
    """
    if not rank_gradients:
        raise ValueError("at least one rank is required")
    width = len(rank_gradients[0])
    if width == 0 or width % len(rank_gradients) != 0:
        raise ValueError("gradient width must be positive and divisible by world size")
    if any(len(row) != width for row in rank_gradients):
        raise ValueError("all ranks must provide gradients with equal width")

    reduced = [
        sum(rank_gradients[rank][column] for rank in range(len(rank_gradients)))
        for column in range(width)
    ]
    shard_width = width // len(rank_gradients)
    return [
        reduced[i * shard_width:(i + 1) * shard_width]
        for i in range(len(rank_gradients))
    ]


def all_gather(shards: list[list[float]]) -> list[float]:
    """Toy All-Gather: concatenate equally sized rank-owned shards."""
    if not shards:
        raise ValueError("at least one shard is required")
    width = len(shards[0])
    if width == 0 or any(len(shard) != width for shard in shards):
        raise ValueError("all shards must have the same positive width")
    return [value for shard in shards for value in shard]


if __name__ == "__main__":
    parameters = 7_500_000_000
    print("7.5B parameters, 64-way data parallelism (decimal GB per GPU)")
    for stage in range(4):
        print("ZeRO stage {}: {:.3f} GB".format(
            stage, model_state_gb(parameters, 64, stage)
        ))

    grads = [
        [1.0, 2.0, 3.0, 4.0],
        [10.0, 20.0, 30.0, 40.0],
        [100.0, 200.0, 300.0, 400.0],
        [1000.0, 2000.0, 3000.0, 4000.0],
    ]
    shards = reduce_scatter_sum(grads)
    print("Reduce-Scatter shards:", shards)
    print("All-Gather:", all_gather(shards))
