"""Importance Sampling: deterministic analytic examples, Python standard library only."""
from math import isfinite

P = (0.90, 0.09, 0.01)

def proposal(r):
    if not (0 < r < 1):
        raise ValueError("q(A) must be strictly between 0 and 1")
    return ((1-r)*P[0]/0.99, (1-r)*P[1]/0.99, r)

def weights(p, q):
    if len(p) != len(q) or not p:
        raise ValueError("p/q length mismatch")
    if any(not isfinite(x) or x < 0 for x in (*p,*q)):
        raise ValueError("invalid probability")
    if abs(sum(p)-1)>1e-10 or abs(sum(q)-1)>1e-10:
        raise ValueError("probabilities must sum to 1")
    if any(a>0 and b==0 for a,b in zip(p,q)):
        raise ValueError("q lacks target support")
    return [a/b if b else 0 for a,b in zip(p,q)]

def ordinary(samples, p, q, f):
    if not samples or len(f)!=len(p):
        raise ValueError("missing samples/values")
    w=weights(p,q)
    return sum(w[k]*f[k] for k in samples)/len(samples)

def snis(samples, p, q, f):
    if not samples or len(f)!=len(p):
        raise ValueError("missing samples/values")
    w=weights(p,q)
    denom=sum(w[k] for k in samples)
    if denom==0: raise ZeroDivisionError("zero total weight")
    return sum(w[k]*f[k] for k in samples)/denom

def exact_expectation(p,q,f):
    w=weights(p,q)
    return sum(q[i]*w[i]*f[i] for i in range(len(p)))

def event_variances(p_event,q_event):
    if not(0<p_event<1 and 0<q_event<1):
        raise ValueError("require nontrivial event probabilities")
    return p_event*(1-p_event), p_event**2*(1/q_event-1)

def trajectory_ratio(pi,beta):
    if len(pi)!=len(beta): raise ValueError("mismatched trajectory")
    ratio=1.0
    for p,b in zip(pi,beta):
        if not(0<=p<=1 and 0<b<=1):
            raise ValueError("behavior must cover target")
        ratio*=p/b
    return ratio

if __name__=="__main__":
    q=proposal(.2)
    assert abs(sum(q)-1)<1e-12
    assert abs(exact_expectation(P,q,(0,0,1))-.01)<1e-12
    a,b=event_variances(.01,.2)
    assert abs(a/b-24.75)<1e-10
    assert abs(trajectory_ratio((.8,.8),(.5,.5))-2.56)<1e-12
    print("importance sampling analytic checks: passed")
