"""Deterministic checks for the GAN three-category teaching model."""
import importlib.util
from math import log
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "posts/architectures/gan/demo.py"
spec = importlib.util.spec_from_file_location("gan_demo", path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_theoretical_best_response():
    best = m.optimal_discriminator(m.REAL, m.generated(0))
    assert all(abs(a-b) < 1e-12 for a,b in zip(best, (.8,.6,2/15)))
    assert m.optimal_discriminator(m.REAL, m.generated(1)) == (.5,.5,.5)


def test_distribution_and_jsd_identity():
    for t in (0,.2,.5,.8,1):
        q = m.generated(t)
        assert abs(sum(q)-1) < 1e-12
        assert all(v > 0 for v in q)
        assert abs(m.game_value(m.REAL,q) - (-log(4)+2*m.jsd(m.REAL,q))) < 1e-12
    assert abs(m.jsd(m.REAL,m.REAL)) < 1e-12
    assert abs(m.game_value(m.REAL,m.REAL)+log(4)) < 1e-12
