"""Small deterministic invariants for the GMM teaching example."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "posts/classical-ml/gmm/demo.py"
spec = importlib.util.spec_from_file_location("gmm_toy", PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_posterior_symmetry():
    row = mod.responsibilities([0.0], [0.5, 0.5], [-1.0, 1.0], [1.0, 1.0])[0]
    assert abs(row[0] - 0.5) < 1e-12
    assert abs(sum(row) - 1.0) < 1e-12


def test_em_demo_monotonic_and_normalized():
    w, m, v, history = mod.run_demo()
    assert len(history) == 26
    assert all(b >= a - 1e-9 for a, b in zip(history, history[1:]))
    assert abs(sum(w) - 1.0) < 1e-12
    assert len(m) == len(v) == 2
    assert min(v) > 0
