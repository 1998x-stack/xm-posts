"""Standard-library tests of syntax-only editing guardrails."""
import unittest
from aci_demo import guarded_edit, demo

class GuardTests(unittest.TestCase):
    def test_reject_syntax_error(self):
        self.assertEqual(guarded_edit("x = 1\n", "x =\n"), ("x = 1\n", "rejected"))
    def test_accept_valid_code(self):
        self.assertEqual(guarded_edit("x = 1\n", "x = 2\n"), ("x = 2\n", "applied"))
    def test_reject_non_text(self):
        with self.assertRaises(TypeError):
            guarded_edit(None, "x = 2\n")
    def test_syntax_is_not_correctness(self):
        self.assertEqual(guarded_edit("x = 2\n", "x = 1\n")[1], "applied")
    def test_demo(self):
        self.assertIn("sum(xs) / len(xs)", demo())

if __name__ == "__main__":
    unittest.main()
