"""Small, deterministic one-dimensional GMM EM teaching implementation.

No external dependencies. Full covariance / multivariate support is intentionally
out of scope. Numerical guards change the pure textbook M-step at the boundary.
"""
from math import exp, isfinite, log, pi

DATA = [-2.3, -2.0, -1.8, -1.5, 0.8, 1.0, 1.3, 1.5]


def logpdf(x: float, mean: float, var: float) -> float:
    assert var > 0
    return -0.5 * (log(2 * pi * var) + (x - mean) ** 2 / var)


def logsumexp(values):
    peak = max(values)
    return peak + log(sum(exp(v - peak) for v in values))


def responsibilities(xs, weights, means, variances):
    result = []
    for x in xs:
        scores = [log(w) + logpdf(x, m, v)
                  for w, m, v in zip(weights, means, variances)]
        norm = logsumexp(scores)
        result.append([exp(v - norm) for v in scores])
    return result


def log_likelihood(xs, weights, means, variances):
    return sum(logsumexp([log(w) + logpdf(x, m, v)
                         for w, m, v in zip(weights, means, variances)])
               for x in xs)


def em_step(xs, weights, means, variances, min_var=1e-6):
    n = len(xs)
    resp = responsibilities(xs, weights, means, variances)
    effective = [sum(row[k] for row in resp) for k in range(2)]
    if any(nk <= 1e-12 for nk in effective):
        raise ValueError("Empty component; restart with new initialization")
    next_means = [sum(row[k] * x for row, x in zip(resp, xs)) / effective[k]
                  for k in range(2)]
    next_variances = [
        max(min_var, sum(row[k] * (x - next_means[k]) ** 2
                         for row, x in zip(resp, xs)) / effective[k])
        for k in range(2)
    ]
    next_weights = [nk / n for nk in effective]
    return next_weights, next_means, next_variances


def run_demo():
    weights, means, variances = [0.5, 0.5], [-2, 1], [1.0, 1.0]
    history = [log_likelihood(DATA, weights, means, variances)]
    for _ in range(25):
        weights, means, variances = em_step(DATA, weights, means, variances)
        value = log_likelihood(DATA, weights, means, variances)
        history.append(value)
    assert all(isfinite(v) for v in history)
    assert all(b + 1e-9 >= a for a, b in zip(history, history[1:]))
    assert abs(sum(weights) - 1) < 1e-12
    assert all(v > 0 for v in variances)
    assert all(abs(sum(row) - 1) < 1e-12
               for row in responsibilities(DATA, weights, means, variances))
    return weights, means, variances, history


if __name__ == "__main__":
    w, m, v, h = run_demo()
    print("weights:", [round(x, 4) for x in w])
    print("means:", [round(x, 4) for x in m])
    print("variances:", [round(x, 4) for x in v])
    print("initial/final log-likelihood:", round(h[0], 4), round(h[-1], 4))
