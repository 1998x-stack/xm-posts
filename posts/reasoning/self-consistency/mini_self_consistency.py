"""Pedagogical majority voting over pre-generated CoT samples (no model calls)."""
from collections import Counter
import re

PATTERN = re.compile(
    r"(?:The answer is|答案(?:是|为))\s*[:：]?\s*(-?\d+(?:,\d{3})*(?:\.\d+)?)",
    re.IGNORECASE,
)

def extract_final_answer(text: str) -> str | None:
    matches = PATTERN.findall(text)
    if not matches:
        return None
    value = float(matches[-1].replace(",", ""))
    return str(int(value)) if value.is_integer() else format(value, ".12g")

def majority_vote(outputs: list[str]) -> tuple[str | None, dict[str, int]]:
    votes = Counter(a for text in outputs if
                    (a := extract_final_answer(text)) is not None)
    if not votes:
        return None, {}
    best = max(votes.values())
    winners = [answer for answer, n in votes.items() if n == best]
    # Do not hide a tie behind a lexicographic ordering.
    return (winners[0] if len(winners) == 1 else None), dict(votes)

if __name__ == "__main__":
    samples = [
        "8+3+5=16. The answer is 16",
        "8-3+5=10. The answer is 10",
        "8+(-3+5)=10. The answer is 10",
    ]
    assert majority_vote(samples) == ("10", {"16": 1, "10": 2})
    assert extract_final_answer("答案是 1,200.00") == "1200"
    assert majority_vote(["The answer is 7", "The answer is 8"])[0] is None
    assert majority_vote(["unparseable"])[0] is None
    print("Self-consistency toy aggregation verified")
