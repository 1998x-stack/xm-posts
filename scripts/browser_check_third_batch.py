#!/usr/bin/env python3
"""Third batch browser QA: regression, decision trees, XGBoost.

Asserts pedagogical arithmetic, keyboard access, live SVG changes and 4 viewport layouts.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "linear-regression": ROOT / "posts/classical-ml/linear-regression/index.html",
    "decision-tree": ROOT / "posts/classical-ml/decision-tree/index.html",
    "xgboost": ROOT / "posts/classical-ml/xgboost/index.html",
}
WIDTHS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def set_slider(page, selector: str, value: str) -> None:
    page.locator(selector).evaluate(
        "(el, v) => { el.value=v; el.dispatchEvent(new Event('input', {bubbles:true})); }",
        value,
    )


def assert_regression(page) -> None:
    assert page.locator("#lr-live-rows tr").count() == 4
    assert page.locator("#lr-rss-total").inner_text() == "0.7000"
    assert page.locator("#lr-live-rows tr").nth(2).locator("td").last.inner_text() == "0.4900"
    assert "R² = 0.8526" in page.locator("#live-readout").inner_text()
    page.locator('[data-fit="mean"]').click()
    assert page.locator("#lr-rss-total").inner_text() == "4.7500"
    assert "R² = 0.0000" in page.locator("#live-readout").inner_text()
    assert page.locator('[data-fit="mean"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-fit="steep"]').click()
    assert page.locator("#lr-rss-total").inner_text() == "2.5000"
    assert "少 2.2500" in page.locator("#lr-compare-note").inner_text()
    page.locator('[data-fit="ols"]').click()
    assert page.locator("#lr-rss-total").inner_text() == "0.7000"
    before = page.locator("#lr-live-rows tr").nth(1).locator("td").nth(1).inner_text()
    page.locator("#slope").focus()
    page.keyboard.press("ArrowRight")
    after = page.locator("#lr-live-rows tr").nth(1).locator("td").nth(1).inner_text()
    assert before != after, (before, after)
    set_slider(page, "#slope", "0.9")
    assert page.locator('[data-fit="ols"]').get_attribute("aria-pressed") == "true"


def assert_tree(page) -> None:
    assert page.locator("#dt-impurity").inner_text() == "0.1875"
    assert page.locator("#dt-gain").inner_text() == "0.2813"
    assert page.locator("#dt-live-threshold").text_content() == "t = 4.5"
    x0 = float(page.locator("#dt-threshold-line").get_attribute("x1"))
    page.locator('[data-t="2.5"]').click()
    assert page.locator("#dt-impurity").inner_text() == "0.2083"
    assert page.locator("#dt-left-detail").text_content().startswith("0 正 / 2 负")
    x1 = float(page.locator("#dt-threshold-line").get_attribute("x1"))
    assert x1 < x0
    page.locator('[data-t="5.5"]').click()
    assert page.locator("#dt-impurity").inner_text() == "0.3000"
    page.locator("#dt-best").click()
    assert page.locator("#threshold-value").inner_text() == "4.5"
    assert page.locator("#dt-impurity").inner_text() == "0.1875"
    assert "7 个候选中最佳" in page.locator("#demo-result").inner_text()
    page.locator("#threshold-range").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#threshold-value").inner_text() == "5.5"
    assert page.locator("#dt-live-threshold").text_content() == "t = 5.5"


def assert_xgboost(page) -> None:
    assert page.locator("#x-gain").inner_text() == "+0.2333"
    assert page.locator("#x-left").inner_text() == "−0.3333"
    assert page.locator("#x-right").inner_text() == "+0.3333"
    assert page.locator("#x-sample-rows tr").count() == 4
    assert page.locator("#x-raw-gain").inner_text() == "+0.3333"
    default_line = float(page.locator("#xgb-cut-line").get_attribute("x1"))
    page.locator('[data-cut="1"]').click()
    assert page.locator("#x-gain").inner_text() == "−0.0063"
    assert page.locator("#x-left").inner_text() == "−0.2500"
    assert float(page.locator("#xgb-cut-line").get_attribute("x1")) < default_line
    page.locator('[data-cut="2"]').click()
    before = page.locator("#x-left").inner_text()
    set_slider(page, "#x-gamma", "0.4")
    assert page.locator("#x-gain").inner_text() == "−0.0667"
    assert page.locator("#x-left").inner_text() == before, (
        "Changing gamma cannot alter fixed-structure leaf weight"
    )
    assert "保留父节点" in page.locator("#x-status").inner_text()
    set_slider(page, "#x-gamma", "0.1")
    set_slider(page, "#x-lambda", "5")
    assert page.locator("#x-left").inner_text() == "−0.1429"
    assert page.locator("#x-gain").inner_text() == "+0.0429"
    page.locator("#x-lambda").focus()
    page.keyboard.press("ArrowLeft")
    assert page.locator("#x-lambda-label").inner_text() == "4.75"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "third-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    options = {"executable_path": str(executable)} if executable.exists() else {}
    checks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **options)
        for slug, source in ARTICLES.items():
            for width, height in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                requests = []
                page.on("pageerror", lambda e, dest=errors: dest.append(str(e)))
                page.route("https?://**", lambda route, dest=requests: (
                    dest.append(route.request.url), route.abort()
                ))
                page.goto(source.as_uri(), wait_until="load")
                status = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                    const links=[...document.querySelectorAll('a[href^="#"]')].map(e=>e.hash.slice(1));
                    return {
                        h1:document.querySelectorAll('h1').length,
                        hasMain:!!document.querySelector('main'),
                        overflow:document.documentElement.scrollWidth-innerWidth,
                        duplicatedIds:ids.length-new Set(ids).size,
                        missingFragments:links.filter(v=>v&&!document.getElementById(decodeURIComponent(v))),
                        invisibleSvg:[...document.querySelectorAll('svg')]
                            .filter(e=>e.getBoundingClientRect().width<=0
                                    ||e.getBoundingClientRect().height<=0).length
                    };
                }""")
                assert status["h1"] == 1 and status["hasMain"], (slug, width, status)
                assert status["overflow"] <= 1, (slug, width, status)
                assert status["duplicatedIds"] == 0 and not status["missingFragments"], (slug, width, status)
                assert status["invisibleSvg"] == 0, (slug, width, status)
                if width in (1440, 360):
                    {"linear-regression": assert_regression,
                     "decision-tree": assert_tree,
                     "xgboost": assert_xgboost}[slug](page)
                assert not errors and not requests, (slug, width, errors, requests)
                page.screenshot(path=str(args.output / f"{slug}-{width}.png"), full_page=False)
                checks.append({"article": slug, "width": width, "pass": True})
                page.close()
        browser.close()
    (args.output / "report.json").write_text(
        json.dumps({"pass": True, "checks": checks}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"pass": True, "checks": checks}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
