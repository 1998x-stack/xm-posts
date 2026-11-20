"""GQA toy reference: standard-library math, no GPU kernels or paper reproduction.

Ainslie et al. 2023: https://aclanthology.org/2023.emnlp-main.298/
Assumptions: uniform contiguous Q-to-KV groups; one query token;
each KV head owns a full key/value sequence; no attention masks or RoPE.
"""
from __future__ import annotations
from math import exp, sqrt, isclose


def group_index(i: int, num_q_heads: int, num_kv_heads: int) -> int:
    if not (0 <= i < num_q_heads and 1 <= num_kv_heads <= num_q_heads):
        raise ValueError("invalid head index/count")
    if num_q_heads % num_kv_heads:
        raise ValueError("the toy implementation requires divisible head counts")
    return i // (num_q_heads // num_kv_heads)


def stable_softmax(logits: list[float]) -> list[float]:
    if not logits:
        raise ValueError("empty key sequence")
    shift = max(logits)
    weights = [exp(x - shift) for x in logits]
    z = sum(weights)
    return [w / z for w in weights]


def dot(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("incompatible vector shapes")
    return sum(x * y for x, y in zip(a, b))


def attention_one(q: list[float], keys: list[list[float]],
                  values: list[list[float]]) -> list[float]:
    if not keys or len(keys) != len(values):
        raise ValueError("keys and values must have matching sequence lengths")
    d = len(q)
    if any(len(k) != d for k in keys):
        raise ValueError("key dimension differs from query dimension")
    vdim = len(values[0])
    if not vdim or any(len(v) != vdim for v in values):
        raise ValueError("inconsistent value dimensions")
    a = stable_softmax([dot(q, k) / sqrt(d) for k in keys])
    return [sum(a[t] * values[t][j] for t in range(len(a)))
            for j in range(vdim)]


def gqa_step(q_heads: list[list[float]],
             k_heads: list[list[list[float]]],
             v_heads: list[list[list[float]]]) -> list[list[float]]:
    """Query heads read K/V sequences belonging to their group (no copies)."""
    h, g = len(q_heads), len(k_heads)
    if not h or not g or len(v_heads) != g or h % g:
        raise ValueError("invalid H and G")
    return [attention_one(q, k_heads[group_index(i, h, g)],
                          v_heads[group_index(i, h, g)])
            for i, q in enumerate(q_heads)]


def mean_pool_projection_heads(heads: list[list[list[float]]],
                               groups: int) -> list[list[list[float]]]:
    """Groupwise, elementwise mean of old K or V projection matrices."""
    h = len(heads)
    if not h or not groups or h % groups:
        raise ValueError("invalid grouping")
    rows, cols = len(heads[0]), len(heads[0][0])
    if not rows or not cols or any(len(m) != rows or
        any(len(row) != cols for row in m) for m in heads):
        raise ValueError("ragged projection weights")
    r = h // groups
    return [[[sum(heads[j][a][b] for j in range(g*r, (g+1)*r)) / r
              for b in range(cols)] for a in range(rows)]
            for g in range(groups)]


def kv_cache_bytes(layers: int, batch: int, tokens: int,
                   kv_heads: int, head_dim: int, bytes_per_elem: int) -> int:
    if min(layers, batch, tokens, kv_heads, head_dim, bytes_per_elem) < 1:
        raise ValueError("all dimensions must be positive")
    return 2 * layers * batch * tokens * kv_heads * head_dim * bytes_per_elem


def self_test() -> None:
    qs = [[1.0, 0.0], [0.0, 1.0], [0.7, 0.3], [0.5, 0.5]]
    key_bank = [[[1.0, 0.0], [0.0, 1.0]],
                [[0.7, 0.4], [0.3, 1.0]],
                [[0.8, 0.3], [0.0, 1.0]],
                [[0.2, 0.3], [0.4, 0.7]]]
    val_bank = [[[1.0, 2.0], [3.0, 4.0]],
                [[4.0, 3.0], [2.0, 1.0]],
                [[1.0, 4.0], [2.0, 3.0]],
                [[3.0, 2.0], [1.0, 4.0]]]
    # G=H: the MHA endpoint has its own K/V sequence per Q head.
    mha = gqa_step(qs, key_bank, val_bank)
    for i in range(len(qs)):
        assert all(isclose(a, b, rel_tol=1e-12) for a, b in zip(
            mha[i], attention_one(qs[i], key_bank[i], val_bank[i])))
    # G=1: the MQA endpoint is shared across all queries.
    mqa = gqa_step(qs, [key_bank[0]], [val_bank[0]])
    for i in range(len(qs)):
        assert all(isclose(a, b, rel_tol=1e-12) for a, b in zip(
            mqa[i], attention_one(qs[i], key_bank[0], val_bank[0])))
    assert [group_index(i, 8, 2) for i in range(8)] == [0,0,0,0,1,1,1,1]
    old = [[[float(i)]] for i in [0,2,4,6]]
    assert mean_pool_projection_heads(old, 2) == [[[1.0]], [[5.0]]]
    mha_bytes = kv_cache_bytes(32,1,4096,32,128,2)
    gqa_bytes = kv_cache_bytes(32,1,4096,8,128,2)
    assert mha_bytes == 2*1024**3
    assert gqa_bytes == 512*1024**2
    assert mha_bytes // gqa_bytes == 4
    for G in [1,2,4,8,16,32]:
        assert kv_cache_bytes(32,1,4096,G,128,2) * 32 == mha_bytes * G


if __name__ == "__main__":
    self_test()
    print("GQA toy checks passed (math, grouping, memory; no GPU timing).")
