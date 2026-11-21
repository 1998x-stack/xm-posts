"""Deterministic invariants for the Reflection teaching example."""
import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "posts" / "agents" / "reflection" / "reflection_demo.py"
SPEC = importlib.util.spec_from_file_location("reflection_demo", MODULE_PATH)
reflection_demo = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(reflection_demo)


class TestReflectionDemo(unittest.TestCase):
    def test_failed_sum_is_corrected_and_reverified(self):
        result = reflection_demo.run_mean_reflection([1, 2, 3])
        self.assertTrue(result["success"])
        self.assertEqual([row["candidate"] for row in result["attempts"]], ["sum", "mean"])
        self.assertEqual(result["attempts"][0]["output"], 6.0)
        self.assertEqual(result["attempts"][-1]["output"], 2.0)
        self.assertTrue(result["attempts"][-1]["passed"])
        self.assertEqual(len(result["memory"]), 1)

    def test_one_round_budget_does_not_claim_success(self):
        result = reflection_demo.run_mean_reflection([1, 2, 3], max_rounds=1)
        self.assertFalse(result["success"])
        self.assertEqual(result["rounds_used"], 1)
        self.assertEqual(result["final_candidate"], "sum")

    def test_single_element_is_already_a_valid_mean(self):
        result = reflection_demo.run_mean_reflection([7])
        self.assertTrue(result["success"])
        self.assertEqual(result["rounds_used"], 1)
        self.assertEqual(result["memory"], [])

    def test_negative_and_fractional_values(self):
        result = reflection_demo.run_mean_reflection([-2, 0, 1.5])
        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["attempts"][-1]["output"], -1 / 6)

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            reflection_demo.run_mean_reflection([])

    def test_nonpositive_round_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            reflection_demo.run_mean_reflection([1, 2], max_rounds=0)


if __name__ == "__main__":
    unittest.main()
