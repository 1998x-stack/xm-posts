"""Deterministic educational tests, no model weights or datasets required."""
from pathlib import Path
from math import isclose, log
import importlib.util

PATH=Path(__file__).resolve().parents[1]/"posts/training/dpo/mini_dpo.py"
spec=importlib.util.spec_from_file_location("mini_dpo",PATH)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_initial_policy_equals_reference():
    assert isclose(mod.dpo_loss(-2.0,-3.0,-2.0,-3.0,beta=0.1), log(2),abs_tol=1e-12)

def test_reference_corrected_margin_and_symmetry():
    a=mod.dpo_margin(-2.2,-3.6,-2.8,-3.4)
    assert isclose(a,0.8,abs_tol=1e-12)
    assert mod.dpo_loss(-2.2,-3.6,-2.8,-3.4,beta=0.5) < log(2)
    swapped=mod.dpo_loss(-3.6,-2.2,-3.4,-2.8,beta=0.5)
    assert isclose(swapped,mod.softplus(0.4),abs_tol=1e-12)
    assert swapped > log(2)

def test_gradient_finite_difference():
    args=(-2.2,-3.6,-2.8,-3.4)
    beta=0.5
    h=1e-6
    numeric=(mod.dpo_loss(args[0]+h,*args[1:],beta)-mod.dpo_loss(args[0]-h,*args[1:],beta))/(2*h)
    assert isclose(numeric,mod.chosen_gradient(*args,beta),abs_tol=1e-8)

def test_completion_only_mask_and_invalid_arguments():
    assert isclose(mod.completion_logp([-1.,-.2,-.3,-9.],[False,True,True,False]),-.5,abs_tol=1e-12)
    for vals,m in [([-.1],[]),([-.1],[False])]:
        try:mod.completion_logp(vals,m)
        except ValueError:pass
        else:assert False,"must reject invalid completion masks"
    for beta in [0,-1,float("inf")]:
        try:mod.dpo_loss(-1,-2,-1,-2,beta)
        except ValueError:pass
        else:assert False,"must reject invalid beta"

def test_numerical_stability():
    assert isclose(mod.softplus(-1000.0),0.0,abs_tol=1e-12)
    assert isclose(mod.softplus(1000.0),1000.0,abs_tol=1e-12)
