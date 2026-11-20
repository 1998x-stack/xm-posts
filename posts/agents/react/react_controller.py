#!/usr/bin/env python3
"""Deterministic ReAct-pattern control-flow teaching example; NOT a language model.
Only standard library. Uses fictional closed-world records.
"""
from __future__ import annotations

from typing import Any

ALLOWED = frozenset({"search", "lookup", "finish"})
FACTS = {
    ("search", "Lumen"): "Lumen 项目归属于 Aurora 团队。",
    ("search", "Lumen 项目"): "Lumen 项目归属于 Aurora 团队。",
    ("lookup", "Aurora"): "Aurora 团队负责人是 Lin。",
}


def tool(name: str, argument: str, *, fail_first: bool = False) -> str:
    """An allow-listed toy adapter. Never executes external commands."""
    if name not in ALLOWED:
        raise ValueError("Tool not allow-listed: " + name)
    if name == "finish":
        return argument
    if fail_first and (name, argument) == ("search", "Lumen"):
        return ""
    return FACTS.get((name, argument), "")


def replay(*, fail_first: bool = False, step_limit: int = 8) -> list[dict[str, Any]]:
    """A fixed policy for demonstrating state transitions; not generated CoT."""
    if step_limit < 1:
        raise ValueError("step_limit must be >= 1")
    trace: list[dict[str, Any]] = []
    plan = [
        ("search", "Lumen"),
        ("search", "Lumen 项目") if fail_first else None,
        ("lookup", "Aurora"),
    ]
    for action in filter(None, plan):
        if len([x for x in trace if x["kind"] == "action"]) >= step_limit:
            return trace + [{"kind": "stopped", "value": "step budget exhausted"}]
        name, arg = action
        trace.append({"kind": "thought", "value": "Retrieve a needed fictional record"})
        trace.append({"kind": "action", "value": f"{name}[{arg}]"})
        observation = tool(name, arg, fail_first=fail_first)
        trace.append({"kind": "observation", "value": observation or "(empty)"})
    has_team = any("Aurora" in x["value"] for x in trace if x["kind"] == "observation")
    has_owner = any("Lin" in x["value"] for x in trace if x["kind"] == "observation")
    if has_team and has_owner:
        return trace + [{"kind": "finish", "value": tool("finish", "Lin")}]
    return trace + [{"kind": "stopped", "value": "insufficient evidence"}]


if __name__ == "__main__":
    for state in replay(fail_first=True):
        print(state["kind"], state["value"])
