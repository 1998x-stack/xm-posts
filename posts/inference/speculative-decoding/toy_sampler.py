"""Pure-stdlib pedagogical checks for one-position speculative sampling.

The function computes the *exact marginal distribution*, not wall-clock latency.
See Leviathan et al., ICML 2023, Section 2.3 and Appendix A.1.
"""
from math import isclose


def _distribution(values):
    values = tuple(float(x) for x in values)
    if not values or any(x < 0 or x > 1 for x in values):
        raise ValueError("probabilities must be in [0,1] and nonempty")
    if not isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise ValueError("probabilities must sum to 1")
    return values


def exact_marginal(target, draft):
    """Combine accepted q mass and corrected rejected mass at one token."""
    p, q = _distribution(target), _distribution(draft)
    if len(p) != len(q):
        raise ValueError("target and draft must use the same vocabulary")
    accepted = [min(a, b) for a, b in zip(p, q)]
    rejected = max(0.0, 1.0 - sum(accepted))
    positive_residual = [max(0.0, a - b) for a, b in zip(p, q)]
    total_residual = sum(positive_residual)
    if total_residual < 1e-12:
        return tuple(accepted)
    return tuple(a + rejected * r / total_residual
                 for a, r in zip(accepted, positive_residual))


def expected_tokens(alpha, gamma):
    """Capped-geometric mean under the paper's i.i.d. acceptance assumption."""
    if not (0 <= alpha <= 1) or not isinstance(gamma, int) or gamma < 1:
        raise ValueError("alpha in [0,1], gamma a positive integer")
    return sum(alpha ** i for i in range(gamma + 1))


def idealized_speedup(alpha, gamma, draft_cost_ratio):
    """Illustrative serial-latency model; not a benchmark."""
    if draft_cost_ratio < 0:
        raise ValueError("draft cost must be nonnegative")
    return expected_tokens(alpha, gamma) / (1 + gamma * draft_cost_ratio)


if __name__ == "__main__":
    p, q = (.3, .4, .3), (.6, .3, .1)
    out = exact_marginal(p, q)
    assert all(isclose(x, y, abs_tol=1e-12) for x, y in zip(out, p))
    print("p =", p, "q =", q, "output =", out)
    print("E[tokens] =", expected_tokens(.75, 3))
    print("idealized speedup =", round(idealized_speedup(.75, 3, .05), 4))
