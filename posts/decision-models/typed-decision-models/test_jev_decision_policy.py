"""Deterministic unit tests for the teaching decision policy."""
import unittest

from jev_decision_policy import (
    binary_cost_threshold,
    choose_with_review,
    expected_risks,
    validate_distribution,
)


PROBABILITIES = {"billing": 0.70, "support": 0.20, "delivery": 0.10}
COSTS = {
    "route_billing": {"billing": 0, "support": 4, "delivery": 5},
    "route_support": {"billing": 3, "support": 0, "delivery": 4},
    "route_delivery": {"billing": 5, "support": 4, "delivery": 0},
}


class DecisionPolicyTests(unittest.TestCase):
    def test_valid_distribution_is_copied(self):
        source = dict(PROBABILITIES)
        result = validate_distribution(source)
        self.assertEqual(result, source)
        self.assertIsNot(result, source)

    def test_rejects_empty_distribution(self):
        with self.assertRaises(ValueError):
            validate_distribution({})

    def test_rejects_distribution_that_does_not_sum_to_one(self):
        with self.assertRaises(ValueError):
            validate_distribution({"a": 0.7, "b": 0.2})

    def test_rejects_negative_and_non_finite_probabilities(self):
        for bad in (-0.1, float("nan"), float("inf"), True):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_distribution({"a": bad, "b": 1.0 - bad})

    def test_expected_risks_match_hand_calculation(self):
        risks = expected_risks(PROBABILITIES, COSTS)
        self.assertAlmostEqual(risks["route_billing"], 1.30)
        self.assertAlmostEqual(risks["route_support"], 2.50)
        self.assertAlmostEqual(risks["route_delivery"], 4.30)

    def test_missing_cost_label_is_rejected(self):
        incomplete = {
            "route_billing": {"billing": 0, "support": 4},
        }
        with self.assertRaises(ValueError):
            expected_risks(PROBABILITIES, incomplete)

    def test_review_wins_when_its_cost_is_lower(self):
        result = choose_with_review(PROBABILITIES, COSTS, review_cost=1.0)
        self.assertEqual(result.action, "review")
        self.assertAlmostEqual(result.expected_loss, 1.0)

    def test_automatic_action_wins_when_review_is_more_expensive(self):
        result = choose_with_review(PROBABILITIES, COSTS, review_cost=2.0)
        self.assertEqual(result.action, "route_billing")
        self.assertAlmostEqual(result.expected_loss, 1.3)

    def test_binary_threshold_uses_asymmetric_costs(self):
        self.assertAlmostEqual(binary_cost_threshold(20, 180), 0.1)

    def test_binary_threshold_rejects_zero_total_cost(self):
        with self.assertRaises(ValueError):
            binary_cost_threshold(0, 0)


if __name__ == "__main__":
    unittest.main()
