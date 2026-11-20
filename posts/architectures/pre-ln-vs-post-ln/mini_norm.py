"""Minimal deterministic Pre-LN vs Post-LN experiment; standard library only.

This is NOT a paper benchmark and contains no attention or language model.
"""
from math import sqrt

EPS = 1e-5

def ln(xs, eps=EPS):
    mu = sum(xs) / len(xs)
    var = sum((v-mu)**2 for v in xs) / len(xs)
    return [(v-mu) / sqrt(var + eps) for v in xs]

def branch(xs):
    # Small linear, circularly coupled toy transformation.
    n = len(xs)
    return [0.2*xs[i] + 0.1*xs[(i+1) % n] for i in range(n)]

def pre_ln(xs):
    f = branch(ln(xs))
    return [x + fx for x,fx in zip(xs, f)]

def post_ln(xs):
    f = branch(xs)
    return ln([x + fx for x,fx in zip(xs, f)])

def jacobian(fun, x, h=1e-5):
    cols = []
    for k in range(len(x)):
        plus = x.copy(); minus = x.copy()
        plus[k] += h; minus[k] -= h
        cols.append([(a-b)/(2*h) for a,b in zip(fun(plus), fun(minus))])
    return list(map(list, zip(*cols)))

def check():
    x = [1.0, 2.0, 4.0, 6.0]
    shifted = [v+2.0 for v in x]
    pre0, pre1 = pre_ln(x), pre_ln(shifted)
    post0, post1 = post_ln(x), post_ln(shifted)
    # LN(v + c*1) = LN(v).  Hence Pre-LN preserves the shortcut shift.
    assert all(abs((b-a)-2.0) < 1e-8 for a,b in zip(pre0, pre1))
    # For this affine-free linear branch, Post-LN removes a uniform shift.
    assert all(abs(a-b) < 1e-8 for a,b in zip(post0, post1))
    jpre, jpost = jacobian(pre_ln,x), jacobian(post_ln,x)
    assert all(abs(sum(row)-1.0) < 1e-6 for row in jpre)
    assert all(abs(sum(row)) < 1e-6 for row in jpost)
    print("toy test passed; Pre-LN preserves constant shift, Post-LN removes it")

if __name__ == "__main__":
    check()
