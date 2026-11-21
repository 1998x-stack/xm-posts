"""Contract checks for the checkpoint optimization explainer and its evidence bundle."""
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "posts/training/checkpoint-optimization"
HTML = ARTICLE / "index.html"


def test_checkpoint_article_has_complete_local_visual_bundle():
    soup = BeautifulSoup(HTML.read_text(encoding="utf-8"), "html.parser")
    assert len(soup.select("h1")) == 1
    maths = soup.select("math")
    assert len(maths) >= 4
    assert all(math.get("aria-label") for math in maths)
    assert all(math.find_parent(class_="math-scroll").get("role") == "region" for math in maths)
    assert not soup.select("svg math")
    assert not re.search(r"\\(?:theta|tau|sqrt|times|approx)\b", HTML.read_text(encoding="utf-8"))
    diagrams = soup.select("figure svg.diagram")
    assert len(diagrams) >= 5
    for diagram in diagrams:
        assert diagram.get("viewbox")
        assert diagram.get("aria-labelledby")
        assert diagram.find("title") and diagram.find("desc")
        scroll_region = diagram.find_parent(class_="figure-scroll")
        assert scroll_region and scroll_region.get("role") == "region"
        assert scroll_region.get("tabindex") == "0"
    svg_files = sorted((ARTICLE / "assets").glob("*.svg"))
    assert len(svg_files) >= 5
    for svg in svg_files:
        source = svg.read_text(encoding="utf-8").strip()
        assert "<svg" in source and "viewBox=" in source
        assert "<title" in source and "<desc" in source
        if svg.name != "00-cover.svg":
            inline = source.replace("<svg ", '<svg class="diagram" ', 1)
            assert inline in HTML.read_text(encoding="utf-8")


def test_checkpoint_evidence_has_primary_and_framework_sources():
    evidence = json.loads((ARTICLE / "evidence.json").read_text(encoding="utf-8"))
    ids = {item["id"] for item in evidence}
    assert {
        "checkfreq-two-phase",
        "checkfreq-overhead",
        "young-daly-model",
        "pytorch-dcp",
        "pytorch-default-stager",
        "megatron-reshardable",
        "deepspeed-zero",
        "activation-checkpoint",
    } <= ids
    assert all(item["source_url"].startswith("https://") for item in evidence)
    assert all(item["status"] in {"verified", "derived"} for item in evidence)


def test_checkpoint_post_uses_existing_training_topic():
    posts = json.loads((ROOT / "content/posts.json").read_text(encoding="utf-8"))
    matches = [post for post in posts if post["slug"] == "checkpoint-optimization"]
    assert len(matches) == 1
    post = matches[0]
    assert post["category"] == "training"
    assert post["topic"] == "checkpointing"
    assert post["status"] in {"draft", "published"}
    assert post["cover"]["src"] == "assets/00-cover.svg"
    assert (ARTICLE / post["cover"]["src"]).is_file()
    assert 8 <= len(post["cover"]["caption"]) <= 80
