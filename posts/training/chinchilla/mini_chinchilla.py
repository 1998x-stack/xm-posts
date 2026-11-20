#!/usr/bin/env python3
"""Deterministic toy Chinchilla budget and loss-law algebra (Python stdlib).

This is not a reproduction of Hoffmann et al. (2022)'s model training
or fitted empirical constants; FLOPs=6*N*D is a planning approximation.
"""
from math import isclose, isfinite

def tokens_for_budget(compute_flops: float, parameters: float) -> float:
    if not (isfinite(compute_flops) and isfinite(parameters)):
        raise ValueError("finite inputs required")
    if compute_flops <= 0 or parameters <= 0:
        raise ValueError("inputs must be positive")
    return compute_flops / (6 * parameters)

def optimum_for_toy_loss(compute_flops: float, *, A: float=1.0, B: float=1.0,
                         alpha: float=0.5, beta: float=0.5) -> tuple[float,float]:
    """Analytic minimizer of E+A*N^-alpha+B*D^-beta with D=C/(6*N)."""
    if not all(isfinite(x) and x > 0 for x in (compute_flops,A,B,alpha,beta)):
        raise ValueError("positive finite coefficients and budget required")
    n = ((alpha*A)/(beta*B) * (compute_flops/6)**beta)**(1/(alpha+beta))
    return n, tokens_for_budget(compute_flops,n)

def predicted_toy_loss(n: float,d:float,*,E:float=1,A:float=1,B:float=1,
                       alpha:float=0.5,beta:float=0.5)->float:
    if min(n,d,A,B,alpha,beta)<=0:
        raise ValueError("positive inputs required")
    return E + A/n**alpha + B/d**beta

if __name__=="__main__":
    c=6*70e9*1.4e12
    assert isclose(tokens_for_budget(c,70e9),1.4e12)
    assert isclose(tokens_for_budget(c,140e9),0.7e12)
    assert isclose(tokens_for_budget(c,280e9),0.35e12)
    assert isclose((tokens_for_budget(c,140e9)/140e9),5.0)
    budget=6*100*100
    n,d=optimum_for_toy_loss(budget)
    assert isclose(n,100) and isclose(d,100)
    optimum=predicted_toy_loss(n,d)
    assert optimum < predicted_toy_loss(50,tokens_for_budget(budget,50))
    assert optimum < predicted_toy_loss(200,tokens_for_budget(budget,200))
    for k in (2,4,16):
        n2,d2=optimum_for_toy_loss(budget*k)
        assert isclose(n2/n,k**0.5)
        assert isclose(d2/d,k**0.5)
    print("Toy compute-optimal scaling checks passed (not paper reproduction).")
