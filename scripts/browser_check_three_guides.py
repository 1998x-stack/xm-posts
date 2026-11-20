#!/usr/bin/env python3
"""Cross-article numerical, interaction and narrow-screen regression checks.

Runs against the actual published article source with Chromium, no network.
"""
from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "knn": ROOT / "posts/classical-ml/knn/index.html",
    "logistic-regression": ROOT / "posts/classical-ml/logistic-regression/index.html",
    "roc-auc": ROOT / "posts/evaluation/roc-auc/index.html",
}
WIDTHS = [1440, 768, 390, 360]


def check_knn(page):
    result = page.locator("#lab-result")
    assert "预测 B" in result.inner_text()
    page.locator('[data-query="3,5.3"]').click()
    assert "预测 B" in result.inner_text(), "3-NN majority should be B"
    page.locator('[data-weight="distance"]').click()
    assert "预测 A" in result.inner_text(), "inverse-distance voting should switch to A"
    assert page.locator("#knn-neighbor-rows tr").count() == 3
    assert page.locator("#knn-query-point").get_attribute("cy") == "61.5"
    assert page.locator('[data-weight="distance"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-k="1"]').click()
    assert page.locator("#knn-neighbor-rows tr").count() == 1


def check_logistic(page):
    before = page.locator("#lr-live-probability").inner_text()
    assert before == "0.7311"
    assert page.locator("#lr-loss-positive").inner_text() == "0.3133"
    assert page.locator("#lr-loss-negative").inner_text() == "1.3133"
    page.locator("#threshold").evaluate(
        "(el) => { el.value='0.9'; el.dispatchEvent(new Event('input', {bubbles:true})); }"
    )
    assert page.locator("#lr-live-probability").inner_text() == before, (
        "threshold must not change a fitted score/probability"
    )
    assert page.locator("#lr-live-decision").inner_text() == "负类"
    page.locator('[data-preset="reverse"]').click()
    assert page.locator("#lr-live-score").inner_text() == "-1.000"
    assert page.locator("#lr-live-probability").inner_text() == "0.2689"
    assert float(page.locator("#lr-probability-meter").evaluate("(el) => el.value")) < 0.3


def check_roc(page):
    assert page.locator("#roc-tp").inner_text() == "2"
    assert page.locator("#roc-fp").inner_text() == "1"
    page.locator('[data-thr=".96"]').click()
    assert page.locator("#roc-tp").inner_text() == "0"
    assert page.locator("#roc-fp").inner_text() == "0"
    assert float(page.locator("#roc-threshold-guide").get_attribute("x1")) == 673
    assert float(page.locator("#roc-live-point").get_attribute("cx")) == 109
    page.locator('[data-thr=".25"]').click()
    assert page.locator("#roc-tp").inner_text() == "4"
    assert page.locator("#roc-fp").inner_text() == "3"
    assert page.locator("#roc-tpr-percent").inner_text() == "100%"
    assert page.locator("#roc-fpr-percent").inner_text() == "75%"
    assert page.locator("#roc-result").inner_text().endswith("AUC=0.75（不变）。")
    assert page.locator('circle[data-score][stroke="#273f4e"]').count() == 7
    assert page.locator('[data-thr=".25"]').get_attribute("aria-pressed") == "true"


def main():
    executable = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    options = {"executable_path": str(executable)} if executable.exists() else {}
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"], **options)
        for slug, source in ARTICLES.items():
            html = source.read_text(encoding="utf-8")
            for width in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": 900})
                errors = []
                page.on("pageerror", lambda e, log=errors: log.append(str(e)))
                page.set_content(html, wait_until="load")
                metrics = page.evaluate(
                    "() => ({overflow: document.documentElement.scrollWidth > innerWidth+1,"
                    " h1: document.querySelectorAll('h1').length})"
                )
                assert not metrics["overflow"], f"{slug}@{width}: document overflow"
                assert metrics["h1"] == 1, f"{slug}: expected exactly one h1"
                if width == 1440:
                    {"knn": check_knn, "logistic-regression": check_logistic,
                     "roc-auc": check_roc}[slug](page)
                assert not errors, f"{slug}@{width}: page errors {errors}"
                results.append({"article": slug, "width": width, "pass": True})
                page.close()
        browser.close()
    print(json.dumps({"pass": True, "checks": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
