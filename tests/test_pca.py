from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
from math import isclose
import pytest

src=Path(__file__).resolve().parents[1]/"posts/classical-ml/pca/mini_pca.py"
spec=spec_from_file_location("mini_pca",src)
m=module_from_spec(spec);spec.loader.exec_module(m)
DATA=[(-2,0),(0,-1),(0,1),(2,0)]

def test_toy_covariance_and_energy():
    model=m.fit_pca_2d(DATA)
    assert model["mean"]==(0,0)
    assert model["covariance"]==((8/3,0),(0,2/3))
    assert isclose(model["explained_variance_ratio"],.8)
    scores=m.transform(DATA,model)
    assert scores==[-2,0,0,2]
    reconstructed=m.inverse_transform(scores,model)
    assert reconstructed==[(-2,0),(0,0),(0,0),(2,0)]
    assert isclose(sum(x*x+y*y for x,y in DATA),sum(v*v for v in scores)+sum((x-a)**2+(y-b)**2 for (x,y),(a,b) in zip(DATA,reconstructed)))

def test_rotation_translation_invariance():
    rotated=[(x+y+3,y-x-7) for x,y in DATA]
    model=m.fit_pca_2d(rotated)
    assert isclose(model["explained_variance_ratio"],.8)
    wx,wy=model["component"]
    assert isclose(wx*wx+wy*wy,1)
    assert wx>=0

@pytest.mark.parametrize("points",[[],[(1,2)],[(1,1),(1,1)],[(1,2,3),(2,4,6)],[(float("nan"),1),(2,3)]])
def test_invalid(points):
    with pytest.raises(ValueError):m.fit_pca_2d(points)
