"""Deterministic regression tests for the K-Means educational example."""
from pathlib import Path
import importlib.util

SRC = Path(__file__).resolve().parents[1] / "posts/classical-ml/k-means/kmeans_demo.py"
spec = importlib.util.spec_from_file_location("educational_kmeans", SRC)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_k_means_four_points():
    centers, labels, history = module.run()
    assert centers == (1.0, 9.0)
    assert labels == (0, 0, 1, 1)
    assert module.inertia(module.POINTS, centers, labels) == 4.0
    assert len(history) >= 3
    for before, after, _, _ in history:
        assert after <= before + 1e-12


def test_k_means_empty_cluster_teaching_policy():
    points = (0., 0., 10.)
    centers = (0., 10., 20.)
    labels = module.assign(points, centers)
    assert module.update(points, centers, labels) == (0., 10., 20.)
