"""Exact pedagogical two-dimensional PCA without external dependencies.

Uses an analytic 2x2 covariance eigensystem for teaching; not a production SVD.
"""
from math import atan2, cos, sin, hypot, isfinite

def fit_pca_2d(points):
    points = [tuple(map(float, p)) for p in points]
    if len(points) < 2 or any(len(p) != 2 for p in points):
        raise ValueError("At least two 2D observations required")
    if not all(isfinite(v) for p in points for v in p):
        raise ValueError("Every coordinate must be finite")
    n = len(points)
    mu = (sum(p[0] for p in points)/n, sum(p[1] for p in points)/n)
    centered = [(x-mu[0], y-mu[1]) for x, y in points]
    a = sum(x*x for x, y in centered)/(n-1)
    b = sum(x*y for x, y in centered)/(n-1)
    c = sum(y*y for x, y in centered)/(n-1)
    total = a+c
    if total <= 0: raise ValueError("zero total variance")
    spread = hypot(a-c, 2*b)
    eigenvalues = ((total+spread)/2, max(0., (total-spread)/2))
    theta = .5*atan2(2*b, a-c)
    w = (cos(theta), sin(theta))
    if w[0] < 0 or (abs(w[0]) < 1e-12 and w[1] < 0):w = (-w[0],-w[1])
    return {"mean":mu, "covariance":((a,b),(b,c)), "component":w,
            "eigenvalues":eigenvalues, "explained_variance_ratio":eigenvalues[0]/total}

def transform(points, model):
    mx, my = model["mean"]
    wx, wy = model["component"]
    return [(float(x)-mx)*wx+(float(y)-my)*wy for x,y in points]

def inverse_transform(scores, model):
    mx, my = model["mean"]
    wx, wy = model["component"]
    return [(mx+s*wx,my+s*wy) for s in scores]

if __name__ == "__main__":
    data = [(-2,0),(0,-1),(0,1),(2,0)]
    m = fit_pca_2d(data)
    assert abs(m["explained_variance_ratio"]-.8)<1e-12
    assert abs(m["eigenvalues"][0]-8/3)<1e-12
    print("PCA toy assertions passed; explained variance 80%")
