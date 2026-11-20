"""Centered LogSumExp / Softmax Taylor expansions; standard library, teaching use."""
from math import exp, log, isclose, isfinite, sqrt

def center(x):
    if not x or any(not isfinite(float(v)) for v in x):
        raise ValueError("nonempty finite logits required")
    mean = sum(x) / len(x)
    return [v - mean for v in x], mean

def logsumexp(x):
    center(x)
    m = max(x)
    return m + log(sum(exp(v - m) for v in x))

def softmax(x):
    z = logsumexp(x)
    return [exp(v - z) for v in x]

def moments(delta):
    n = len(delta)
    return [sum(v**r for v in delta) / n for r in range(5)]

def lse_series(x, lam=1.0, order=4):
    d, mu = center(x)
    m = moments(d)
    terms = [log(len(x)) + mu, 0.0, lam**2 * m[2]/2,
             lam**3 * m[3]/6, lam**4 * (m[4]-3*m[2]**2)/24]
    # This expansion is for mu*1 + lam*delta; the mean is not scaled.
    return sum(terms[:order+1])

def softmax_series(x, lam=1.0, order=3):
    if not 0 <= order <= 3:
        raise ValueError("order 0..3")
    d, _ = center(x)
    m = moments(d)
    n = len(x)
    return [(1 + (lam*a if order>=1 else 0)
              + (lam**2*(a*a-m[2])/2 if order>=2 else 0)
              + (lam**3*(a**3-3*m[2]*a-m[3])/6 if order>=3 else 0))/n
            for a in d]

def approx_attention(query, keys, values):
    """Single-prefix first-order softmax, 1D query/key, scalar value."""
    if len(keys)!=len(values) or not keys:
        raise ValueError("keys/values mismatch")
    t=len(keys)
    sk=sum(keys); sv=sum(values); skv=sum(k*v for k,v in zip(keys,values))
    return sv/t + query*skv/t - query*sk*sv/(t*t)

if __name__ == "__main__":
    x = [-1.3, -0.3, 0.4, 1.2]
    assert isclose(sum(softmax(x)),1,abs_tol=1e-12)
    assert all(isclose(a,b,abs_tol=1e-12) for a,b in
               zip(softmax(x),softmax([v+1000 for v in x])))
    for order in (0,1,2,3):
        assert isclose(sum(softmax_series(x,.4,order)),1,abs_tol=1e-12)
    for lam in (.2,.1):
        exact=softmax([lam*v for v in x])
        err1=max(abs(a-b) for a,b in zip(exact,softmax_series(x,lam,1)))
        err2=max(abs(a-b) for a,b in zip(exact,softmax_series(x,lam,2)))
        assert err2 < err1
    assert isclose(approx_attention(.2,[.3,-.2],[1.,3.]),
                   sum(a*b for a,b in zip(softmax_series([.06,-.04],1,1),[1.,3.])),
                   abs_tol=1e-12)
    assert isclose(logsumexp([3,3]),3+log(2),abs_tol=1e-12)
    assert isclose(lse_series(x,0,4),log(4),abs_tol=1e-12)
    print("centered Taylor algebra: deterministic assertions passed")
