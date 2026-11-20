"""Diagnose mobile overflow in WordPiece article (explicit Chromium QA)."""
from pathlib import Path

from playwright.sync_api import sync_playwright


ARTICLE = Path(__file__).resolve().parents[1] / "posts/foundations/wordpiece/index.html"


def test_wordpiece_narrow_mobile_document_width():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 360, "height": 800})
            page.goto(ARTICLE.as_uri())
            report = page.evaluate("""() => {
              const overflowing = Array.from(document.querySelectorAll('*')).map(el => {
                const rect = el.getBoundingClientRect();
                return {
                  tag: el.tagName.toLowerCase(),
                  id: el.id || '',
                  class: String(el.getAttribute('class') || '').slice(0,100),
                  right: Math.round(rect.right),
                  left: Math.round(rect.left),
                  width: Math.round(rect.width),
                  text: String(el.textContent || '').trim().slice(0,55),
                  parent: el.parentElement ? el.parentElement.tagName.toLowerCase() +
                    '.' + String(el.parentElement.className || '').slice(0,50) : ''
                };
              }).filter(x => x.right > innerWidth + 1 && x.width > 0 && x.tag !== 'svg' && !['rect', 'text', 'path', 'g', 'title', 'desc'].includes(x.tag));
              return {
                 innerWidth,
                 scrollWidth: document.documentElement.scrollWidth,
                 offenders: overflowing.slice(0,50)
              };
            }""")
            assert report["scrollWidth"] <= report["innerWidth"] + 1, (
                "document width=" + str(report["scrollWidth"]) + " at viewport " + str(report["innerWidth"]) +
                "; overflowing HTML elements: " + repr(report["offenders"][:12])
            )
        finally:
            browser.close()
