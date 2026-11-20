from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("mcp_contract_demo.py")
SPEC = importlib.util.spec_from_file_location("mcp_contract_demo", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_read_only_tool_builds_current_protocol_request():
    headers, body = MODULE.prepare_call(
        "search_docs", {"query": "MCP security", "limit": 3}
    )
    assert headers["MCP-Protocol-Version"] == "2026-07-28"
    assert headers["Mcp-Method"] == "tools/call"
    assert headers["Mcp-Name"] == "search_docs"
    assert body["jsonrpc"] == "2.0"
    assert body["method"] == "tools/call"
    assert body["params"]["name"] == "search_docs"
    assert body["params"]["_meta"]["io.modelcontextprotocol/protocolVersion"] == "2026-07-28"


def test_mutating_tool_requires_explicit_approval():
    with pytest.raises(MODULE.ApprovalRequired):
        MODULE.prepare_call("delete_record", {"record_id": "r-17"})
    headers, body = MODULE.prepare_call(
        "delete_record", {"record_id": "r-17"}, approved=True
    )
    assert headers["Mcp-Name"] == "delete_record"
    assert body["params"]["arguments"]["record_id"] == "r-17"


def test_allow_list_is_checked_before_request_construction():
    with pytest.raises(PermissionError, match="allow-listed"):
        MODULE.prepare_call(
            "delete_record",
            {"record_id": "r-17"},
            approved=True,
            allowed_tools={"search_docs"},
        )


def test_schema_rejects_missing_unknown_and_wrongly_typed_arguments():
    with pytest.raises(ValueError, match="missing"):
        MODULE.prepare_call("search_docs", {})
    with pytest.raises(ValueError, match="unknown"):
        MODULE.prepare_call("search_docs", {"query": "x", "admin": True})
    with pytest.raises(TypeError, match="limit"):
        MODULE.prepare_call("search_docs", {"query": "x", "limit": "three"})


def test_response_id_must_match_the_request():
    response = {"jsonrpc": "2.0", "id": 17, "result": {"content": []}}
    assert MODULE.validate_response(response, 17) == {"content": []}
    with pytest.raises(ValueError, match="id"):
        MODULE.validate_response(response, 18)
