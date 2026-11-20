"""教学参考：多头缩放点积注意力与因果 Mask（不含 dropout）。

运行: python mini_attention.py
依赖: pip install torch
与 2017 Transformer 的核心注意力公式一致，但不是完整翻译系统。
"""
import math
import torch
from torch import nn


class MultiHeadAttention(nn.Module):
    def __init__(self, d_model: int = 512, heads: int = 8):
        super().__init__()
        if d_model % heads:
            raise ValueError("d_model must be divisible by heads")
        self.heads = heads
        self.d_head = d_model // heads
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)

    def _split(self, tensor: torch.Tensor) -> torch.Tensor:
        batch, length, _ = tensor.shape
        return tensor.reshape(batch, length, self.heads, self.d_head).transpose(1, 2)

    def forward(self, query, key, value, allowed=None):
        """query [B,Lq,D], key/value [B,Lk,D]

        allowed: 可选 bool mask，可广播为 [B,H,Lq,Lk]。
        此教学版本要求每个 Query 至少允许一个 Key，以免 softmax(-inf,...,-inf) 得 NaN。
        """
        q = self._split(self.q_proj(query))
        k = self._split(self.k_proj(key))
        v = self._split(self.v_proj(value))
        logits = (q @ k.transpose(-2, -1)) / math.sqrt(self.d_head)
        if allowed is not None:
            if allowed.dtype != torch.bool:
                raise TypeError("allowed must be a bool tensor")
            logits = logits.masked_fill(~allowed, float("-inf"))
        weights = torch.softmax(logits, dim=-1)
        context = weights @ v
        batch, _, length, _ = context.shape
        context = context.transpose(1, 2).contiguous().reshape(batch, length, -1)
        return self.out_proj(context), weights


def causal_mask(length, device=None):
    """形状 [1,1,L,L]，True 表示允许当前位置读取该 Key。"""
    return torch.ones(length, length, dtype=torch.bool, device=device).tril()[None, None]


if __name__ == "__main__":
    torch.manual_seed(7)
    attention = MultiHeadAttention(d_model=32, heads=4)
    x = torch.randn(2, 5, 32)
    output, weights = attention(x, x, x, allowed=causal_mask(5))
    assert output.shape == (2, 5, 32)
    assert weights.shape == (2, 4, 5, 5)
    assert torch.allclose(weights.sum(dim=-1), torch.ones(2, 4, 5), atol=1e-6)
    future = torch.triu(torch.ones(5, 5, dtype=torch.bool), diagonal=1)
    assert torch.all(weights[..., future] == 0)
    memory = torch.randn(2, 7, 32)
    cross, cross_weights = attention(x, memory, memory)
    assert cross.shape == (2, 5, 32)
    assert cross_weights.shape == (2, 4, 5, 7)
    print("PASS: causal self-attention & cross-attention shape/mask checks")
