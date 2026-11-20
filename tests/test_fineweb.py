"""FineWeb educational mechanics: deterministic regression checks, not paper reproduction."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "posts/datasets/fineweb"
spec = importlib.util.spec_from_file_location("mini_fineweb", SRC / "mini_fineweb.py")
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_fineweb_toy_math():
    mod.self_test()


def test_fineweb_sources_and_diagrams():
    notes = json.loads((SRC / "evidence.json").read_text(encoding="utf-8"))
    assert len(notes) >= 16
    assert {e["status"] for e in notes} <= {"verified","derived","illustrative","unverified"}
    assert all(e["source_url"].startswith("https://") and e["locator"] for e in notes)
    assert len(list((SRC / "assets").glob("*.svg"))) >= 6


def test_fineweb_explainer_content():
    html = (SRC / "index.html").read_text(encoding="utf-8")
    assert html.count("<h1") == 1
    assert html.count("<math display=") >= 3
    assert 'id="jaccard"' in html and 'data-threshold="3"' in html
    assert "FineWeb-Edu" in html and "2013-48" in html
