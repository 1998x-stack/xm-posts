import importlib.util
from pathlib import Path
SOURCE = Path(__file__).resolve().parents[1] / "posts/reasoning/self-consistency/mini_self_consistency.py"
spec = importlib.util.spec_from_file_location("mini_sc", SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_majority():
    assert mod.majority_vote(["The answer is 10", "The answer is 10", "The answer is 16"]) == ("10", {"10": 2, "16": 1})
    assert mod.extract_final_answer("答案是 1,200.00") == "1200"
    assert mod.extract_final_answer("The answer is -2.5") == "-2.5"

def test_uncertain_cases():
    assert mod.majority_vote(["The answer is 10", "The answer is 16"])[0] is None
    assert mod.majority_vote(["no canonical final answer"]) == (None, {})
    assert mod.majority_vote(["The answer is 7", "not parseable"])[1] == {"7": 1}
