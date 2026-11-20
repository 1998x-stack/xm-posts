"""Deterministic regression tests for the article's toy memory model."""
from memory_demo import Fact, reconcile


def test_new_evidence_updates_memory():
    original = Fact("api_path", "/v1", 1, "old-note")
    result = reconcile(original, [Fact("api_path", "/v2", 5, "trusted-log")])
    assert result.value == "/v2" and result.source == "trusted-log"


def test_unrelated_event_cannot_change_note():
    original = Fact("api_path", "/v1", 2, "old-note")
    assert reconcile(original, [Fact("other_key", "data", 9, "log")]) == original


def test_older_evidence_cannot_overwrite_fresh_note():
    original = Fact("api_path", "/v2", 9, "verified")
    assert reconcile(original, [Fact("api_path", "/v1", 4, "stale")]) == original


def test_empty_event_log_preserves_existing_note():
    original = Fact("api_path", "/v2", 9, "verified")
    assert reconcile(original, []) == original
