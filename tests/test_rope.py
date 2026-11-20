"""Properties verified in the teaching RoPE implementation."""
import importlib.util
import math
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mini_rope", ROOT/"posts/architectures/rope/mini_rope.py")
rope = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rope)

def test_norm_preserved():
    x = (0.2, -0.8, 1.5, 0.4, -1.2, 0.9)
    length = rope.dot(x,x)
    for pos in (0,1,19,4096):
        r = rope.rotate(x,pos)
        assert math.isclose(rope.dot(r,r),length,rel_tol=1e-12,abs_tol=1e-12)

def test_score_depends_on_relative_displacement():
    q = (1.0,2.0,0.5,-0.9)
    k = (-0.3,0.7,1.1,0.2)
    for m,n in ((2,5),(1,3),(128,133)):
        x = rope.score(q,k,m,n)
        for offset in (1,10,1000):
            assert math.isclose(x,rope.score(q,k,m+offset,n+offset),rel_tol=1e-11,abs_tol=1e-11)

def test_zero_distance_equal_original_dot():
    q,k = (1.0,2.0,-0.7,0.4),(0.1,-0.5,0.3,0.9)
    for m in (0,1,100):
        assert rope.score(q,k,m,m)==pytest.approx(rope.dot(q,k),abs=1e-12)

def test_invalid_rotary_dimension_and_position():
    for v in ((),(1.0,),(1.0,2.0,3.0)):
        with pytest.raises(ValueError):
            rope.rotate(v,0)
    with pytest.raises(ValueError):
        rope.rotate((1.,0.),-1)
    with pytest.raises(ValueError):
        rope.rotate((1.,0.),1,base=1.0)

def test_shape_mismatch():
    with pytest.raises(ValueError):
        rope.dot((1.,2.),(1.,))
