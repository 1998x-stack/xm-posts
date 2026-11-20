#!/usr/bin/env python3
"""Tiny single-channel valid cross-correlation, not a reproduction of LeNet-5."""
def output_length(n,k,stride=1,pad=0,dilation=1):
    if min(n,k,stride,dilation)<=0 or pad<0: raise ValueError("invalid size")
    q=n+2*pad-dilation*(k-1)-1
    if q<0: raise ValueError("kernel too large")
    return q//stride+1

def correlate_valid(x,w):
    if not x or not x[0] or not w or not w[0]: raise ValueError("empty")
    h=len(x);width=len(x[0]);kh=len(w);kw=len(w[0])
    if kh>h or kw>width or any(len(a)!=width for a in x) or any(len(a)!=kw for a in w):
        raise ValueError("invalid dimensions")
    return [[sum(x[i+u][j+v]*w[u][v] for u in range(kh) for v in range(kw))
             for j in range(width-kw+1)] for i in range(h-kh+1)]

def kernel_gradient(x,grad,kh,kw):
    ho=len(x)-kh+1;wo=len(x[0])-kw+1
    if ho<=0 or wo<=0 or len(grad)!=ho or any(len(a)!=wo for a in grad):
        raise ValueError("upstream gradient shape mismatch")
    return [[sum(grad[i][j]*x[i+u][j+v] for i in range(ho) for j in range(wo))
             for v in range(kw)] for u in range(kh)]

def self_test():
    x=[[1,0,2,0,1],[0,1,2,1,0],[2,1,0,1,2],[0,2,1,0,1],[1,0,1,2,0]]
    w=[[1,0,-1] for _ in range(3)]
    y=correlate_valid(x,w)
    assert len(y)==3 and all(len(a)==3 for a in y) and y[0][:2]==[-1,0]
    assert output_length(32,5)==28 and output_length(28,2,2)==14
    shapes=[32,output_length(32,5),14,output_length(14,5),5,output_length(5,5)]
    assert shapes==[32,28,14,10,5,1]
    analytic=kernel_gradient(x,[[1]*3 for _ in range(3)],3,3)
    eps=1e-6
    for u in range(3):
        for v in range(3):
            plus=[a[:] for a in w];minus=[a[:] for a in w]
            plus[u][v]+=eps;minus[u][v]-=eps
            numeric=(sum(map(sum,correlate_valid(x,plus)))-sum(map(sum,correlate_valid(x,minus))))/(2*eps)
            assert abs(numeric-analytic[u][v])<1e-7,(u,v,numeric,analytic[u][v])
    print("CNN shape, forward and finite-difference gradient assertions passed")

if __name__=="__main__":self_test()
