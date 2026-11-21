"""A tiny Host-side MCP call adapter for teaching and deterministic tests.

This is NOT a complete MCP SDK or a network client. It demonstrates the
policy boundary before a Host sends a JSON-RPC tools/call request.
"""
from __future__ import annotations

PROTOCOL_VERSION = "2026-07-28"


class ApprovalRequired(PermissionError):
    """Raised when a mutating tool has not received explicit approval."""


TOOLS = {
    "search_docs": {
        "read_only": True,
        "required": {"query": str},
        "optional": {"limit": int},
    },
    "delete_record": {
        "read_only": False,
        "required": {"record_id": str},
        "optional": {},
    },
}


def _validate_arguments(tool_name: str, arguments: dict) -> None:
    spec = TOOLS[tool_name]
    if not isinstance(arguments, dict):
        raise TypeError("tool arguments must be an object")
    allowed = set(spec["required"]) | set(spec["optional"])
    unknown = set(arguments) - allowed
    missing = set(spec["required"]) - set(arguments)
    if unknown:
        raise ValueError("unknown arguments: " + ", ".join(sorted(unknown)))
    if missing:
        raise ValueError("missing arguments: " + ", ".join(sorted(missing)))
    for name, expected_type in {**spec["required"], **spec["optional"]}.items():
        if name in arguments and type(arguments[name]) is not expected_type:
            raise TypeError(name + " must be " + expected_type.__name__)


def prepare_call(
    tool_name: str,
    arguments: dict,
    *,
    approved: bool = False,
    allowed_tools: set[str] | None = None,
    request_id: int = 1,
    client_name: str = "xm-posts-teaching-host",
) -> tuple[dict, dict]:
    """Validate policy and construct a version-scoped JSON-RPC request."""
    if tool_name not in TOOLS:
        raise ValueError("unknown tool: " + tool_name)
    if allowed_tools is not None and tool_name not in allowed_tools:
        raise PermissionError("tool is not allow-listed: " + tool_name)
    _validate_arguments(tool_name, arguments)
    if not TOOLS[tool_name]["read_only"] and not approved:
        raise ApprovalRequired("explicit approval required for " + tool_name)

    headers = {
        "Content-Type": "application/json",
        "MCP-Protocol-Version": PROTOCOL_VERSION,
        "Mcp-Method": "tools/call",
        "Mcp-Name": tool_name,
    }
    body = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments,
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": PROTOCOL_VERSION,
                "io.modelcontextprotocol/clientInfo": {
                    "name": client_name,
                    "version": "1.0.0",
                },
                "io.modelcontextprotocol/clientCapabilities": {},
            },
        },
    }
    return headers, body


def validate_response(response: dict, expected_id: int) -> dict:
    """Reject mismatched or malformed JSON-RPC responses."""
    if not isinstance(response, dict) or response.get("jsonrpc") != "2.0":
        raise ValueError("invalid JSON-RPC response envelope")
    if response.get("id") != expected_id:
        raise ValueError("response id does not match request id")
    if "error" in response:
        raise RuntimeError("remote JSON-RPC error: " + str(response["error"]))
    if "result" not in response:
        raise ValueError("response has neither result nor error")
    return response["result"]


if __name__ == "__main__":
    request_headers, request_body = prepare_call(
        "search_docs", {"query": "MCP security", "limit": 3}
    )
    print("headers:", request_headers)
    print("jsonrpc:", request_body)
    try:
        prepare_call("delete_record", {"record_id": "r-17"})
    except ApprovalRequired as exc:
        print("blocked:", exc)
    approved_headers, approved_body = prepare_call(
        "delete_record", {"record_id": "r-17"}, approved=True
    )
    print("approved request:", approved_headers["Mcp-Name"], approved_body["id"])
