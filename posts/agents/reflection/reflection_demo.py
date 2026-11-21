"""Deterministic teaching demo for a bounded reflection loop.

This is a fixed toy policy, not an LLM, not Reflexion's original implementation,
and not a benchmark reproduction. It makes feedback -> memory -> revision
executable without running generated code or calling external tools.
"""
from __future__ import annotations
import math
from typing import Sequence


def run_mean_reflection(values: Sequence[float] = (1.0, 2.0, 3.0), *, max_rounds: int = 3) -> dict:
    """Simulate a failed sum candidate, an actionable critique, and a verified fix."""
    if not values:
        raise ValueError("values must contain at least one number")
    if max_rounds < 1:
        raise ValueError("max_rounds must be >= 1")
    expected = sum(values) / len(values)
    candidate = "sum"
    memory: list[str] = []
    attempts: list[dict] = []
    for round_index in range(max_rounds):
        output = sum(values) if candidate == "sum" else sum(values) / len(values)
        passed = math.isclose(float(output), float(expected), rel_tol=1e-9, abs_tol=1e-9)
        feedback = None if passed else (
            "The candidate computes a sum; divide by the number of elements "
            "to satisfy the mean objective."
        )
        attempts.append({"round":round_index+1,"candidate":candidate,"output":float(output),
                         "expected":float(expected),"passed":passed,"feedback":feedback})
        if passed:
            break
        memory.append(feedback)
        if round_index + 1 < max_rounds and "divide by the number of elements" in feedback:
            candidate = "mean"
    return {"success":bool(attempts and attempts[-1]["passed"]),
            "final_candidate":candidate,"expected":float(expected),
            "attempts":attempts,"memory":memory,"rounds_used":len(attempts)}


if __name__ == "__main__":
    result = run_mean_reflection()
    for attempt in result["attempts"]:
        print(f"round={attempt['round']} candidate={attempt['candidate']} "
              f"output={attempt['output']} passed={attempt['passed']}")
    print("success:", result["success"])
    print("memory:", result["memory"])
