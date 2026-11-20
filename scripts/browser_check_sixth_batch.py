#!/usr/bin/env python3
"""Sixth batch real-browser QA for Weight Decay, Adam and AdamW visual labs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "weight-decay": ROOT / "posts/foundations/weight-decay/index.html",
    "adam": ROOT / "posts/foundations/adam/index.html",
    "adamw": ROOT / "posts/foundations/adamw/index.html",
}
VIEWPORTS = ((1440, 900), (768, 1024), (390, 844), (360, 800))


def set_slider(page, css: str, value: str) -> None:
    page.locator(css).evaluate(
        "(el, val)=>{el.value=val; el.dispatchEvent(new Event('input', {bubbles:true}));}",
        value,
    )


def check_decay(page) -> None:
    assert page.locator("#factor").inner_text() == "0.9800"
    assert page.locator("#retention").inner_text() == "36.42%"
    assert page.locator("#wd-constant-final").inner_text() == "36.42%"
    assert page.locator("#wd-scheduled-final").inner_text() == "59.84%"
    assert page.locator("#wd-step-rows tr").count() == 4
    assert page.locator("#wd-step-rows tr").last.locator("td").last.inner_text() == "0.598416"
    constant = page.locator("#wd-constant-path").get_attribute("d")
    scheduled = page.locator("#wd-schedule-path").get_attribute("d")
    assert constant != scheduled
    set_slider(page, "#steps", "1")
    assert page.locator("#retention").inner_text() == "98.00%"
    assert page.locator("#wd-scheduled-final").inner_text() == "98.00%"
    set_slider(page, "#steps", "50")
    set_slider(page, "#wd", "0")
    assert page.locator("#retention").inner_text() == "100.00%"
    assert page.locator("#wd-scheduled-final").inner_text() == "100.00%"
    page.locator("#reset").click()
    assert page.locator("#retention").inner_text() == "36.42%"
    page.locator("#lr").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#v-lr").inner_text() == "0.11"
    assert page.locator("#wd-constant-path").get_attribute("d") != constant


def check_adam(page) -> None:
    assert page.locator("#adam-dynamic-rows tr").count() == 4
    assert page.locator("#adam-g").inner_text() == "+2.00"
    assert page.locator("#adam-mhat").inner_text() == "+2.0000"
    assert page.locator("#adam-theta").inner_text() == "2.999000"
    assert page.locator("#adam-dynamic-bars rect").count() == 9
    page.locator('[data-time="2"]').click()
    assert page.locator("#adam-g").inner_text() == "−1.00"
    assert page.locator("#adam-mhat").inner_text() == "+0.4211"
    assert page.locator("#adam-dynamic-rows tr").nth(1).get_attribute("aria-current") == "step"
    page.locator('[data-time="4"]').focus()
    page.keyboard.press("Enter")
    assert page.locator("#adam-g").inner_text() == "+0.00"
    assert page.locator("#adam-mhat").inner_text() == "+0.3193"
    assert page.locator("#adam-theta").inner_text() == "2.998114"
    assert "−0.00027886" in page.locator("#adam-dynamic-explain").inner_text()
    assert page.locator('[data-time="4"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#adam-dynamic-rows tr").nth(3).get_attribute("aria-current") == "step"
    page.locator('[data-time="1"]').click()
    assert page.locator("#adam-theta").inner_text() == "2.999000"


def check_adamw(page) -> None:
    assert page.locator("#scale-value").inner_text() == "5"
    assert page.locator("#coupled-value").inner_text() == "0.99800"
    assert page.locator("#decoupled-value").inner_text() == "0.99000"
    assert page.locator("#aw-table-c2").inner_text() == "0.99800"
    assert page.locator("#aw-table-d2").inner_text() == "0.99000"
    assert page.locator("#aw-coupled-two-label").text_content() == "0.00200"
    before = float(page.locator("#aw-coupled-two-bar").get_attribute("width"))
    page.locator("#jump-scale").click()
    assert page.locator("#scale-value").inner_text() == "15"
    assert page.locator("#aw-table-c2").inner_text() == "0.99933"
    assert page.locator("#aw-coupled-two-label").text_content() == "0.00067"
    assert page.locator("#aw-table-ddrop").inner_text() == "0.01000"
    assert float(page.locator("#aw-coupled-two-bar").get_attribute("width")) < before
    set_slider(page, "#s-two", "1")
    assert page.locator("#coupled-value").inner_text() == "0.99000"
    assert page.locator("#aw-coupled-two-label").text_content() == "0.01000"
    page.locator("#reset-scale").click()
    assert page.locator("#scale-value").inner_text() == "5"
    page.locator("#s-two").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#scale-value").inner_text() == "6"
    assert page.locator("#aw-table-cdrop").inner_text() == "0.00167"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/sixth-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"))
    launcher = {"executable_path": str(executable)} if executable.exists() else {}
    successful = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **launcher)
        for slug, file in ARTICLES.items():
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors, requests = [], []
                page.on("pageerror", lambda e, target=errors: target.append(str(e)))
                page.route("https?://**", lambda route, target=requests: (
                    target.append(route.request.url), route.abort()
                ))
                page.goto(file.as_uri(), wait_until="load")
                audit = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
                    const refs=[...document.querySelectorAll('a[href^="#"]')]
                        .map(a=>decodeURIComponent(a.hash.slice(1)));
                    return {
                        h1:document.querySelectorAll('h1').length,
                        main:!!document.querySelector('main'),
                        overflow:document.documentElement.scrollWidth-innerWidth,
                        duplicates:ids.length-new Set(ids).size,
                        absentAnchors:refs.filter(ref=>ref&&!document.getElementById(ref)),
                        hiddenSvg:[...document.querySelectorAll('svg')]
                            .filter(s=>s.getBoundingClientRect().width<=0 || s.getBoundingClientRect().height<=0).length
                    };
                }""")
                assert audit["h1"] == 1 and audit["main"], (slug, width, audit)
                assert audit["duplicates"] == 0 and not audit["absentAnchors"], (slug, width, audit)
                assert audit["overflow"] <= 1 and audit["hiddenSvg"] == 0, (slug, width, audit)
                if width in (1440, 360):
                    {"weight-decay": check_decay, "adam": check_adam, "adamw": check_adamw}[slug](page)
                assert not errors and not requests, (slug, width, errors, requests)
                page.screenshot(path=str(args.output / f"{slug}-{width}.png"), full_page=False)
                successful.append({"article": slug, "width": width, "pass": True})
                page.close()
        browser.close()
    report = {"pass": True, "checks": successful}
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
