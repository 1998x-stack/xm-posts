"""Deterministic educational RNN tests."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from math import isfinite

path = Path(__file__).resolve().parents[1] / "posts/architectures/rnn/mini_rnn.py"
spec = spec_from_file_location("mini_rnn", path)
mini = module_from_spec(spec)
spec.loader.exec_module(mini)


def test_bptt_matches_finite_difference():
    _, gradient = mini.loss_and_grad()
    numerical = mini.finite_difference()
    assert all(abs(a - b) < 1e-6 for a, b in zip(gradient, numerical))


def test_loss_valid_and_recurrent_signal_nonzero():
    loss, gradient = mini.loss_and_grad()
    assert loss >= 0 and isfinite(loss)
    assert len(gradient) == 3 and all(isfinite(x) for x in gradient)
    assert abs(gradient[1]) > 1e-5


def test_reject_inconsistent_or_empty_sequence():
    for x, y in [((), ()), ((1.0,), ())]:
        try:
            mini.loss_and_grad(x=x, target=y)
        except ValueError:
            pass
        else:
            raise AssertionError("Should reject inconsistent sequence lengths")
