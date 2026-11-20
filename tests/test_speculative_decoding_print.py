"""Regression guard for the Speculative Decoding MathML print layout (issue #117).

This is a source-level guard, not a substitute for visual PDF inspection.
"""
from pathlib import Path

ARTICLE = Path(__file__).resolve().parents[1] / "posts/inference/speculative-decoding/index.html"


def test_speculative_decoding_print_mathml_is_page_safe():
    html = ARTICLE.read_text(encoding="utf-8")
    assert html.count('<div class="mathbox math-scroll"') == 5
    assert "@media print{" in html
    print_css = html.split("@media print{", 1)[1].split("</style>", 1)[0]
    assert ".figure,.tile,.lab,.mathbox{break-inside:avoid;page-break-inside:avoid}" in print_css
    assert ".mathbox math{display:none!important}" in print_css
    assert ".mathbox::after{content:attr(data-print-formula)" in print_css
    assert html.count('data-print-formula="') == 5
    assert "overflow-wrap:anywhere" in print_css
