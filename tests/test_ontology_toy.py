from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts" / "knowledge-representation" / "ontology"))
from ontology_toy import EXAMPLE_TRIPLES, infer


def test_subclass_chain_and_domain_range_inference():
    result = infer(EXAMPLE_TRIPLES)
    assert ("alice", "rdf:type", "Student") in result
    assert ("alice", "rdf:type", "Person") in result
    assert ("CS101", "rdf:type", "Course") in result


def test_inference_preserves_every_explicit_fact():
    explicit = set(EXAMPLE_TRIPLES)
    assert explicit <= infer(EXAMPLE_TRIPLES)


def test_closure_is_idempotent():
    once = infer(EXAMPLE_TRIPLES)
    twice = infer(once)
    assert once == twice
