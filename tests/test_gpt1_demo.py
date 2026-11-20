"""Deterministic checks for the GPT-1 explainer's educational causal attention."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "posts/training/gpt-1/causal_attention_demo.py"
spec = spec_from_file_location("gpt1_causal_demo", SOURCE)
demo = module_from_spec(spec)
spec.loader.exec_module(demo)

def test_demo_self_check():
    demo.check()

def test_single_token_attends_only_to_itself():
    assert demo.causal_attention([[0.0, 0.0]], [[8.0, 2.0]], [[7.0]]) == [[7.0]]

def test_future_values_cannot_change_prefix():
    q = [[1., 0.], [0., 1.], [1., 1.]]
    k = [[1., 0.], [0., 1.], [1., 1.]]
    v = [[5.], [6.], [7.]]
    before = demo.causal_attention(q, k, v)
    after = demo.causal_attention(q, k, [[5.], [6.], [-999.]])
    assert before[:2] == after[:2]
    assert before[2] != after[2]
