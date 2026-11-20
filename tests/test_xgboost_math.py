"""XGBoost tutorial math invariants with no third-party runtime dependency."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "posts/classical-ml/xgboost/mini_xgboost.py"
spec = importlib.util.spec_from_file_location("mini_xgboost", PATH)
xgb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xgb)

def test_leaf_and_gain():
    assert abs(xgb.leaf_weight(1, 2) + 1/3) < 1e-12
    assert abs(xgb.split_gain(1, 2, -1, 2) - (1/3-.1)) < 1e-12

def test_exact_split():
    cut, gain = xgb.scan_splits([1,2,3,4], [.5,.5,-.5,-.5], [1,1,1,1])
    assert cut == 2.5
    assert abs(gain - (1/3-.1)) < 1e-12

def test_missing_default_and_pruning():
    values = xgb.missing_default_gains((.5,1),(-.5,1),(.5,1))
    assert values["left"] != values["right"]
    assert xgb.split_gain(1,2,-1,2,gamma=.5) < 0
