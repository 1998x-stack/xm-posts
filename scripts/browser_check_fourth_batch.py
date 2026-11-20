#!/usr/bin/env python3
"""Fourth teaching pass browser QA: Naive Bayes, SVM and SGD.

Checks numerical updates, keyboard controls, semantic structure, mobile overflow,
live SVG behavior, and offline operation. Run after installing Playwright Chromium.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "naive-bayes": ROOT / "posts/classical-ml/naive-bayes/index.html",
    "svm": ROOT / "posts/classical-ml/svm/index.html",
    "sgd": ROOT / "posts/foundations/sgd/index.html",
}
WIDTHS = ((1440, 900), (768, 1024), (390, 844), (360, 800))


def check_naive_bayes(page) -> None:
    assert page.locator("#nb-evidence-rows tr").count() == 2
    assert "12.000 : 1" in page.locator("#nb-evidence-total").inner_text()
    assert "+1.386" in page.locator("#nb-evidence-rows").inner_text()
    page.locator('[data-query="free free meeting"]').click()
    assert page.locator("#nb-evidence-rows tr").count() == 2
    assert page.locator("#nb-evidence-rows tr").first.locator("td").nth(1).inner_text() == "2"
    assert "5.333 : 1" in page.locator("#nb-evidence-total").inner_text()
    assert "against" in (page.locator("#nb-evidence-rows tr").nth(1).locator("span").get_attribute("class") or "")
    page.locator("#alpha").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#alpha-value").inner_text() == "1.25"
    assert "推广后验" in page.locator("#nb-evidence-tip").inner_text()


def check_svm(page) -> None:
    assert "w = 0.5" in page.locator("#svm-c-candidates .best").inner_text()
    assert "0.225" in page.locator("#svm-c-result").inner_text()
    assert page.locator('.heat-cell[data-i="0"][data-j="2"] .heat-value').text_content() == "0.05"
    page.locator('.svm-c-btn[data-c="1"]').focus()
    page.keyboard.press("Enter")
    assert page.locator('.svm-c-btn[data-c="1"]').get_attribute("aria-pressed") == "true"
    assert "w = 1" in page.locator("#svm-c-result").inner_text()
    assert "0.500" in page.locator("#svm-c-result").inner_text()
    page.locator('.gamma-btn[data-gamma="0.15"]').click()
    assert page.locator('.heat-cell[data-i="0"][data-j="2"] .heat-value').text_content() == "0.55"
    assert page.locator('.gamma-btn[data-gamma="0.15"]').get_attribute("aria-pressed") == "true"


def check_sgd(page) -> None:
    assert "第 0 步" in page.locator("#sgd-step-count").inner_text()
    page.locator('[data-choice="one"]').click()
    assert "θ=-0.300" in page.locator("#sgd-step-count").inner_text()
    assert "θ=+0.200" in page.locator("#sgd-demo-output").inner_text()
    page.locator('[data-choice="all"]').focus()
    page.keyboard.press("Enter")
    assert "第 2 步" in page.locator("#sgd-step-count").inner_text()
    assert "θ=-0.070" in page.locator("#sgd-step-count").inner_text()
    assert len(page.locator("#sgd-path").get_attribute("points").split()) == 3
    assert page.locator("#sgd-history-list li").count() == 2
    page.locator("#sgd-reset").click()
    assert "第 0 步" in page.locator("#sgd-step-count").inner_text()
    assert len(page.locator("#sgd-path").get_attribute("points").split()) == 1
    assert page.locator("#sgd-history-list li").count() == 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/fourth-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    chromium = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    options = {"executable_path": str(chromium)} if chromium.exists() else {}
    checks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **options)
        for slug, source in ARTICLES.items():
            for width, height in WIDTHS:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors, network_requests = [], []
                page.on("pageerror", lambda error, dest=errors: dest.append(str(error)))
                page.route("https?://**", lambda route, dest=network_requests: (
                    dest.append(route.request.url), route.abort()
                ))
                page.goto(source.as_uri(), wait_until="load")
                status = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                    const links=[...document.querySelectorAll('a[href^="#"]')]
                        .map(e=>decodeURIComponent(e.hash.slice(1)));
                    return {
                        h1:document.querySelectorAll('h1').length,
                        main:!!document.querySelector('main'),
                        overflow:document.documentElement.scrollWidth-innerWidth,
                        duplicatedIds:ids.length-new Set(ids).size,
                        missingFragments:links.filter(id=>id&&!document.getElementById(id)),
                        invisibleSvg:[...document.querySelectorAll('svg')]
                            .filter(svg=>svg.getBoundingClientRect().width<=0
                                       ||svg.getBoundingClientRect().height<=0).length
                    };
                }""")
                assert status["h1"] == 1 and status["main"], (slug, width, status)
                assert status["overflow"] <= 1, (slug, width, status)
                assert status["duplicatedIds"] == 0, (slug, width, status)
                assert not status["missingFragments"] and not status["invisibleSvg"], (slug, width, status)
                if width in (1440, 360):
                    {"naive-bayes": check_naive_bayes,
                     "svm": check_svm, "sgd": check_sgd}[slug](page)
                assert not errors and not network_requests, (slug, width, errors, network_requests)
                page.screenshot(path=str(args.output / f"{slug}-{width}.png"), full_page=False)
                checks.append({"article": slug, "width": width, "passed": True})
                page.close()
        browser.close()
    report = {"passed": True, "checks": checks}
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
