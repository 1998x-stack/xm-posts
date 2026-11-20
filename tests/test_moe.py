"""Scientific invariants for the minimal MoE router."""
from pathlib import Path
import sys
from math import isclose
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"posts"/"architectures"/"moe"))
from moe_toy import route_topk, combine_scalar, dispatch, cv_squared, importance, self_test


def test_self_test():
    self_test()


@pytest.mark.parametrize("k",[1,2,3,4])
def test_support_normalization(k):
    gate=route_topk([4.,3.,2.,1.],k)
    assert sum(v>0 for v in gate)==k
    assert isclose(sum(gate),1,abs_tol=1e-12)


def test_softmax_shift_invariance():
    a=route_topk([2.,1.,0.],2)
    b=route_topk([100002.,100001.,100000.],2)
    assert a==pytest.approx(b)


def test_tie_determinism():
    assert route_topk([1.,1.,0.],1)==[1.,0.,0.]


def test_mixture_and_importance():
    assert isclose(combine_scalar(3.,[.6,.4],[(2.,1.),(-1.,0.)]), .6*7 + .4*(-3))
    assert importance([[.8,.2],[.8,.2]])==pytest.approx([1.6,.4])
    assert cv_squared([4.,0.,0.,0.])==3.


@pytest.mark.parametrize("k",[1,2,3])
@pytest.mark.parametrize("cf",[.5,1.,1.5,2.])
def test_capacity_conserves_assignments(k,cf):
    r=dispatch([[3.,2.,1.,0.]]*6,k,cf)
    assert sum(r["counts"])+r["overflow"]==r["candidates"]==6*k
    assert all(x<=r["capacity"] for x in r["counts"])


def test_invalid_inputs():
    with pytest.raises(ValueError):
        route_topk([],1)
    with pytest.raises(ValueError):
        route_topk([1.,2.],0)
    with pytest.raises(ValueError):
        route_topk([float("nan"),1.],1)
    with pytest.raises(ValueError):
        dispatch([[1.,2.],[1.]],1)
