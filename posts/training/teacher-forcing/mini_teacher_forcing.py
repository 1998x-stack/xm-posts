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


if __name__ == "__main__":
    pairs = shifted_pairs(["<bos>", "我", "爱", "机器", "学习", "<eos>"])
    assert pairs == [("<bos>", "我"), ("我", "爱"), ("爱", "机器"),
                     ("机器", "学习"), ("学习", "<eos>")]
    assert abs(token_cross_entropy([0.8, 0.7, 0.6]) - 0.3635494) < 1e-6
    trajectories = demo_rollouts()
    assert trajectories["teacher_outputs"] == ["We", "love", "cats"]
    assert trajectories["free_outputs"] == ["We", "like", "dogs"]
    print("OK: shift, mean NLL, distinct training/inference feedback")
