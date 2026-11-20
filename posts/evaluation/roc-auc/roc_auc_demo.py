"""Offline educational ROC-AUC implementation; Python 3.11+, standard library only."""
import math
Y = [1,1,1,1,0,0,0,0]
S = [.95,.78,.55,.40,.83,.48,.32,.12]

def validate(labels,scores):
    if not labels or len(labels)!=len(scores): raise ValueError("Nonempty equal-length labels and scores required")
    if any(type(y) is not int or y not in (0,1) for y in labels): raise ValueError("Binary integer labels required")
    if any(not math.isfinite(float(s)) for s in scores): raise ValueError("Scores must be finite")
    p=sum(labels);n=len(labels)-p
    if not p or not n: raise ValueError("Both classes required")
    return p,n

def roc_points(labels,scores):
    p,n=validate(labels,scores)
    records=sorted(zip(scores,labels),reverse=True)
    tp=fp=k=0;out=[(0.,0.)]
    while k<len(records):
        score=records[k][0]
        while k<len(records) and records[k][0]==score:
            if records[k][1]:tp+=1
            else:fp+=1
            k+=1
        out.append((fp/n,tp/p))
    return out

def trapezoidal_auc(labels,scores):
    pts=roc_points(labels,scores)
    return sum((b[0]-a[0])*(b[1]+a[1])/2 for a,b in zip(pts,pts[1:]))

def pairwise_auc(labels,scores):
    validate(labels,scores)
    p=[s for y,s in zip(labels,scores) if y==1]
    n=[s for y,s in zip(labels,scores) if y==0]
    return sum(1. if x>y else .5 if x==y else 0. for x in p for y in n)/(len(p)*len(n))

def precision_at_prevalence(pi,tpr,fpr):
    if any(not 0<=v<=1 for v in (pi,tpr,fpr)): raise ValueError("Rates out of range")
    den=pi*tpr+(1-pi)*fpr
    if den==0: raise ValueError("Precision undefined if no predicted positives")
    return pi*tpr/den

def self_test():
    assert roc_points(Y,S)[3]==(.25,.5)
    assert roc_points(Y,S)[-1]==(1.,1.)
    assert math.isclose(trapezoidal_auc(Y,S),.75)
    assert math.isclose(pairwise_auc(Y,S),.75)
    assert pairwise_auc([1,0],[.5,.5])==.5
    assert trapezoidal_auc([1,0],[.5,.5])==.5
    assert pairwise_auc([1,0],[1.,0.])==1.
    assert pairwise_auc([1,0],[0.,1.])==0.
    assert math.isclose(pairwise_auc(Y,[x**3 for x in S]),.75)
    assert .47<precision_at_prevalence(.01,.9,.01)<.48
    print("ROC-AUC educational assertions passed")
if __name__=="__main__":self_test()
