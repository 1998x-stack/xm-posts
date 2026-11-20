"""PDF button contract: built-only, one accessible download link, no body rewrite."""
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from render_pdfs import with_download_link, PDF_NAME, PRINT_CSS


def test_pdf_download_markup_is_layout_neutral_and_accessible():
    original = '<!doctype html><html><head><title>A</title></head><body class="paper"><main><h1>Understanding Q&amp;K</h1><p>保留 SVG、MathML 和正文</p></main></body></html>'
    result = with_download_link(original, "Understanding Q&K", "q-and-k")
    soup = BeautifulSoup(result, "html.parser")
    assert soup.select_one("main").decode_contents() == BeautifulSoup(original, "html.parser").select_one("main").decode_contents()
    assert len(soup.select("h1")) == 1
    button = soup.select_one('a[data-pdf-download]')
    assert button is not None
    assert button["href"] == PDF_NAME
    assert button["download"] == "xm-posts-q-and-k.pdf"
    assert "Understanding Q&K" in button["aria-label"]
    assert button.get_text(strip=True) == "下载 PDF"
    assert soup.select_one('link[rel="alternate"][type="application/pdf"]')["href"] == PDF_NAME
    assert soup.select_one('link[href="../../../assets/pdf-download.css"]')
    assert '<main><h1>Understanding Q&amp;K</h1>' in result


def test_pdf_download_markup_fails_closed_on_duplicate_or_bad_html():
    base = "<html><head></head><body><main><h1>T</h1></main></body></html>"
    once = with_download_link(base, "T", "t")
    with pytest.raises(ValueError, match="already exists"):
        with_download_link(once, "T", "t")
    with pytest.raises(ValueError, match="Missing or malformed"):
        with_download_link("<html><body></body></html>", "T", "t")


def test_pdf_print_rules_preserve_diagrams_but_hide_navigation():
    assert "figure" in PRINT_CSS and "break-inside" in PRINT_CSS
    assert "nav[aria-label" in PRINT_CSS
    assert "display: none !important" in PRINT_CSS
    assert "svg" in PRINT_CSS
