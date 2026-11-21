"""A deterministic iteration-level serving scheduler, not an Orca GPU reproduction."""
from dataclasses import dataclass


@dataclass
class Request:
    name: str
    arrival: int
    target: int
    generated: int = 0

    def __post_init__(self):
        if self.arrival < 0 or self.target <= 0:
            raise ValueError("arrival must be nonnegative and target must be positive")


def schedule(requests):
    """Yield (iteration, active request names, newly finished names)."""
    if len({r.name for r in requests}) != len(requests):
        raise ValueError("request names must be unique")
    t = 0
    while any(r.generated < r.target for r in requests):
        active = [r for r in requests if r.arrival <= t and r.generated < r.target]
        for req in active:
            req.generated += 1
        yield t, [r.name for r in active], [r.name for r in active if r.generated == r.target]
        t += 1


if __name__ == "__main__":
    demo = [Request("A", 0, 2), Request("B", 0, 4), Request("C", 2, 2)]
    for step in schedule(demo):
        print(step)
