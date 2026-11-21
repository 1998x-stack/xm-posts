"""Deterministic token-budget teaching model, not Sarathi-Serve reproduction."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Batch:
    decode_tokens: int
    prefill_chunk: int
    remaining_prefill: int
    budget: int

    def __post_init__(self):
        assert 0 <= self.decode_tokens <= self.budget
        assert 0 <= self.prefill_chunk
        assert self.decode_tokens + self.prefill_chunk <= self.budget
        assert self.remaining_prefill >= 0


def plan_step(decode_count: int, remaining: int, budget: int) -> Batch:
    """Reserve decode slots first; fill remaining slots from one prefill."""
    if decode_count < 0 or remaining < 0 or budget <= 0:
        raise ValueError("negative work or non-positive budget")
    if decode_count > budget:
        raise ValueError("budget cannot fit ongoing decodes")
    chunk = min(remaining, budget - decode_count)
    return Batch(decode_count, chunk, remaining - chunk, budget)


def schedule_prefill(decode_count: int, prompt_length: int, budget: int):
    """Yield one batch per iteration until prompt prefill finishes."""
    remaining = prompt_length
    if decode_count >= budget and remaining > 0:
        raise ValueError("no prefill progress possible")
    while remaining:
        batch = plan_step(decode_count, remaining, budget)
        remaining = batch.remaining_prefill
        yield batch


if __name__ == "__main__":
    for step, batch in enumerate(schedule_prefill(2, 13, 8), 1):
        print(step, batch)
