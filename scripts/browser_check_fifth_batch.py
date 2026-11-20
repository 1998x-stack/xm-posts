#!/usr/bin/env python3
"""Fifth visual teaching batch: CNN -> AlexNet -> MobileNet.

Run real Chromium checks across laptop/tablet/mobile, including keyboard controls,
reactive SVG values, exact arithmetic, offline behavior and page layout.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "cnn": ROOT / "posts/architectures/cnn/index.html",
    "alexnet": ROOT / "posts/architectures/alexnet/index.html",
    "mobilenet": ROOT / "posts/architectures/mobilenet/index.html",
}
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def set_range(page, selector: str, value: str) -> None:
    page.locator(selector).evaluate(
        "(el,v) => { el.value=v; el.dispatchEvent(new Event('input',{bubbles:true})); }",
        value,
    )


def assert_cnn(page) -> None:
    assert page.locator("#cnn-product-rows tr").count() == 9
    assert page.locator("#cnn-live-map-cells rect").count() == 9
    assert page.locator("#cnn-live-map-cells text").count() == 9
    assert "点积 = −1" in page.locator("#toy-result").inner_text()
    assert "九次" not in page.locator("#cnn-sum-note").inner_text()  # actual numeric terms, not prose
    page.locator('[data-cnn-output="1,1"]').click()
    assert "点积 = 2" in page.locator("#toy-result").inner_text()
    assert page.locator("#cnn-live-dot").text_content() == "输出值 2"
    assert page.locator("#cnn-product-rows tr").count() == 9
    assert page.locator('[data-cnn-output="1,1"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#pixel-grid span.hot").count() == 9
    page.locator('[data-pos="0,1"]').click()
    assert "点积 = 0" in page.locator("#toy-result").inner_text()
    assert page.locator('[data-cnn-output="0,1"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-cnn-output="2,2"]').focus()
    page.keyboard.press("Enter")
    assert "点积 = −1" in page.locator("#toy-result").inner_text()
    assert page.locator("#cnn-live-position").text_content() == "当前窗口 (2,2)"


def assert_alexnet(page) -> None:
    assert "输出 55×55×96" in page.locator("#conv-readout").inner_text()
    assert "有效宽度 227" in page.locator("#alex-conv-explain").inner_text()
    assert page.locator("#alex-seen").inner_text() == "48"
    assert page.locator("#alex-weights").inner_text() == "307,200"
    assert page.locator("#alex-macs").inner_text() == "223,948,800"
    assert page.locator("#alex-cell-ab").text_content() == "不连接"
    page.locator('[data-mode="224"]').click()
    assert "H=224, P=2" in page.locator("#conv-readout").inner_text()
    assert "输出 55×55×96" in page.locator("#conv-readout").inner_text()
    assert "有效宽度 228" in page.locator("#alex-conv-explain").inner_text()
    assert page.locator('[data-mode="224"]').get_attribute("aria-pressed") == "true"
    page.locator('[data-alex-groups="1"]').click()
    assert page.locator("#alex-seen").inner_text() == "96"
    assert page.locator("#alex-weights").inner_text() == "614,400"
    assert page.locator("#alex-macs").inner_text() == "447,897,600"
    assert page.locator("#alex-cell-ab").text_content() == "连接"
    assert page.locator("#alex-cell-ba").text_content() == "连接"
    page.locator('[data-alex-groups="2"]').focus()
    page.keyboard.press("Enter")
    assert page.locator("#alex-weights").inner_text() == "307,200"
    assert page.locator("#alex-cell-ab").text_content() == "不连接"


def assert_mobilenet(page) -> None:
    assert page.locator("#mb-dw-macs").inner_text() == "903,168"
    assert page.locator("#mb-pw-macs").inner_text() == "6,422,528"
    assert page.locator("#mb-full-macs").inner_text() == "57,802,752"
    assert page.locator("#mb-ratio").inner_text() == "12.7%"
    assert abs(float(page.locator("#mb-relative").evaluate("(e)=>e.value")) - 7325696/57802752) < 1e-10
    default_width = float(page.locator("#mb-dw-bar").get_attribute("width"))
    page.locator('[data-mode="detail"]').click()
    assert "903,168" in page.locator("#mode-output").inner_text()
    assert page.locator('[data-mode="detail"]').get_attribute("aria-pressed") == "true"
    set_range(page, "#alpha", "0.5")
    set_range(page, "#rho", "0.5")
    assert page.locator("#mb-dw-macs").inner_text() == "112,896"
    assert page.locator("#mb-pw-macs").inner_text() == "401,408"
    assert page.locator("#mb-full-macs").inner_text() == "3,612,672"
    assert page.locator("#mb-ratio").inner_text() == "14.2%"
    assert float(page.locator("#mb-dw-bar").get_attribute("width")) > default_width, (
        "under a current full-layer scale, the relative DW share rises as N decreases"
    )
    page.locator("#rho").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#rho-out").inner_text() == "0.625"
    set_range(page, "#rho", "1")
    set_range(page, "#alpha", "1")
    assert page.locator("#mb-ratio").inner_text() == "12.7%"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "fifth-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    opts = {"executable_path": str(executable)} if executable.exists() else {}
    checks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **opts)
        for slug, source in ARTICLES.items():
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors, remote = [], []
                page.on("pageerror", lambda e, dest=errors: dest.append(str(e)))
                page.route("https?://**", lambda route, dest=remote: (
                    dest.append(route.request.url), route.abort()
                ))
                page.goto(source.as_uri(), wait_until="load")
                audit = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
                    const fragments=[...document.querySelectorAll('a[href^="#"]')]
                        .map(a=>decodeURIComponent(a.hash.slice(1)));
                    return {
                        h1:document.querySelectorAll('h1').length,
                        main:!!document.querySelector('main'),
                        overflow:document.documentElement.scrollWidth - innerWidth,
                        duplicateIds:ids.length-new Set(ids).size,
                        badFragments:fragments.filter(id=>id&&!document.getElementById(id)),
                        zeroSizeSvg:[...document.querySelectorAll('svg')]
                            .filter(e=>!e.getBoundingClientRect().width || !e.getBoundingClientRect().height).length
                    };
                }""")
                assert audit["h1"] == 1 and audit["main"], (slug, width, audit)
                assert audit["duplicateIds"] == 0 and not audit["badFragments"], (slug, width, audit)
                assert audit["overflow"] <= 1 and audit["zeroSizeSvg"] == 0, (slug, width, audit)
                if width in (1440, 360):
                    {"cnn": assert_cnn, "alexnet": assert_alexnet,
                     "mobilenet": assert_mobilenet}[slug](page)
                assert not errors and not remote, (slug, width, errors, remote)
                page.screenshot(path=str(args.output / f"{slug}-{width}.png"), full_page=False)
                checks.append({"article": slug, "width": width, "pass": True})
                page.close()
        browser.close()
    result = {"pass": True, "checks": checks}
    (args.output / "report.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
