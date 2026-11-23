"""Source-level contract tests for the GroupLens draft article."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
POST_DIR = ROOT / "posts/recommender-systems/grouplens"
SVG_NS = "{http://www.w3.org/2000/svg}"


def test_grouplens_is_registered_as_a_draft_and_not_in_published_routes():
    categories = json.loads((ROOT / "content/categories.json").read_text(encoding="utf-8"))
    posts = json.loads((ROOT / "content/posts.json").read_text(encoding="utf-8"))
    routes = json.loads((ROOT / "content/reading_paths.json").read_text(encoding="utf-8"))
    category = next(item for item in categories if item["slug"] == "recommender-systems")
    assert category["topics"] == [{
        "slug": "collaborative-filtering",
        "title": "Collaborative Filtering & Neighborhood Models",
    }]
    post = next(item for item in posts if item["category"] == "recommender-systems" and item["slug"] == "grouplens")
    assert post["status"] == "draft"
    assert post["topic"] == "collaborative-filtering"
    assert post["cover"]["src"] == "assets/02-rating-matrix.svg"
    assert all("grouplens" not in route["posts"] for route in routes)


def test_article_semantics_math_and_local_figures():
    html = (POST_DIR / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    assert len(soup.select("h1")) == 1
    assert len(soup.select("h2")) >= 10
    assert soup.select_one("main#content article")
    assert soup.select_one('a.skip[href="#content"]')
    assert "@media print" in html
    assert "@media (prefers-reduced-motion: reduce)" in html
    assert "原创图解 · 单文件离线 HTML" not in html
    assert "参考 Colah 风格，非原文翻译" not in html

    math = soup.select("math")
    assert len(math) == 3
    assert all(item.get("aria-label") for item in math)
    assert all(len(item.find_all(recursive=False)) == 2 for item in soup.select("mfrac"))
    assert all(len(item.find_all(recursive=False)) == 2 for item in soup.select("munder"))
    assert not soup.select("svg math")

    figures = soup.select("figure img[src]")
    assert len(figures) == 8
    seen = set()
    for image in figures:
        relative = image["src"]
        assert relative.startswith("assets/") and relative.endswith(".svg")
        assert relative not in seen
        seen.add(relative)
        svg_path = POST_DIR / relative
        assert svg_path.is_file()
        root = ET.parse(svg_path).getroot()
        assert root.tag == SVG_NS + "svg"
        assert root.attrib.get("viewBox")
        assert root.attrib.get("role") == "img"
        assert root.find(SVG_NS + "title") is not None
        assert root.find(SVG_NS + "desc") is not None
        ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
        assert len(ids) == len(set(ids)), relative
        assert image.find_parent("figure").find("figcaption") is not None


def test_evidence_ledger_has_unique_traceable_claims():
    evidence = json.loads((POST_DIR / "evidence.json").read_text(encoding="utf-8"))
    ids = [item["id"] for item in evidence]
    assert len(ids) == len(set(ids))
    assert len(evidence) >= 15
    for item in evidence:
        assert item["claim"]
        assert item["kind"]
        assert item["source_url"].startswith("https://")
        assert item["locator"]
        assert item["status"] in {"verified", "derived", "illustrative", "unverified"}
