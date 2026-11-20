"""Minimal, dependency-free DPO arithmetic, not a language-model trainer.

All log-probs are conditional completion sequence log probabilities.
See Rafailov et al., NeurIPS 2023, Eq. (7).
"""
from __future__ import annotations
from math import exp, log1p
from typing import Sequence


def completion_logp(token_logps: Sequence[float], mask: Sequence[bool]) -> float:
    """Sum log p(token | prefix) for completion labels only (not prompt/pad)."""
    if len(token_logps) != len(mask) or not any(mask):
        raise ValueError("mask must match log-probs and include completion tokens")
    return sum(float(v) for v, take in zip(token_logps, mask) if take)


def softplus(x: float) -> float:
    """Stable log(1+exp(x)), including large positive/negative values."""
    return max(x, 0.0) + log1p(exp(-abs(x)))


def dpo_margin(chosen_policy: float, rejected_policy: float,
               chosen_ref: float, rejected_ref: float) -> float:
    """Chosen log-ratio minus rejected log-ratio."""
    return (chosen_policy - chosen_ref) - (rejected_policy - rejected_ref)


def dpo_loss(chosen_policy: float, rejected_policy: float,
             chosen_ref: float, rejected_ref: float,
             beta: float = 0.1) -> float:
    """Negative log sigmoid(beta * margin), stable over large margins."""
    if not (0 < beta < float("inf")):
        raise ValueError("beta must be finite and positive")
    return softplus(-beta * dpo_margin(
        chosen_policy, rejected_policy, chosen_ref, rejected_ref))


def chosen_gradient(chosen_policy: float, rejected_policy: float,
                    chosen_ref: float, rejected_ref: float,
                    beta: float = 0.1) -> float:
    """Derivative of DPO loss wrt chosen_policy log-prob; reference fixed."""
    if not (0 < beta < float("inf")):
        raise ValueError("beta must be finite and positive")
    z = beta * dpo_margin(chosen_policy, rejected_policy, chosen_ref, rejected_ref)
    sigmoid_negative = exp(-softplus(z))
    return -beta * sigmoid_negative


if __name__ == "__main__":
    from math import log
    assert abs(dpo_loss(-2.0, -3.0, -2.0, -3.0) - log(2)) < 1e-12
    assert completion_logp([-1.0, -0.2, -0.3, -9.0], [False, True, True, False]) == -0.5
    assert dpo_loss(-2.2, -3.6, -2.8, -3.4, 0.5) < log(2)
    print("DPO minimal checks passed; no model training performed.")
