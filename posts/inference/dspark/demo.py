"""DSpark teaching math; no model or hardware benchmark. Python 3.11+."""
from math import isclose, prod

def acceptance(p,q):
    assert len(p)==len(q) and p
    assert all(x>=0 for x in p+q)
    assert isclose(sum(p),1) and isclose(sum(q),1)
    return sum(min(x,y) for x,y in zip(p,q))

def residual(p,q):
    acceptance(p,q)
    d=[max(0,x-y) for x,y in zip(p,q)]
    z=sum(d)
    return [x/z for x in d] if z else None

def survival(c):
    assert all(0<=x<=1 for x in c)
    return [prod(c[:i+1]) for i in range(len(c))]

def schedule(confidences,cost):
    """Fixed realized confidence toy; first non-improvement, not a sampler proof."""
    assert confidences and cost>=0
    R=len(confidences)
    rows=sorted(((a,r,j) for r,c in enumerate(confidences)
                 for j,a in enumerate(survival(c),1) if a>0),
                key=lambda t:(-t[0],t[2],t[1]))
    lengths=[0]*R
    total=R
    best=1000*R
    for K,(a,r,j) in enumerate(rows,1):
        score=(total+a)*1000/(1+cost*K)
        if score<=best+1e-9:
            break
        assert lengths[r]+1==j
        lengths[r]=j
        total+=a
        best=score
    return lengths,best

def self_test():
    p,q=[.7,.3],[.5,.5]
    a=acceptance(p,q)
    assert isclose(a,.8) and isclose(a,1-.5*sum(abs(x-y) for x,y in zip(p,q)))
    assert all(isclose(min(x,y)+(1-a)*z,x) for x,y,z in zip(p,q,residual(p,q)))
    assert residual(p,p) is None
    assert all(isclose(x,y) for x,y in zip(survival([.9,.8,.6,.4]),[.9,.72,.432,.1728]))
    assert isclose(.5+.5*.7,.85) and not isclose(.85,.7)
    c=[[.9,.8,.6],[.8,.5,.3]]
    lengths,tps=schedule(c,.2)
    assert lengths==[2,1] and isclose(tps,2762.5)
    assert schedule(c,0)[0]==[3,3]
    assert schedule(c,.8)[0]==[0,0]
    assert schedule([[1,1],[1,1]],0)[0]==[2,2]

if __name__=="__main__":
    self_test()
    print("DSpark teaching assertions passed")
