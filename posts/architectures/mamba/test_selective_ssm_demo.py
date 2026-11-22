"""Tiny CPU tests of equations, not empirical paper reproduction."""
import math
import pytest
from selective_ssm_demo import gated_step, affine_combine, scan_sequential, scan_from_prefix

def test_gate_extremes():
    assert gated_step(3.0, 7.0, 0.0) == 3.0
    assert gated_step(3.0, 7.0, 1.0) == 7.0
    assert gated_step(3.0, 7.0, 0.25) == 4.0
    with pytest.raises(ValueError):
        gated_step(0.0, 1.0, 1.1)

def test_affine_associativity_and_prefix():
    xs=[(0.8,1.2),(0.4,-2),(0.95,0),(0.3,5)]
    left=affine_combine(affine_combine(xs[0],xs[1]),xs[2])
    right=affine_combine(xs[0],affine_combine(xs[1],xs[2]))
    assert all(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12) for a,b in zip(left,right))
    assert scan_sequential(xs,0.8)==pytest.approx(scan_from_prefix(xs,0.8))
