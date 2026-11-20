"""Exact algebra checks for the LogSumExp & Softmax Taylor teaching post."""
from pathlib import Path
import importlib.util, math
SRC=Path(__file__).resolve().parents[1]/"posts/foundations/logsumexp-softmax-taylor/mini_softmax_taylor.py"
spec=importlib.util.spec_from_file_location("softmax_taylor_demo",SRC)
demo=importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)
def test_shift_and_stability():
    x=[-1.3,-.3,.4,1.2]
    assert math.isclose(demo.logsumexp([1000,1000]),1000+math.log(2),abs_tol=1e-12)
    assert all(math.isclose(a,b,abs_tol=1e-12) for a,b in zip(demo.softmax(x),demo.softmax([v+1000 for v in x])))
def test_probability_sum_by_order():
    for order in range(4):
        for lam in (0,.2,1.4,3):
            assert math.isclose(sum(demo.softmax_series([-1.3,-.3,.4,1.2],lam,order)),1,abs_tol=1e-12)
def test_order_of_small_error():
    x=[-1.3,-.3,.4,1.2]
    for lam in (.1,.2):
        exact=demo.softmax([lam*v for v in x])
        errs=[max(abs(a-b) for a,b in zip(exact,demo.softmax_series(x,lam,j))) for j in (1,2,3)]
        assert errs[1]<errs[0]
        assert errs[2]<errs[1]
def test_attention_first_order():
    keys=[.3,-.2,.8];values=[1.,3.,2.];query=.1
    t=len(keys);scores=[query*k for k in keys]
    expected=sum(p*v for p,v in zip(demo.softmax_series(scores,1,1),values))
    assert math.isclose(demo.approx_attention(query,keys,values),expected,abs_tol=1e-12)
def test_bad_input():
    import pytest
    with pytest.raises(ValueError): demo.logsumexp([])
    with pytest.raises(ValueError): demo.softmax_series([1,2],order=8)
