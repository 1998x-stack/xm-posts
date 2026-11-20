"""Regression tests for typography/print contracts in standalone paper posts."""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import data
from validate_site import check_article_layout


def test_every_published_article_has_valid_layout_contract():
    _, posts = data(ROOT)
    for post in posts:
        if post["status"] != "published":
            continue
        path = ROOT / "posts" / post["category"] / post["slug"] / "index.html"
        check_article_layout(path.read_text(encoding="utf-8"), str(path.relative_to(ROOT)))


MINIMAL = """<!DOCTYPE html><html lang="zh-CN"><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>@media print{body{color:black}}@media(prefers-reduced-motion:reduce){*{animation:none}}</style>
</head><body><main><h1>Title</h1><h2>Section</h2><h3>Widget</h3></main></body></html>"""


@pytest.mark.parametrize("broken", [
    MINIMAL.replace("<!DOCTYPE html>", "<!DOCTYPE html><!DOCTYPE html>"),
    MINIMAL.replace("<h3>Widget</h3>", "<h4>Widget</h4>"),
    MINIMAL.replace("@media print", "@media(print)"),
    MINIMAL.replace("@media(prefers-reduced-motion:reduce)", "@media screen"),
])
def test_layout_contract_rejects_invalid_html(broken):
    with pytest.raises(AssertionError):
        check_article_layout(broken, "fixture.html")


def test_layout_contract_accepts_valid_html():
    check_article_layout(MINIMAL, "fixture.html")
