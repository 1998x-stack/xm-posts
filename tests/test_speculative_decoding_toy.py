"""Deterministic unit checks for the speculative decoding teaching model."""
import importlib.util
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "posts/inference/speculative-decoding/toy_sampler.py"
spec = importlib.util.spec_from_file_location("speculative_toy", SOURCE)
model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model)


@pytest.mark.parametrize("p,q", [
    ((.3, .4, .3), (.6, .3, .1)),
    ((.5, .5), (.5, .5)),
    ((0, 1), (1, 0)),
    ((.1, .2, .7), (.7, .2, .1)),
])
def test_exact_output_distribution(p, q):
    assert model.exact_marginal(p, q) == pytest.approx(p, abs=1e-12)


def test_error_cases():
    with pytest.raises(ValueError):
        model.exact_marginal((.3, .3), (.5, .5))
    with pytest.raises(ValueError):
        model.exact_marginal((.5, .5), (1,))
    with pytest.raises(ValueError):
        model.expected_tokens(1.1, 3)
    with pytest.raises(ValueError):
        model.expected_tokens(.4, 0)


def test_expected_tokens_and_idealized_speedup():
    assert model.expected_tokens(0, 3) == 1
    assert model.expected_tokens(1, 3) == 4
    assert model.expected_tokens(.75, 3) == pytest.approx(2.734375)
    assert model.idealized_speedup(.75, 3, .05) == pytest.approx(2.3777173913)
