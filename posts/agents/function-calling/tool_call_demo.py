from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolResult:
    call_id: str
    output: dict[str, Any]


def get_weather(location: str) -> dict[str, Any]:
    """Return deterministic teaching data; this function does not access a network."""
    return {
        "location": location,
        "temperature_c": 18,
        "condition": "cloudy",
    }


TOOLS: dict[str, Callable[[str], dict[str, Any]]] = {
    "get_weather": get_weather,
}


def execute_function_call(call: dict[str, Any]) -> ToolResult:
    """Validate a normalized tool-call envelope before invoking an allowlisted tool."""
    if not isinstance(call, dict) or set(call) != {"call_id", "name", "arguments"}:
        raise ValueError("invalid call envelope")

    call_id = call["call_id"]
    name = call["name"]
    raw_arguments = call["arguments"]

    if not isinstance(call_id, str) or not call_id:
        raise ValueError("missing call_id")
    if not isinstance(name, str) or name not in TOOLS:
        raise ValueError("tool is not allowlisted")
    if not isinstance(raw_arguments, str):
        raise ValueError("arguments must be a JSON string")

    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ValueError("arguments are not valid JSON") from exc

    if not isinstance(arguments, dict):
        raise ValueError("arguments must be an object")
    if set(arguments) != {"location"}:
        raise ValueError("expected exactly one field: location")

    location = arguments["location"]
    if not isinstance(location, str) or not location.strip():
        raise ValueError("location must be a non-empty string")
    if len(location) > 80:
        raise ValueError("location is too long")

    output = TOOLS[name](location.strip())
    return ToolResult(call_id=call_id, output=output)


if __name__ == "__main__":
    request = {
        "call_id": "call_demo_001",
        "name": "get_weather",
        "arguments": "{\"location\":\"Tokyo\"}",
    }
    result = execute_function_call(request)
    print(json.dumps({
        "call_id": result.call_id,
        "output": result.output,
    }, ensure_ascii=False, indent=2))
