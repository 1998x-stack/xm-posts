"""Decision Tree teaching-kernel regression tests."""
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from math import isclose
import pytest
file=Path(__file__).resolve().parents[1]/"posts/classical-ml/decision-tree/mini_decision_tree.py"
spec=spec_from_file_location("mini_decision_tree",file)
tree=module_from_spec(spec)
spec.loader.exec_module(tree)

def test_impurities():
    assert tree.gini([0,0])==0
    assert tree.entropy([0,0,0])==0
    assert tree.gini([0,1])==0.5
    assert tree.entropy([0,1])==1.0
    assert isclose(tree.gini([0,1,2]),2/3)

def test_manual_split():
    split=tree.best_gini_split(tree.X,tree.Y)
    assert (split["threshold"],split["left_size"],split["right_size"])==(4.5,4,4)
    assert isclose(split["parent_gini"],0.46875)
    assert isclose(split["weighted_gini"],0.1875)
    assert isclose(split["gain"],0.28125)

def test_order_invariance():
    assert tree.best_gini_split(list(reversed(tree.X)),list(reversed(tree.Y)))["threshold"]==4.5
    assert tree.midpoints([1,1,3,3])==[2]

def test_regression_and_pruning():
    model=tree.best_sse_split([1,2,3,4],[2,2,8,8])
    assert model["threshold"]==2.5 and model["sse"]==0
    assert model["parent_sse"]==36 and model["left_mean"]==2 and model["right_mean"]==8
    a=0.28125
    assert isclose(tree.complexity_cost(.1875,2,a),tree.complexity_cost(.46875,1,a))

def test_errors():
    with pytest.raises(ValueError): tree.gini([])
    with pytest.raises(ValueError): tree.entropy([])
    with pytest.raises(ValueError): tree.best_gini_split([1,2],[0])
    with pytest.raises(ValueError): tree.best_gini_split([1,1],[0,1])
    with pytest.raises(ValueError): tree.best_sse_split([1,2],[1,float("nan")])
    with pytest.raises(ValueError): tree.complexity_cost(.2,2,-.1)

def test_smoke():
    tree.smoke_test()

def test_article_chromium(tmp_path):
    """Real Chromium checks MathML geometry, four responsive sizes, print, offline JS and interaction."""
    import subprocess
    import sys
    root=Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable,
         str(root/"skills/olah-style-paper-posts/scripts/browser_check.py"),
         str(root/"posts/classical-ml/decision-tree/index.html"),
         "--output", str(tmp_path/"decision-tree-browser")],
        check=True,
        cwd=root,
    )
