"""Numerical checks for the GroupLens Figure 5 teaching implementation."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts/recommender-systems/grouplens"))

from grouplens_demo import (  # noqa: E402
    figure_5_profiles,
    mean_rating,
    pearson_similarity,
    predict_rating,
)


def test_figure_5_pairwise_correlations_match_the_paper():
    profiles = figure_5_profiles()
    assert pearson_similarity(profiles["Ken"], profiles["Lee"]) == pytest.approx(-0.8)
    assert pearson_similarity(profiles["Ken"], profiles["Meg"]) == pytest.approx(1.0)
    assert pearson_similarity(profiles["Ken"], profiles["Nan"]) == pytest.approx(0.0)


def test_ken_article_six_prediction_matches_the_paper():
    profiles = figure_5_profiles()
    assert predict_rating("Ken", "6", profiles) == pytest.approx(4.555555555555555)


def test_nan_article_six_independent_recalculation_is_transparent():
    profiles = figure_5_profiles()
    assert pearson_similarity(profiles["Nan"], profiles["Lee"]) == pytest.approx(0.6)
    assert pearson_similarity(profiles["Nan"], profiles["Meg"]) == pytest.approx(1.0)
    assert predict_rating("Nan", "6", profiles) == pytest.approx(3.875)
    # The original text reports 3.75; the discrepancy is recorded in the article/evidence.
    assert 3.875 != 3.75


def test_one_common_item_is_not_a_defined_pearson_correlation():
    assert pearson_similarity({"a": 1, "b": 2}, {"a": 4, "c": 5}) is None


def test_zero_variance_on_common_items_is_not_a_defined_correlation():
    assert pearson_similarity({"a": 3, "b": 3, "c": 4}, {"a": 1, "b": 5, "d": 2}) is None


def test_prediction_returns_none_when_no_neighbor_has_a_defined_nonzero_similarity():
    profiles = {
        "target": {"a": 1, "b": 2},
        "neighbor": {"c": 4, "d": 5},
    }
    assert predict_rating("target", "c", profiles) is None


def test_prediction_keeps_negative_similarity_instead_of_discarding_it():
    profiles = figure_5_profiles()
    # Lee's low score is useful because Lee is negatively correlated with Ken.
    assert predict_rating("Ken", "6", profiles) > 3.5


def test_empty_profile_has_no_baseline():
    assert mean_rating({}) is None


# pytest is imported at the end to keep the implementation module dependency-free.
import pytest  # noqa: E402
