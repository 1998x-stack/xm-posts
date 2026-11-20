"""Minimal causal self-attention cache: pure Python, one head, one layer."""
from math import exp, sqrt, isclose

def softmax(xs):
    offset = max(xs)
    a = [exp(x - offset) for x in xs]
    return [x / sum(a) for x in a]

def attention(q, keys, values):
    # q,k are vectors, here with head_dim=1; values are two-dimensional.
    logits = [q * k / sqrt(1) for k in keys]
    weights = softmax(logits)
    return tuple(sum(weights[i] * values[i][j]
                     for i in range(len(keys))) for j in range(2))

def baseline(tokens):
    out = []
    for t in range(len(tokens)):
        keys = [x for x in tokens[:t+1]]  # full recompute, for illustration
        vals = [(x, -x) for x in tokens[:t+1]]
        out.append(attention(tokens[t], keys, vals))
    return out

def cached(tokens):
    keys, vals, out = [], [], []
    for x in tokens:
        keys.append(x)
        vals.append((x, -x))
        out.append(attention(x, keys, vals))
    return out

def kv_bytes(layers, batch, tokens, kv_heads, head_dim, bytes_per_elem):
    return 2 * layers * batch * tokens * kv_heads * head_dim * bytes_per_elem

if __name__ == "__main__":
    samples = [0.25, -0.6, 1.1, 0.8]
    a, b = baseline(samples), cached(samples)
    assert len(a) == len(b) == 4
    assert all(isclose(u, v, rel_tol=1e-12, abs_tol=1e-12)
               for left, right in zip(a, b)
               for u, v in zip(left, right))
    assert kv_bytes(32, 1, 4096, 8, 128, 2) == 536870912
    assert kv_bytes(32, 1, 4096, 32, 128, 2) == 2147483648
    print("PASS: cached outputs equal baseline; cache bytes verified.")
