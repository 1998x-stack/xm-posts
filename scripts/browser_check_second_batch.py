#!/usr/bin/env python3
"""Check second learning batch: PCA, K-Means and GMM across four browser sizes.

This complements the full per-article smoke tests with causal numeric assertions.
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
    "pca": ROOT / "posts/classical-ml/pca/index.html",
    "k-means": ROOT / "posts/classical-ml/k-means/index.html",
    "gmm": ROOT / "posts/classical-ml/gmm/index.html",
}
SIZES = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def numeric_progress(page, selector):
    return float(page.locator(selector).evaluate("(e) => e.value"))


def assert_pca(page):
    assert page.locator("#pca-retained-percent").inner_text().endswith("%")
    page.locator("#axis-horizontal").click()
    horizontal = numeric_progress(page, "#pca-retained-meter")
    page.locator("#axis-vertical").click()
    vertical = numeric_progress(page, "#pca-retained-meter")
    assert horizontal > vertical, (horizontal, vertical)
    assert page.locator("#angle-readout").inner_text() == "90°"
    assert abs(vertical + numeric_progress(page, "#pca-lost-meter") - 1) < 1e-10
    page.locator("#optimize").click()
    optimum = numeric_progress(page, "#pca-retained-meter")
    assert optimum > horizontal, (optimum, horizontal)
    assert "理论最佳约" in page.locator("#demo-output").inner_text()
    page.locator("#toggle").click()
    assert page.locator("#toggle").get_attribute("aria-pressed") == "false"
    assert abs(optimum + numeric_progress(page, "#pca-lost-meter") - 1) < 1e-10


def assert_kmeans(page):
    rows = page.locator("#km-point-rows tr")
    assert rows.count() == 4
    assert page.locator("#km-j").inner_text() == "100.000"
    assert numeric_progress(page, "#km-objective-meter") == 100
    page.locator("#demo-next").click()
    assert page.locator("#km-j").inner_text() == "100.000"
    page.locator("#demo-next").click()
    assert page.locator("#km-j").inner_text() == "34.667"
    assert page.locator("#km-point-rows tr").nth(1).locator("td").last.inner_text() == "21.778"
    page.locator("#demo-next").click()
    assert page.locator("#km-j").inner_text() == "16.889"
    page.locator("#demo-prev").click()
    assert page.locator("#km-j").inner_text() == "34.667"
    page.locator("#demo-finish").click()
    assert page.locator("#km-j").inner_text() == "4.000"
    assert page.locator("#demo-next").is_disabled()
    assert page.locator("#km-total").inner_text() == "4.000"
    page.locator("#demo-reset").click()
    assert page.locator("#km-j").inner_text() == "100.000"
    assert page.locator("#demo-prev").is_disabled()


def assert_gmm(page):
    assert page.locator("#gmm-a").inner_text() == "50.0%"
    initial_density = page.locator("#gmm-density-a").inner_text()
    assert page.locator("#gmm-boundary-label").inner_text() == "x=0.00"
    page.locator("#gmm-prior").evaluate(
        "(e) => { e.value='0.8'; e.dispatchEvent(new Event('input', {bubbles:true})); }"
    )
    assert page.locator("#gmm-prior-label").inner_text() == "80%"
    assert page.locator("#gmm-a").inner_text() == "80.0%"
    assert page.locator("#gmm-density-a").inner_text() == initial_density, (
        "changing prior must not change Gaussian component density"
    )
    assert page.locator("#gmm-boundary-label").inner_text() == "x=0.40"
    assert float(page.locator("#gmm-boundary").get_attribute("x1")) > 377.5
    page.locator("#gmm-left-example").click()
    assert page.locator("#gmm-x-label").inner_text() == "-1.25"
    assert float(page.locator("#gmm-a").inner_text().replace("%", "")) > 95
    assert math.isclose(float(page.locator("#gmm-point").get_attribute("cx")), 261.875)
    page.locator("#gmm-reset").click()
    assert page.locator("#gmm-a").inner_text() == "50.0%"
    assert page.locator("#gmm-prior-label").inner_text() == "50%"
    assert page.locator("#gmm-boundary-label").inner_text() == "x=0.00"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "second-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    options = {"executable_path": str(executable)} if executable.exists() else {}
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"], **options)
        for slug, source in ARTICLES.items():
            html = source.read_text(encoding="utf-8")
            for width, height in SIZES:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                requests = []
                page.on("pageerror", lambda e, dest=errors: dest.append(str(e)))
                page.route("https?://**", lambda r, dest=requests: (dest.append(r.request.url), r.abort()))
                page.set_content(html, wait_until="load")
                metrics = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
                    return {
                        h1:document.querySelectorAll('h1').length,
                        width:document.documentElement.scrollWidth,
                        viewport:innerWidth,
                        duplicateIds: ids.length-new Set(ids).size,
                        brokenSvg:[...document.querySelectorAll('svg')]
                            .filter(s=>!s.getBoundingClientRect().width||!s.getBoundingClientRect().height).length
                    };
                }""")
                assert metrics["h1"] == 1 and metrics["duplicateIds"] == 0, (slug, width, metrics)
                assert metrics["width"] <= width + 1, (slug, width, metrics)
                assert metrics["brokenSvg"] == 0, (slug, width, metrics)
                if width == 1440:
                    {"pca": assert_pca, "k-means": assert_kmeans, "gmm": assert_gmm}[slug](page)
                assert not errors and not requests, (slug, width, errors, requests)
                results.append({"article": slug, "width": width, "pass": True})
                page.screenshot(path=str(args.output / f"{slug}-{width}.png"), full_page=False)
                page.close()
        browser.close()
    report = {"pass": True, "checks": results}
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
