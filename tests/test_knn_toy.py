"""Deterministic tests for the KNN tutorial, no third-party ML dependency."""
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "posts" / "classical-ml" / "knn" / "mini_knn.py"
spec = importlib.util.spec_from_file_location("xm_post_knn", SCRIPT)
knn = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(knn)


def test_article_neighbor_ranking():
    assert [i for i, _ in knn.neighbors(knn.POINTS, knn.QUERY, 3)] == [4, 5, 7]
    assert knn.classify(knn.POINTS, knn.LABELS, knn.QUERY, k=1) == "A"
    assert knn.classify(knn.POINTS, knn.LABELS, knn.QUERY, k=3) == "B"


def test_inverse_distance_and_zero_distance():
    knn.self_test()
    assert knn.classify(((0,), (0,), (4,)), ("A", "B", "B"), (0,), k=3, weights="distance") == "A"


def test_invalid_k():
    import pytest
    with pytest.raises(ValueError):
        knn.neighbors(knn.POINTS, knn.QUERY, 11)
