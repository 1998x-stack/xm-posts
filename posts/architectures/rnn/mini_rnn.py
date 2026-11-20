"""Scalar tanh RNN with explicit full BPTT (educational, not Elman 1990 reproduction).
Requires Python 3.11+, standard library only, deterministic data.
"""
from math import tanh

X = (0.25, -0.4, 0.1, 0.3)
TARGET = (0.05, -0.12, 0.08, 0.15)
PARAMS = (0.7, 0.55, -0.8)  # input weight, recurrent weight, output weight


def loss_and_grad(params=PARAMS, x=X, target=TARGET):
    if len(x) != len(target) or not x:
        raise ValueError("x and target must have equal nonzero length")
    wx, wh, v = params
    h = [0.0]
    for xt in x:
        h.append(tanh(wx * xt + wh * h[-1]))
    y = [v * z for z in h[1:]]
    loss = sum(0.5 * (pred - gold)**2 for pred, gold in zip(y, target))
    gwx = gwh = gv = dh_future = 0.0
    for t in range(len(x) - 1, -1, -1):
        dy = y[t] - target[t]
        gv += dy * h[t + 1]
        dh = dy * v + dh_future
        da = dh * (1.0 - h[t + 1]**2)
        gwx += da * x[t]
        gwh += da * h[t]
        dh_future = da * wh
    return loss, (gwx, gwh, gv)


def finite_difference(params=PARAMS, eps=1e-6):
    values = []
    for i in range(len(params)):
        p, q = list(params), list(params)
        p[i] += eps
        q[i] -= eps
        values.append((loss_and_grad(tuple(p))[0] -
                       loss_and_grad(tuple(q))[0]) / (2.0 * eps))
    return tuple(values)


def check(tol=1e-6):
    loss, exact = loss_and_grad()
    numeric = finite_difference()
    for a, n in zip(exact, numeric):
        assert abs(a - n) < tol, (a, n)
    return loss, exact


if __name__ == "__main__":
    print("loss and gradients:", check())
