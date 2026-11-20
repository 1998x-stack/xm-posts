#!/usr/bin/env python3
"""Deterministic teaching protocol for standard vs few-shot CoT prompts.

No language model is called; results are not a replication of Wei et al. (2022).
Usage: python posts/reasoning/chain-of-thought/mini_cot.py
"""
from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Example:
    question: str
    rationale: str
    answer: str

EXAMPLES = (
    Example("4 bags, 3 items each, plus 2", "4*3=12; 12+2=14", "14"),
    Example("23 items, remove 20, add 6", "23-20=3; 3+6=9", "9"),
)

def format_prompt(examples: tuple[Example, ...], question: str, cot: bool) -> str:
    if not examples or not question.strip():
        raise ValueError("Need nonempty demonstrations and test question")
    blocks = []
    for ex in examples:
        if not all((ex.question.strip(), ex.rationale.strip(), ex.answer.strip())):
            raise ValueError("Incomplete example")
        answer = f"{ex.rationale}. Answer: {ex.answer}" if cot else ex.answer
        blocks.append(f"Q: {ex.question}\nA: {answer}")
    blocks.append(f"Q: {question}\nA:")
    return "\n\n".join(blocks)

def extract_answer(text: str) -> str | None:
    matches = re.findall(r"(?:Answer|答案)\s*[:：]\s*([-+]?\d+(?:\.\d+)?)", text, re.I)
    return matches[-1] if matches else None

def self_test() -> None:
    question = "19 apples, give away 4 and receive 3"
    standard = format_prompt(EXAMPLES, question, cot=False)
    cot = format_prompt(EXAMPLES, question, cot=True)
    assert "4*3=12" not in standard
    assert "4*3=12" in cot
    assert cot.count("Q:") == len(EXAMPLES) + 1
    assert standard.split("Q:")[-1] == cot.split("Q:")[-1]
    assert extract_answer("Step 1: 19-4=15. Answer: 18") == "18"
    assert extract_answer("no output marker") is None
    try:
        format_prompt((), question, True)
    except ValueError:
        pass
    else:
        raise AssertionError("empty demonstrations should fail")

if __name__ == "__main__":
    self_test()
    print("Prompt structure and parser: assertions passed; no model invoked.")
