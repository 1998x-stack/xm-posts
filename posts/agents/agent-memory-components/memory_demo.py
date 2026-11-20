"""A deterministic teaching model of checking persisted notes against dated events.

Not an implementation of Anthropic dreaming or any production memory system.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Fact:
    key: str
    value: str
    observed_at: int
    source: str


def reconcile(note: Fact, events: Iterable[Fact]) -> Fact:
    """Select the most recent verified direct observation for the same key.

    Inputs must already be trusted and authorized by the caller. Ties favour the
    existing note rather than introducing unstable ordering.
    """
    result = note
    for event in events:
        if event.key == note.key and event.observed_at > result.observed_at:
            result = event
    return result


if __name__ == "__main__":
    old = Fact("api_path", "/v1", 1, "old-note")
    log = [Fact("api_path", "/v2", 4, "verified-tool-log")]
    current = reconcile(old, log)
    assert current.value == "/v2"
    assert current.source == "verified-tool-log"
    print(current)
