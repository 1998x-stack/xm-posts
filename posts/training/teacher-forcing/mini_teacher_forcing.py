"""Teacher forcing：无第三方依赖的确定性教学算例。

只演示输入右移、条件依赖及 NLL；不是 RNN/Transformer 的完整训练。
"""
from math import log
from typing import Sequence


def shifted_pairs(tokens: Sequence[str]) -> list[tuple[str, str]]:
    """tokens 含开头 BOS 与结尾 EOS；输出 (上一词输入, 下一词目标)。"""
    if len(tokens) < 3 or tokens[0] != "<bos>" or tokens[-1] != "<eos>":
        raise ValueError("sequence must start with <bos> and end with <eos>")
    return list(zip(tokens[:-1], tokens[1:]))


def token_cross_entropy(gold_probabilities: Sequence[float]) -> float:
    """平均逐 token 负对数似然，不能用 argmax 正确率代替。"""
    if not gold_probabilities or any(p <= 0 or p > 1 for p in gold_probabilities):
        raise ValueError("each correct-token probability must be in (0, 1]")
    return -sum(log(p) for p in gold_probabilities) / len(gold_probabilities)


def demo_rollouts() -> dict[str, list[str]]:
    """固定的教学转移表：同一个模型，不同输入造成不同后续轨迹。"""
    next_token = {"<bos>": "We", "I": "love", "We": "like", "love": "cats", "like": "dogs"}
    teacher_inputs = ["<bos>", "I", "love"]
    teacher_outputs = [next_token[token] for token in teacher_inputs]
    free_inputs = ["<bos>"]
    for _ in range(2):
        free_inputs.append(next_token[free_inputs[-1]])
    free_outputs = [next_token[token] for token in free_inputs]
    return {"teacher_inputs": teacher_inputs, "teacher_outputs": teacher_outputs,
            "free_inputs": free_inputs, "free_outputs": free_outputs}


def mixed_copy_probability(q: float) -> float:
    """Two-position toy: true prefix with probability q, else independent fair prefix."""
    if not 0 <= q <= 1:
        raise ValueError("q must be in [0, 1]")
    return (1 + q) / 2


def at_least_one_error(epsilon: float, steps: int) -> float:
    """Independent equal-risk toy, not a model of real text quality."""
    if not 0 <= epsilon <= 1 or steps < 0:
        raise ValueError("invalid probability or steps")
    return 1 - (1 - epsilon) ** steps


def masked_token_nll(probabilities: Sequence[float], mask: Sequence[bool]) -> float:
    if len(probabilities) != len(mask):
        raise ValueError("mask must align with targets")
    return token_cross_entropy([p for p, keep in zip(probabilities, mask) if keep])


if __name__ == "__main__":
    pairs = shifted_pairs(["<bos>", "我", "爱", "机器", "学习", "<eos>"])
    assert pairs == [("<bos>", "我"), ("我", "爱"), ("爱", "机器"),
                     ("机器", "学习"), ("学习", "<eos>")]
    assert abs(token_cross_entropy([0.8, 0.7, 0.6]) - 0.3635480) < 1e-6
    trajectories = demo_rollouts()
    assert trajectories["teacher_outputs"] == ["We", "love", "cats"]
    assert trajectories["free_outputs"] == ["We", "like", "dogs"]
    assert mixed_copy_probability(0) == 0.5
    assert mixed_copy_probability(0.5) == 0.75
    assert mixed_copy_probability(1) == 1
    assert abs(at_least_one_error(0.02, 50) - 0.6358303) < 1e-6
    assert at_least_one_error(0.5, 0) == 0
    assert abs(masked_token_nll([0.1, 0.8, 0.7, 0.6], [False, True, True, True]) - 0.3635480) < 1e-6
    try:
        masked_token_nll([0.5], [False])
    except ValueError:
        pass
    else:
        raise AssertionError("empty supervision must not silently divide by zero")
    assert abs(0.25 / 0.2 - 1.25) < 1e-12
    print("OK: shift, NLL, feedback, mixed prefixes, independent risk, mask, ratio")
