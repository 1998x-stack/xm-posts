"""Independent deterministic checks for the GNN teaching page."""
import importlib.util
from math import isclose
from pathlib import Path

FILE = Path(__file__).resolve().parents[1] / "posts" / "architectures" / "gnn" / "mini_gnn.py"
spec = importlib.util.spec_from_file_location("mini_gnn", FILE)
gnn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gnn)


def test_hand_calculated_layers():
    data = gnn.demo()
    assert isclose(data["mean_1"][1], 14 / 3, abs_tol=1e-12)
    assert isclose(data["mean_2"][1], 41 / 9, abs_tol=1e-12)


def test_gcns_symmetric_normalization_differs_from_row_mean():
    data = gnn.demo()
    assert isclose(data["gcn_1"][1], 4.816496580927726, abs_tol=1e-12)
    assert not isclose(data["gcn_1"][1], data["mean_1"][1], abs_tol=1e-12)


def test_permutation_equivariance():
    order = (2, 0, 3, 1)
    inverse = {old: new for new, old in enumerate(order)}
    values = [gnn.INPUT[old] for old in order]
    edges = tuple((inverse[a], inverse[b]) for a, b in gnn.EDGES)
    for method in (gnn.mean_with_self, gnn.symmetric_gcn):
        expected = method(gnn.INPUT, gnn.EDGES)
        observed = method(values, edges)
        assert all(isclose(observed[inverse[old]], expected[old], abs_tol=1e-12)
                   for old in range(4))


def test_invalid_self_loop_is_explicit():
    try:
        gnn.mean_with_self([1, 2], ((0, 0),))
    except ValueError:
        pass
    else:
        raise AssertionError("unexpected duplicate self-loop")
