"""Small deterministic NoisyNet mathematics checks; not an Atari reproduction."""
from math import copysign, isclose, sqrt

def f(z: float) -> float:
    """Factorised noise transform from Fortunato et al., Eq. 10-11."""
    return copysign(sqrt(abs(z)), z) if z else 0.0

def factorised(eps_in, eps_out):
    """Return q-by-p weight noise and q bias noise."""
    if not eps_in or not eps_out:
        raise ValueError("dimensions must be positive")
    u = [f(v) for v in eps_in]
    v = [f(v) for v in eps_out]
    return [[b * a for a in u] for b in v], v

def sample_counts(p: int, q: int):
    if p < 1 or q < 1:
        raise ValueError("dimensions must be positive")
    return {"independent": p * q + q, "factorised": p + q}

def noisy_linear(x, mu_w, sigma_w, mu_b, sigma_b, eps_w, eps_b):
    q = len(mu_w)
    p = len(x)
    if q == 0 or p == 0 or any(len(v) != q for v in (sigma_w,)) or any(len(v) != p for v in mu_w + sigma_w + eps_w) or len(eps_w) != q or any(len(v) != q for v in (mu_b, sigma_b, eps_b)):
        raise ValueError("invalid shapes")
    return [sum((mu_w[j][i] + sigma_w[j][i] * eps_w[j][i]) * x[i] for i in range(p)) + mu_b[j] + sigma_b[j] * eps_b[j] for j in range(q)]

def squared_loss_gradients(mu, sigma, eps, x, target):
    """Scalar reparameterised noisy weight, 0.5*(y-target)^2."""
    y = (mu + sigma * eps) * x
    dy = y - target
    return dy * x, dy * eps * x

def _checks():
    w, b = factorised([1.0, 4.0], [9.0, -16.0])
    assert w == [[3.0, 6.0], [-4.0, -8.0]]
    assert b == [3.0, -4.0]
    assert sample_counts(4, 2) == {"independent": 10, "factorised": 6}
    mu_w = [[1.0, 0.0], [0.0, 1.0]]
    sig_w = [[0.1, 0.1], [0.1, 0.1]]
    y = noisy_linear([2.0, 3.0], mu_w, sig_w, [0, 0], [0, 0], w, b)
    assert all(isclose(a, z) for a, z in zip(y, [4.4, -0.2]))
    zero = noisy_linear([2.0, 3.0], mu_w, [[0, 0], [0, 0]], [0, 0], [0, 0], w, b)
    assert zero == [2.0, 3.0]
    mu, sigma, eps, x, target = 0.7, 0.3, -0.8, 2.0, 1.5
    ga, gb = squared_loss_gradients(mu, sigma, eps, x, target)
    def loss(m, s):
        return 0.5 * (((m + s * eps) * x) - target) ** 2
    h = 1e-6
    assert isclose(ga, (loss(mu + h, sigma) - loss(mu - h, sigma)) / (2*h), abs_tol=1e-8)
    assert isclose(gb, (loss(mu, sigma + h) - loss(mu, sigma - h)) / (2*h), abs_tol=1e-8)
    assert [round(100 * (n - b) / b) for b, n in [(83, 123), (132, 172), (80, 94)]] == [48, 30, 18]
    return True

if __name__ == "__main__":
    assert _checks()
    print("NoisyNet deterministic math checks passed")
