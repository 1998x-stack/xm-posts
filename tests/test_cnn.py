"""CNN deterministic minimal numerical contract."""
from pathlib import Path
import runpy
def load():
    return runpy.run_path(str(Path(__file__).resolve().parents[1]/"posts"/"architectures"/"cnn"/"mini_cnn.py"))
def test_forward_backward():
    load()["self_test"]()
def test_shape_cases():
    f=load()["output_length"]
    assert f(7,3,stride=2,pad=1)==4
    assert f(7,3,dilation=2)==3
