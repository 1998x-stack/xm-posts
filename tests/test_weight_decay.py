"""Weight Decay paper explainer: exact, reproducible numerical checks."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "posts/foundations/weight-decay/mini_weight_decay.py"
spec = spec_from_file_location("mini_weight_decay", SOURCE)
m = module_from_spec(spec)
spec.loader.exec_module(m)


def test_standard_sgd_l2_equivalence():
    theta, grad = [2., -1., .3], [.5, -.25, -.2]
    a=m.decayed_sgd(theta,grad,.1,.2)
    b=m.l2_sgd(theta,grad,.1,.2)
    assert all(abs(x-y)<1e-12 for x,y in zip(a,b))


def test_fixed_preconditioning_changes_decay_effect():
    a=m.preconditioned([1.,1.],[0.,0.],.1,.1,[1.,5.],True)
    b=m.preconditioned([1.,1.],[0.,0.],.1,.1,[1.,5.],False)
    assert all(abs(x-y)<1e-12 for x,y in zip(a,[.99,.998]))
    assert all(abs(x-y)<1e-12 for x,y in zip(b,[.99,.99]))


def test_retention_and_demo():
    assert abs(m.retention(.1,.2,50)-.98**50)<1e-14
    assert m.retention(.1,0,1000)==1
    assert m.retention(.1,.2,0)==1
    assert m.demo()[2] == [.99,.99]
