"""Small deterministic logistic-regression teaching kernel (stdlib only).

Objective: mean Bernoulli negative log-likelihood + lambda/2 * w**2;
intercept is deliberately not regularized. This is NOT a paper reproduction.
"""
from __future__ import annotations
from math import exp, log1p, isfinite

X = (-2.0, -1.0, 1.0, 2.0)
Y = (0.0, 0.0, 1.0, 1.0)

def sigmoid(z: float) -> float:
    if z >= 0:
        return 1.0 / (1.0 + exp(-z))
    ez = exp(z)
    return ez / (1.0 + ez)

def softplus(z: float) -> float:
    return max(z, 0.0) + log1p(exp(-abs(z)))

def binary_loss_from_logit(z: float, y: float) -> float:
    if y not in (0.0, 1.0):
        raise ValueError("binary label required")
    return softplus(z) - y * z

def objective(w: float, b: float, lam: float = 0.1) -> float:
    return (sum(binary_loss_from_logit(w*x+b,y) for x,y in zip(X,Y))/len(X)
            + 0.5*lam*w*w)

def gradients(w: float, b: float, lam: float = 0.1) -> tuple[float,float]:
    errors = [sigmoid(w*x+b)-y for x,y in zip(X,Y)]
    return (sum(e*x for e,x in zip(errors,X))/len(X) + lam*w,
            sum(errors)/len(X))

def train(steps: int = 250, lr: float = 0.4, lam: float = 0.1) -> tuple[float,float]:
    w=b=0.0
    for _ in range(steps):
        dw,db=gradients(w,b,lam)
        w-=lr*dw
        b-=lr*db
    return w,b

def self_test() -> None:
    assert sigmoid(0.0)==0.5
    assert sigmoid(1000.0)==1.0 and sigmoid(-1000.0)==0.0
    assert abs(binary_loss_from_logit(0.0,1.0)-0.6931471805599453)<1e-12
    assert isfinite(binary_loss_from_logit(1000.0,0.0))
    assert isfinite(binary_loss_from_logit(-1000.0,1.0))
    dw,db=gradients(0.0,0.0,0.0)
    assert abs(dw+0.75)<1e-12 and abs(db)<1e-12
    eps=1e-5
    for w,b in ((0.2,-0.3),(1.0,0.5),(-0.6,0.4)):
        dw,db=gradients(w,b,0.1)
        fdw=(objective(w+eps,b)-objective(w-eps,b))/(2*eps)
        fdb=(objective(w,b+eps)-objective(w,b-eps))/(2*eps)
        assert abs(dw-fdw)<1e-8,(dw,fdw)
        assert abs(db-fdb)<1e-8,(db,fdb)
    w,b=train()
    assert objective(w,b)<objective(0.0,0.0)
    assert w>0 and abs(b)<1e-10

if __name__=="__main__":
    self_test()
    w,b=train()
    print(f"self_test PASS; w={w:.6f}; b={b:.6f}; objective={objective(w,b):.6f}")
