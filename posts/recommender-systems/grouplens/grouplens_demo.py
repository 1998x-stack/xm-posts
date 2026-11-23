"""Deterministic GroupLens-style user-user collaborative filtering demo.

This is a small teaching implementation of the Pearson-weighted deviation
predictor illustrated in Resnick et al. (1994), not a reproduction of the
distributed Better Bit Bureau system.

The ratings dictionaries map article IDs to explicit 1..5 ratings.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import sqrt
from typing import Optional

RatingProfile = Mapping[str, float]


def mean_rating(profile: RatingProfile) -> Optional[float]:
    """Return the mean of a user's observed ratings, or None for no ratings."""
    values = list(profile.values())
    if not values:
        return None
    return sum(values) / len(values)


def pearson_similarity(a: RatingProfile, b: RatingProfile) -> Optional[float]:
    """Pearson correlation over co-rated items only.

    Returns None when fewer than two co-rated items exist or either profile
    has zero variance on the co-rated subset. None is not silently converted
    to zero: those cases are undefined, not evidence of dissimilarity.
    """
    common = sorted(set(a).intersection(b))
    if len(common) < 2:
        return None

    av = [float(a[item]) for item in common]
    bv = [float(b[item]) for item in common]
    mean_a = sum(av) / len(av)
    mean_b = sum(bv) / len(bv)
    centered_a = [value - mean_a for value in av]
    centered_b = [value - mean_b for value in bv]

    numerator = sum(x * y for x, y in zip(centered_a, centered_b))
    norm_a = sqrt(sum(x * x for x in centered_a))
    norm_b = sqrt(sum(y * y for y in centered_b))
    denominator = norm_a * norm_b
    if denominator == 0:
        return None
    return numerator / denominator


def predict_rating(
    target_user: str,
    target_item: str,
    profiles: Mapping[str, RatingProfile],
) -> Optional[float]:
    """Predict one missing rating with Pearson-weighted deviations.

    The target user's baseline is the mean of all observed ratings in their
    profile. Each neighbor contributes only if they rated target_item and
    their Pearson similarity is defined and nonzero. Negative similarities
    are retained; normalization uses the sum of absolute similarities.
    """
    if target_user not in profiles:
        raise KeyError(f"unknown target user: {target_user}")

    target_profile = profiles[target_user]
    baseline = mean_rating(target_profile)
    if baseline is None:
        return None

    numerator = 0.0
    denominator = 0.0
    for neighbor, profile in profiles.items():
        if neighbor == target_user or target_item not in profile:
            continue
        similarity = pearson_similarity(target_profile, profile)
        if similarity is None or abs(similarity) < 1e-12:
            continue
        neighbor_history = {item: value for item, value in profile.items() if item != target_item}
        neighbor_mean = mean_rating(neighbor_history)
        if neighbor_mean is None:
            continue
        numerator += similarity * (float(profile[target_item]) - neighbor_mean)
        denominator += abs(similarity)

    if denominator == 0:
        return None
    return baseline + numerator / denominator


def figure_5_profiles() -> dict[str, dict[str, float]]:
    """Return the explicit ratings transcribed from Figure 5 (paper p. 180)."""
    return {
        "Ken": {"1": 1, "2": 5, "4": 2, "5": 4},
        "Lee": {"1": 4, "2": 2, "4": 5, "5": 1, "6": 2},
        "Meg": {"1": 2, "2": 4, "3": 3, "6": 5},
        "Nan": {"1": 2, "2": 4, "4": 5, "5": 1},
    }


def main() -> None:
    profiles = figure_5_profiles()
    for neighbor in ("Lee", "Meg", "Nan"):
        print(f"Ken–{neighbor}: {pearson_similarity(profiles['Ken'], profiles[neighbor])}")
    ken_prediction = predict_rating("Ken", "6", profiles)
    nan_prediction = predict_rating("Nan", "6", profiles)
    print(f"Ken / article 6 (independent calculation): {ken_prediction:.6f}")
    print(f"Nan / article 6 (independent calculation): {nan_prediction:.6f}")
    print("Paper p. 181 reports Nan = 3.75; Figure 5 + displayed formula recalculate to 3.875.")


if __name__ == "__main__":
    main()
