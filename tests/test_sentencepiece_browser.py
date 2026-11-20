"""Chromium interaction and MathML regression for the SentencePiece article."""
from pathlib import Path
from playwright.sync_api import sync_playwright

ARTICLE = Path(__file__).resolve().parents[1] / "posts/foundations/sentencepiece/index.html"
MATH_NS = "http://www.w3.org/1998/Math/MathML"


def test_sentencepiece_browser_keyboard_and_mobile():
    source = ARTICLE.read_text(encoding="utf-8")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        try:
            for width in (1440, 768, 390, 360):
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors = []
                page.on("pageerror", lambda exc: errors.append(str(exc)))
                page.set_content(source, wait_until="load")
                result = page.evaluate("""() => ({
                    overflow: document.documentElement.scrollWidth > innerWidth + 1,
                    h1: document.querySelectorAll('h1').length,
                    figures: document.querySelectorAll('figure svg').length,
                    math: [...document.querySelectorAll('math')].map(x => ({
                        namespace: x.namespaceURI,
                        width: x.getBoundingClientRect().width,
                        height: x.getBoundingClientRect().height
                    }))
                })""")
                assert not result["overflow"], f"horizontal page overflow at {width}px"
                assert result["h1"] == 1
                assert result["figures"] == 5
                assert len(result["math"]) == 4
                assert all(x["namespace"] == MATH_NS and x["width"] > 1 and x["height"] > 1
                           for x in result["math"])
                assert not errors
                if width == 1440:
                    before = float(page.locator("#v0").inner_text().strip("%"))
                    slider = page.locator("#alpha")
                    slider.focus()
                    page.keyboard.press("End")
                    assert page.locator("#alpha-value").inner_text() == "3.0"
                    after = float(page.locator("#v0").inner_text().strip("%"))
                    assert after > before
                    total = sum(float(page.locator(f"#v{i}").inner_text().strip("%")) for i in range(3))
                    assert abs(total - 100.0) < 0.03
                page.close()
        finally:
            browser.close()
