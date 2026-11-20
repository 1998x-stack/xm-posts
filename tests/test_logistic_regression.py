"""Check the independent logistic-regression teaching kernel."""
import importlib.util
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "posts" / "classical-ml" / "logistic-regression" / "logistic_regression_demo.py"
spec = importlib.util.spec_from_file_location("logistic_demo", SRC)
demo = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(demo)

def test_logistic_kernel():
    demo.self_test()

def test_probability_symmetry_and_monotonicity():
    for z in (-10.0, -2.0, 0.0, 2.0, 10.0):
        assert abs(demo.sigmoid(z) + demo.sigmoid(-z) - 1.0) < 1e-12
    assert demo.sigmoid(-2.0) < demo.sigmoid(0.0) < demo.sigmoid(2.0)

def test_regularized_training_reduces_objective():
    w,b = demo.train()
    assert demo.objective(w,b) < demo.objective(0.0,0.0)
    assert abs(demo.gradients(w,b)[0]) < 1e-6
