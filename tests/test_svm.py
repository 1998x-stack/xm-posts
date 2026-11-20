"""Assertions for the pedagogical one-dimensional analytic SVM."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from math import isclose
import pytest

file=Path(__file__).resolve().parents[1]/"posts/classical-ml/svm/mini_svm.py"
spec=spec_from_file_location("mini_svm",file)
svm=module_from_spec(spec)
spec.loader.exec_module(svm)

def test_exact_1d_separable_solution():
    model=svm.solve_hard_margin_1d([-2,-1],[1,2])
    assert model["support"]==(-1.0,1.0)
    assert model["alpha"]==(0.5,0.5)
    assert model["w"]==1.0 and model["b"]==0.0
    assert svm.predict(model,0.4)==1 and svm.predict(model,-0.4)==-1

def test_translation_and_scaling():
    m=svm.solve_hard_margin_1d([-4,-2],[2,4])
    assert isclose(m["w"],0.5)
    assert isclose(m["geometric_margin"],2.0)
    shifted=svm.solve_hard_margin_1d([0,1],[3,4])
    assert isclose(shifted["w"],1)
    assert isclose(shifted["b"],-2)

def test_hinge_and_rbf():
    assert svm.hinge(1,1.1)==0
    assert svm.hinge(1,.5)==.5
    assert svm.hinge(-1,.5)==1.5
    assert svm.rbf(3,3,.75)==1
    assert isclose(svm.rbf(-1,2,.5),svm.rbf(2,-1,.5))

def test_reject_nonseparable_or_missing_class():
    with pytest.raises(ValueError):
        svm.solve_hard_margin_1d([-2,1],[0,2])
    with pytest.raises(ValueError):
        svm.solve_hard_margin_1d([], [1])
    with pytest.raises(ValueError):
        svm.rbf(1,2,-1)
