"""A deterministic teaching helper for trajectory-level safety evaluation.

This module aggregates already-human- or grader-labeled turns. It does not
classify natural-language content and is not a safety filter.
"""
def appropriate_response_rate(transcripts):
    if not transcripts:
        raise ValueError("need at least one transcript")
    passed = 0
    for turns in transcripts:
        if turns and all(turn.get("appropriate") is True for turn in turns):
            passed += 1
    return passed / len(transcripts)


if __name__ == "__main__":
    example = [
        [{"appropriate": True}, {"appropriate": True}],
        [{"appropriate": True}, {"appropriate": False}],
        [{"appropriate": True}],
    ]
    print(f"trajectory-level pass rate: {appropriate_response_rate(example):.3f}")
