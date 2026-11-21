from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ARTICLE = (
    Path(__file__).resolve().parents[1]
    / "posts"
    / "training"
    / "reward-hacking"
    / "index.html"
)


def test_keyboard_focus_reaches_the_interactive_lab() -> None:
    launch_options: dict[str, object] = {"headless": True, "args": ["--no-sandbox"]}
    chromium_path = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    if chromium_path.exists():
        launch_options["executable_path"] = str(chromium_path)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_options)
        page = browser.new_page(viewport={"width": 390, "height": 844})
        page.set_content(ARTICLE.read_text(encoding="utf-8"), wait_until="load")

        focused_id = ""
        for _ in range(48):
            page.keyboard.press("Tab")
            focused_id = page.evaluate("document.activeElement.id")
            if focused_id == "alpha-range":
                break

        assert focused_id == "alpha-range", "Keyboard tab order must reach the optimization slider."
        focus_style = page.evaluate(
            """() => ({
                outlineStyle: getComputedStyle(document.activeElement).outlineStyle,
                outlineWidth: getComputedStyle(document.activeElement).outlineWidth
            })"""
        )
        assert focus_style["outlineStyle"] not in {"none", "hidden"}
        assert float(focus_style["outlineWidth"].replace("px", "")) >= 2.0

        assert page.locator("label[for='alpha-range']").count() == 1
        assert page.locator("#lab-status[aria-live='polite']").count() == 1
        initial = page.locator("#alpha-value").inner_text()
        page.keyboard.press("ArrowRight")
        assert page.locator("#alpha-value").inner_text() != initial

        browser.close()
