import importlib.util
from pathlib import Path
import pytest

file=Path(__file__).resolve().parents[1]/"posts/foundations/importance-sampling/mini_importance_sampling.py"
spec=importlib.util.spec_from_file_location("mini_importance_sampling",file)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_proposal_and_change_of_measure():
    for r in (.01,.05,.20,.50,.80):
        q=m.proposal(r)
        assert sum(q)==pytest.approx(1)
        assert m.weights(m.P,q)[2]==pytest.approx(.01/r)
        for f in ((0,0,1),(2,-1,7),(1,1,1)):
            assert m.exact_expectation(m.P,q,f)==pytest.approx(sum(p*v for p,v in zip(m.P,f)))

def test_variance_analytic():
    a,b=m.event_variances(.01,.2)
    assert a==pytest.approx(.0099)
    assert b==pytest.approx(.0004)
    assert a/b==pytest.approx(24.75)
    assert m.event_variances(.01,.01)[1]==pytest.approx(a)

def test_snis_is_different_from_ordinary():
    q=m.proposal(.2)
    assert m.ordinary([2],m.P,q,(0,0,1))==pytest.approx(.05)
    assert m.snis([2],m.P,q,(0,0,1))==pytest.approx(1)
    with pytest.raises(ZeroDivisionError):
        m.snis([0],(0,1),(.5,.5),(0,1))

def test_invalid_support_and_trajectory():
    with pytest.raises(ValueError,match="support"):
        m.weights((.5,.5),(0,1))
    assert m.trajectory_ratio((.8,.8),(.5,.5))==pytest.approx(2.56)
    with pytest.raises(ValueError):
        m.trajectory_ratio((.8,),(0,))
