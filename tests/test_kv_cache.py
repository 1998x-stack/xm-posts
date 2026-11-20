"""Deterministic toy attention/KV cache checks; no GPU or downloads required."""
import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "posts" / "inference" / "kv-cache" / "mini_kv_cache.py"
spec = importlib.util.spec_from_file_location("kv_example", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def test_cache_reuses_keys_without_changing_causal_outputs():
    for values in ([.25, -.6, 1.1, .8], [2.0], [-2.0, 0.0, 2.0]):
        old = module.baseline(values)
        new = module.cached(values)
        assert len(old) == len(new) == len(values)
        for oa, ob in zip(old, new):
            assert max(abs(a-b) for a,b in zip(oa,ob)) < 1e-12

def test_kv_bytes_heads_scale_and_zero_tokens():
    assert module.kv_bytes(32,1,4096,8,128,2) == 512 * 1024**2
    assert module.kv_bytes(32,1,4096,32,128,2) == 2 * 1024**3
    assert module.kv_bytes(32,1,0,8,128,2) == 0
    assert module.kv_bytes(32,1,4096,8,128,2) * 4 == module.kv_bytes(32,1,4096,32,128,2)
