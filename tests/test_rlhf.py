import importlib.util
from pathlib import Path
import math

MODULE = Path(__file__).resolve().parents[1] / "posts/training/rlhf/mini_rlhf.py"
spec = importlib.util.spec_from_file_location("mini_rlhf", MODULE)
toy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(toy)

def test_rlhf_math_examples():
    toy.run_checks()
    assert toy.preference_probability(1, 1) == 0.5
    assert math.isclose(toy.pairwise_loss(2, 1), toy.pairwise_loss(12, 11))
    assert toy.discrete_kl([0.5, 0.5], [0.5, 0.5]) == 0
