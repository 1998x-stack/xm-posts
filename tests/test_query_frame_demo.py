from __future__ import annotations

import pytest

from examples.query_frame_demo import parse_query_demo


EXAMPLE = (
    "Find recent papers about efficient LLM inference, "
    "especially methods that reduce KV cache memory."
)


def test_demo_preserves_raw_query_and_extracts_supported_fields():
    frame = parse_query_demo(EXAMPLE)
    assert frame.raw_query == EXAMPLE
    assert frame.intent == "research_search"
    assert frame.entities == ("LLM inference", "KV Cache")
    assert "time:recent" in frame.constraints
    assert "objective:reduce_memory" in frame.constraints


def test_underspecified_time_is_not_silently_guessed():
    frame = parse_query_demo(EXAMPLE)
    assert frame.needs_clarification
    assert any("时间窗口" in item for item in frame.unresolved)


def test_unknown_intent_abstains_instead_of_inventing_entities():
    frame = parse_query_demo("play something nice")
    assert frame.intent == "unknown"
    assert frame.entities == ()
    assert frame.needs_clarification


def test_empty_query_is_rejected():
    with pytest.raises(ValueError):
        parse_query_demo("   ")
