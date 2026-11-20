"""Tiny, deterministic ACI guardrail teaching example. Not the SWE-agent code."""
import ast

def guarded_edit(current: str, proposal: str) -> tuple[str, str]:
    if not isinstance(current, str) or not isinstance(proposal, str):
        raise TypeError("source must be text")
    try:
        ast.parse(proposal)
    except SyntaxError:
        return current, "rejected"
    return proposal, "applied"

def demo():
    old = "def mean(xs):\n    return sum(xs)\n"
    bad = "def mean(xs):\n    return sum(xs) /\n"
    good = "def mean(xs):\n    return sum(xs) / len(xs)\n"
    retained, status = guarded_edit(old, bad)
    assert retained == old and status == "rejected"
    updated, status = guarded_edit(retained, good)
    assert updated == good and status == "applied"
    return updated

if __name__ == "__main__":
    print(demo())
