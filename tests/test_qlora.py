"""Deterministic cross-checks for QLoRA pedagogical assets."""
from __future__ import annotations
from pathlib import Path
import importlib.util
import json
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "posts" / "training" / "qlora"

def test_qlora_numbered_evidence_and_figures():
    data = json.loads((POST / "evidence.json").read_text(encoding="utf-8"))
    ids = [entry["id"] for entry in data]
    assert len(ids) >= 12 and len(ids) == len(set(ids))
    assert all(entry.get("source_url") and entry.get("locator") for entry in data)
    soup = BeautifulSoup((POST / "index.html").read_text(encoding="utf-8"), "html.parser")
    ids = [element.get("id") for element in soup.select("[id]")]
    assert len(ids) == len(set(ids)), "Duplicate HTML ids in QLoRA article"
    assert soup.find(id="nf4") and soup.find(id="nf4-gb")
    assert len(soup.find_all("h1")) == 1
    assert len(soup.find_all("figure")) >= 6
    assert len(soup.find_all("svg")) == len(list((POST / "assets").glob("*.svg")))
    assert len(soup.find_all("math")) >= 3
    for fraction in soup.select("math mfrac"):
        assert len(fraction.find_all(recursive=False)) == 2, "Malformed MathML fraction"
    assert not soup.select("svg math"), "MathML cannot be nested in SVG"
    assert soup.find("select", id="scale") is not None
    assert len(soup.select("[data-shortcut]")) == 2
    assert len(soup.select("section[id]")) >= 12

def test_qlora_math_toy_runs():
    spec = importlib.util.spec_from_file_location("mini_qlora", POST / "mini_qlora.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    module.test()
