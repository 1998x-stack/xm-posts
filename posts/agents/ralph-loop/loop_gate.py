"""A tiny, deterministic completion gate for a Ralph-style outer loop."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Verification:
    completion_promise: bool
    tests_pass: bool
    blockers: int = 0
    regressions: int = 0


def decide(check: Verification, iteration: int, max_iterations: int) -> str:
    """Return complete, continue, or budget_exhausted.

    A model's completion promise is necessary but never sufficient:
    objective checks, blockers, and regressions are evaluated separately.
    """
    if iteration < 1 or max_iterations < 1:
        raise ValueError("iteration and max_iterations must be positive")
    if check.blockers < 0 or check.regressions < 0:
        raise ValueError("blockers and regressions cannot be negative")

    if (
        check.completion_promise
        and check.tests_pass
        and check.blockers == 0
        and check.regressions == 0
    ):
        return "complete"

    if iteration >= max_iterations:
        return "budget_exhausted"

    return "continue"
