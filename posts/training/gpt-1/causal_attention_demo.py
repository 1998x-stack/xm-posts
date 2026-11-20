#!/usr/bin/env python3
"""Educational causal attention; not a historical GPT-1 reproduction."""
from math import exp, sqrt, isclose

def softmax(xs):
    assert xs
    z = max(xs)
    es = [exp(x-z) for x in xs]
    return [e/sum(es) for e in es]

def causal_attention(q,k,v):
    """Single head [T,d] Q,K and [T,dv] V -> [T,dv]."""
    n=len(q)
    assert n>0 and len(k)==len(v)==n
    d=len(q[0]); dv=len(v[0])
    assert d>0 and dv>0 and all(len(x)==d for x in q+k)
    assert all(len(x)==dv for x in v)
    out=[]
    for i in range(n):
        logits=[sum(a*b for a,b in zip(q[i],k[j]))/sqrt(d) for j in range(i+1)]
        weights=softmax(logits)
        out.append([sum(weights[j]*v[j][col] for j in range(i+1)) for col in range(dv)])
    return out

def joint_log_likelihood(log_label, lm_log_probs, lam=0.5):
    """Equation 5: maximize log-likelihoods."""
    return log_label+lam*sum(lm_log_probs)

def check():
    q=[[1.,0.],[0.,1.],[1.,1.]]
    k=[[1.,0.],[0.,1.],[1.,1.]]
    v=[[1.],[2.],[3.]]
    baseline=causal_attention(q,k,v)
    perturb=causal_attention(q,[k[0],k[1],[1000.,-1000.]],[v[0],v[1],[999.]])
    assert baseline[:2]==perturb[:2], "future token leaked into history"
    assert not isclose(baseline[-1][0],perturb[-1][0])
    assert isclose(sum(softmax([1.,2.,3.])),1.,abs_tol=1e-12)
    assert isclose(joint_log_likelihood(-2.,[-1.,-3.]),-4.,abs_tol=1e-12)
    print("PASS causal mask, probability, joint objective")
if __name__=="__main__":
    check()
