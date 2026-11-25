"""A deterministic Bernoulli policy-gradient example for Score Centering.
This is a one-parameter teaching model, not an LLM trainer or paper reproduction.
"""
def _check_probability(value: float, name: str) -> None:
    if not 0.0 < value < 1.0:
        raise ValueError(f"{name} must be strictly between 0 and 1")


def decompose(p: float, q: float, advantage_one: float, advantage_zero: float) -> dict[str, float]:
    """Return naive update, drift, covariance signal and centered update."""
    _check_probability(p, "p")
    _check_probability(q, "q")
    score_one, score_zero = 1.0 - p, -p
    mean_score = q * score_one + (1.0 - q) * score_zero
    mean_advantage = q * advantage_one + (1.0 - q) * advantage_zero
    naive = q * advantage_one * score_one + (1.0 - q) * advantage_zero * score_zero
    drift = mean_advantage * mean_score
    signal = (
        q * (advantage_one - mean_advantage) * (score_one - mean_score)
        + (1.0 - q) * (advantage_zero - mean_advantage) * (score_zero - mean_score)
    )
    centered = (
        q * advantage_one * (score_one - mean_score)
        + (1.0 - q) * advantage_zero * (score_zero - mean_score)
    )
    return {"mean_score":mean_score,"mean_advantage":mean_advantage,"naive":naive,
            "drift":drift,"signal":signal,"centered":centered}


if __name__ == "__main__":
    for name, value in decompose(0.6, 0.8, 1.5, -0.5).items():
        print(f"{name:>16}: {value: .6f}")
