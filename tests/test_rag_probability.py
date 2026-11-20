"""Regression tests for the pedagogical RAG marginalization examples."""
from importlib.util import module_from_spec, spec_from_file_location
from math import isclose
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "posts" / "retrieval-rag" / "rag" / "toy_probability.py"
SPEC = spec_from_file_location("rag_probabilities", SOURCE)
assert SPEC is not None and SPEC.loader is not None
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_rag_example_weights():
    seq, tok = MODULE.probabilities(0.6)
    assert isclose(seq, 0.226, abs_tol=1e-12)
    assert isclose(tok, 0.310, abs_tol=1e-12)


def test_single_document_equivalence():
    for weight in (0.0, 1.0):
        seq, tok = MODULE.probabilities(weight)
        assert isclose(seq, tok, abs_tol=1e-12)


def test_input_out_of_range():
    import pytest
    for weight in (-0.01, 1.01):
        with pytest.raises(ValueError):
            MODULE.probabilities(weight)
