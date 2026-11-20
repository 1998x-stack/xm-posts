from collections import Counter
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rejection_sampling import best_of_n, rejection_sample


def test_rejection_sampling_recovers_target_distribution():
    target = [0.1, 0.3, 0.6]
    proposal = [0.4, 0.4, 0.2]
    samples = rejection_sample(target, proposal, n=50_000, seed=7)
    counts = Counter(samples)
    frequencies = [counts[i] / len(samples) for i in range(3)]
    assert abs(frequencies[0] - 0.1) < 0.012
    assert abs(frequencies[1] - 0.3) < 0.012
    assert abs(frequencies[2] - 0.6) < 0.012


def test_proposal_must_cover_target_support():
    with pytest.raises(ValueError):
        rejection_sample([0.5, 0.5], [1.0, 0.0], n=10)


def test_invalid_distribution_is_rejected():
    with pytest.raises(ValueError):
        rejection_sample([0.2, 0.2], [0.5, 0.5], n=10)


def test_best_of_n_is_a_separate_ranking_operation():
    assert best_of_n(["low", "high", "middle"], [0.1, 0.9, 0.4]) == "high"
