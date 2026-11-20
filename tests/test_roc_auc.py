"""ROC-AUC deterministic assertions for both independent computation paths."""
import importlib.util
from pathlib import Path
import math
import pytest
src=Path(__file__).resolve().parents[1]/"posts"/"evaluation"/"roc-auc"/"roc_auc_demo.py"
spec=importlib.util.spec_from_file_location("roc_auc_demo",src)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
def test_main_toy():
    m.self_test()
    assert math.isclose(m.pairwise_auc(m.Y,m.S),m.trapezoidal_auc(m.Y,m.S))
def test_ties_grouped_and_half_credit():
    y=[1,0,1,0];s=[.9,.9,.2,.2]
    assert m.roc_points(y,s)==[(0.,0.),(.5,.5),(1.,1.)]
    assert m.pairwise_auc(y,s)==.5
    assert m.trapezoidal_auc(y,s)==.5
def test_invalid_data():
    with pytest.raises(ValueError):m.pairwise_auc([1,1],[.1,.8])
    with pytest.raises(ValueError):m.roc_points([1,0],[.2,float("nan")])
    with pytest.raises(ValueError):m.roc_points([1,0],[.2])
