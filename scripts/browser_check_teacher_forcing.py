#!/usr/bin/env python3
"""Teacher Forcing: real browser check at 1440/768/390/360px and both interactions."""
from pathlib import Path
import argparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "posts/training/teacher-forcing/index.html"


def check(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for width in (1440, 768, 390, 360):
            page.set_viewport_size({"width": width, "height": 900})
            page.goto(HTML.resolve().as_uri(), wait_until="load")
            assert page.locator("h1").count() == 1
            assert page.locator("figure img").count() == 4
            images = page.locator("figure img").evaluate_all(
                "(nodes) => nodes.map(i => ({loaded:i.complete && i.naturalWidth > 0, src:i.getAttribute('src')}))"
            )
            assert all(i["loaded"] for i in images), images
            assert page.locator("math[display='block']").count() >= 3
            maths = page.locator("math").evaluate_all(
                "(nodes) => nodes.every(n => n.namespaceURI === 'http://www.w3.org/1998/Math/MathML' && n.getBoundingClientRect().height > 0)"
            )
            assert maths, "MathML did not render correctly"
            widths = page.evaluate("({scroll:document.documentElement.scrollWidth,viewport:window.innerWidth})")
            assert widths["scroll"] <= widths["viewport"] + 1, f"{width}: {widths}"
            page.screenshot(path=str(out / f"teacher-forcing-{width}.png"), full_page=True)
        page.locator('[data-mode="free"]').click()
        assert page.locator('[data-mode="free"]').get_attribute("aria-pressed") == "true"
        page.locator("#step").evaluate(
            "(el) => { el.value = '3'; el.dispatchEvent(new Event('input', {bubbles:true})); }"
        )
        assert "模型输入：like" in page.locator("#rollout-output").inner_text()
        assert "本步预测：dogs" in page.locator("#rollout-output").inner_text()
        page.locator('[data-mode="teacher"]').click()
        assert "模型输入：love" in page.locator("#rollout-output").inner_text()
        assert "本步预测：cats" in page.locator("#rollout-output").inner_text()
        page.locator("#prob").evaluate(
            "(el) => { el.value = '0.1'; el.dispatchEvent(new Event('input', {bubbles:true})); }"
        )
        assert "1.01218" in page.locator("#loss-output").inner_text()
        page.emulate_media(media="print")
        assert page.locator("h1").is_visible()
        assert page.locator("figure img").first.is_visible()
        browser.close()
    print("TEACHER FORCING BROWSER QA OK: 4 viewports, SVG, MathML, interactivity, print")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/teacher-forcing")
    args = parser.parse_args()
    check(args.output)
