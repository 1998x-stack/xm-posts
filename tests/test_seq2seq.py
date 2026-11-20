"""Regression tests for the seq2seq teaching calculations."""
from __future__ import annotations
import importlib.util
from math import isclose, log
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "posts" / "architectures" / "seq2seq" / "mini_seq2seq.py"
spec = importlib.util.spec_from_file_location("mini_seq2seq", SRC)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_teacher_forcing_shift_and_eos():
    assert m.shifted_targets(["one", "two"]) == (
        ["BOS", "one", "two"], ["one", "two", "EOS"])


def test_padding_mask_is_excluded_from_nll():
    out = m.masked_nll([0.5, 0.25, 0.0], [True, True, False])
    assert isclose(out, -(log(0.5) + log(0.25)) / 2)
    assert isclose(-2 * out, log(0.5 * 0.25))


def test_attention_weights_and_context():
    w = m.masked_softmax([0.0, 1.0, 1000.0], [True, True, False])
    assert isclose(sum(w), 1.0)
    assert w[2] == 0.0
    c = m.weighted_context([0.25, 0.75], [[1.0, 0.0], [0.0, 2.0]])
    assert c == [0.25, 1.5]


def test_beam_can_differ_from_greedy():
    assert m.greedy_decode(m.toy_probs) == ("BOS", "A", "C", "EOS")
    assert m.beam_search(m.toy_probs, width=2) == ("BOS", "B", "EOS")
