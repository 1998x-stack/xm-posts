"""Small, dependency-free metrics for repeated Agent evaluation runs.

Each row in runs represents one task; each value is one repeated attempt.
The task ordering must remain stable across attempts.
"""
from __future__ import annotations

from collections.abc import Sequence


def summarize_runs(runs: Sequence[Sequence[bool]]) -> dict[str, float | int]:
    """Return Pass@1, Pass@k, Pass^k and pooled attempt success.

    Pass@1 is the first attempt's task success rate.
    Pass@k is the fraction of tasks with at least one successful attempt.
    Pass^k is the fraction of tasks with every attempt successful.
    mean_attempt_success pools all task-attempt outcomes.

    This helper assumes each task has the same number of attempts. It does
    not assume independence and computes empirical rates directly.
    """
    if not runs:
        raise ValueError("runs must contain at least one task")

    normalized: list[list[bool]] = []
    attempts_per_task = len(runs[0])
    if attempts_per_task == 0:
        raise ValueError("each task must contain at least one attempt")

    for task_index, row in enumerate(runs):
        if len(row) != attempts_per_task:
            raise ValueError(
                f"task {task_index} has {len(row)} attempts; "
                f"expected {attempts_per_task}"
            )
        if any(type(value) is not bool for value in row):
            raise TypeError(f"task {task_index} must contain only bool values")
        normalized.append(list(row))

    task_count = len(normalized)
    total_successes = sum(sum(row) for row in normalized)
    pass_at_1 = sum(row[0] for row in normalized) / task_count
    pass_at_k = sum(any(row) for row in normalized) / task_count
    pass_all_k = sum(all(row) for row in normalized) / task_count
    mean_attempt_success = total_successes / (task_count * attempts_per_task)

    return {
        "task_count": task_count,
        "attempts_per_task": attempts_per_task,
        "pass_at_1": pass_at_1,
        "pass_at_k": pass_at_k,
        "pass_all_k": pass_all_k,
        "mean_attempt_success": mean_attempt_success,
    }


if __name__ == "__main__":
    import json

    example = [
        [True, True, False, True, True],
        [True, False, False, False, True],
        [False, False, False, False, False],
    ]
    print(json.dumps(summarize_runs(example), indent=2))
