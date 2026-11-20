"""Tiny LoRA algebra and publishing-entry regression."""
from pathlib import Path
import runpy
import json
ROOT = Path(__file__).resolve().parents[1]

def test_lora_toy_executes():
    m = runpy.run_path(str(ROOT / "posts/training/lora/mini_lora.py"))
    assert m["low_rank_forward"](m["W0"], m["A"], m["B"], m["x"]) == [3.0, 10.0]
    assert m["matvec"](m["merged_weight"](m["W0"], m["A"], m["B"]), m["x"]) == [3.0, 10.0]

def test_lora_registered_for_training():
    posts=json.loads((ROOT / "content/posts.json").read_text(encoding="utf8"))
    entry=next(p for p in posts if p["slug"] == "lora")
    assert entry["category"] == "training" and entry["status"] == "published"
    article=(ROOT / "posts/training/lora/index.html").read_text(encoding="utf8")
    assert "Table 4" in article and "Table 5" in article and article.count("<svg") >= 6
