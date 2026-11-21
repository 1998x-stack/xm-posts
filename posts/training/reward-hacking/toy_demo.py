#!/usr/bin/env python3
"""A deterministic toy model showing proxy reward rising as true reward falls.

This is an analytic teaching example, not an empirical model-training result.
"""
from __future__ import annotations


def evaluate(alpha: float) -> dict[str, float]:
    """Return the proxy-optimal action and both rewards for alpha >= 0."""
    if alpha < 0:
        raise ValueError("alpha must be non-negative")

    x_star = 1.0 + alpha / 2.0
    true_reward = -((x_star - 1.0) ** 2)
    proxy_reward = true_reward + alpha * x_star

    return {
        "alpha": alpha,
        "x_star": x_star,
        "proxy_reward": proxy_reward,
        "true_reward": true_reward,
    }


def main() -> None:
    print("alpha | x*    | proxy | true")
    for alpha in (0.0, 1.0, 2.0, 3.0):
        result = evaluate(alpha)
        print(
            f"{alpha:>5.1f} | {result['x_star']:>5.2f} | "
            f"{result['proxy_reward']:>5.2f} | {result['true_reward']:>5.2f}"
        )


if __name__ == "__main__":
    main()
