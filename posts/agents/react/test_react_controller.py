"""Invariant tests for the closed-world ReAct-pattern teaching controller."""
import unittest
from react_controller import tool, replay


class ReActControllerTests(unittest.TestCase):
    def test_normal(self):
        trace = replay()
        self.assertEqual(trace[-1], {"kind": "finish", "value": "Lin"})
        self.assertEqual(sum(x["kind"] == "action" for x in trace), 2)

    def test_recover_empty_search(self):
        trace = replay(fail_first=True)
        self.assertEqual(trace[-1]["value"], "Lin")
        self.assertEqual(sum(x["kind"] == "action" for x in trace), 3)
        self.assertIn("(empty)", [x["value"] for x in trace])

    def test_budget_stops(self):
        self.assertEqual(replay(fail_first=True, step_limit=2)[-1]["kind"], "stopped")
        with self.assertRaises(ValueError):
            replay(step_limit=0)

    def test_tool_allowlist(self):
        with self.assertRaises(ValueError):
            tool("run_shell", "rm -rf /")
        self.assertEqual(tool("lookup", "Aurora"), "Aurora 团队负责人是 Lin。")


if __name__ == "__main__":
    unittest.main()
