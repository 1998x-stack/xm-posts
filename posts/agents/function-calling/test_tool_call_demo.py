import unittest

from tool_call_demo import execute_function_call


class FunctionCallExecutorTests(unittest.TestCase):
    def valid_call(self):
        return {
            "call_id": "call_test_001",
            "name": "get_weather",
            "arguments": "{\"location\":\"Tokyo\"}",
        }

    def test_valid_call_preserves_call_id_and_returns_fixture(self):
        result = execute_function_call(self.valid_call())
        self.assertEqual(result.call_id, "call_test_001")
        self.assertEqual(result.output["location"], "Tokyo")
        self.assertEqual(result.output["temperature_c"], 18)
        self.assertEqual(result.output["condition"], "cloudy")

    def test_unknown_tool_is_rejected(self):
        call = self.valid_call()
        call["name"] = "delete_everything"
        with self.assertRaisesRegex(ValueError, "allowlisted"):
            execute_function_call(call)

    def test_malformed_json_is_rejected(self):
        call = self.valid_call()
        call["arguments"] = "{\"location\":"
        with self.assertRaisesRegex(ValueError, "valid JSON"):
            execute_function_call(call)

    def test_extra_argument_is_rejected(self):
        call = self.valid_call()
        call["arguments"] = "{\"location\":\"Tokyo\",\"forecast_days\":3}"
        with self.assertRaisesRegex(ValueError, "exactly one field"):
            execute_function_call(call)

    def test_missing_argument_is_rejected(self):
        call = self.valid_call()
        call["arguments"] = "{}"
        with self.assertRaisesRegex(ValueError, "exactly one field"):
            execute_function_call(call)

    def test_empty_location_is_rejected(self):
        call = self.valid_call()
        call["arguments"] = "{\"location\":\"   \"}"
        with self.assertRaisesRegex(ValueError, "non-empty"):
            execute_function_call(call)

    def test_missing_call_id_is_rejected(self):
        call = self.valid_call()
        call["call_id"] = ""
        with self.assertRaisesRegex(ValueError, "call_id"):
            execute_function_call(call)


if __name__ == "__main__":
    unittest.main()
