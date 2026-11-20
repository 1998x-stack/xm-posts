#!/usr/bin/env python3
"""Fourth learning-path QA: RNN sensitivity, LSTM cell memory, Seq2Seq attention.

Playwright checks four viewport widths, including genuine keyboard and button interactions.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = {
    "rnn": ROOT / "posts/architectures/rnn/index.html",
    "lstm": ROOT / "posts/architectures/lstm/index.html",
    "seq2seq": ROOT / "posts/architectures/seq2seq/index.html",
}
VIEWPORTS = [(1440, 900), (768, 1024), (390, 844), (360, 800)]


def change_range(page, selector, value):
    page.locator(selector).evaluate(
        "(element,value)=>{element.value=value;element.dispatchEvent(new Event('input',{bubbles:true}));}",
        value,
    )


def test_rnn(page):
    assert page.locator("#lambda-result").inner_text() == "0.1678"
    assert page.locator("#rnn-magnitude-rows tr").count() == 5
    assert page.locator("#rnn-magnitude-rows tr").last.locator("td").first.inner_text() == "0.167772"
    initial_path = page.locator("#rnn-log-path").get_attribute("d")
    page.locator('[data-rate="0.5"]').click()
    assert page.locator("#lambda-result").inner_text() == "0.0039"
    change_range(page, "#rnn-steps", "16")
    assert page.locator("#rnn-readout-step").inner_text() == "16"
    assert page.locator("#rnn-magnitude-rows tr").last.locator("td").first.inner_text() == "0.000015"
    assert page.locator("#rnn-plot-n").text_content() == "k=16"
    assert page.locator("#rnn-log-path").get_attribute("d") != initial_path
    page.locator('[data-rate="1"]').click()
    assert page.locator("#lambda-result").inner_text() == "1.0000"
    page.locator("#lambda").focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#lambda-value").inner_text() == "1.10"
    assert page.locator("#rnn-log-end").get_attribute("cy") is not None


def test_lstm(page):
    assert page.locator("#lstm-old").inner_text() == "0.445700"
    assert page.locator("#lstm-added").inner_text() == "0.000000"
    assert page.locator("#lstm-total").inner_text() == "0.445700"
    page.locator("#write-new").click()
    assert page.locator("#lstm-added").inner_text() == "0.554300"
    assert page.locator("#lstm-total").inner_text() == "1.000000"
    assert page.locator("#write-new").get_attribute("aria-pressed") == "true"
    assert page.locator("#lstm-trajectory-rows rect").count() >= 8
    page.locator('[data-forget="1"]').click()
    assert page.locator("#lstm-old").inner_text() == "1.000000"
    assert page.locator("#lstm-added").inner_text() == "0.800000"
    assert page.locator("#lstm-total").inner_text() == "1.800000"
    page.locator("#steps").focus()
    page.keyboard.press("ArrowLeft")
    assert page.locator("#steps-value").inner_text() == "39"
    page.locator("#retain-only").click()
    assert page.locator("#lstm-added").inner_text() == "0.000000"
    assert page.locator("#lstm-total").inner_text() == "1.000000"


def test_seq2seq(page):
    assert page.locator("#s2s-context-value").inner_text() == "1.950"
    assert page.locator("#s2s-matrix-rows tr").count() == 3
    assert page.locator('#s2s-matrix-rows tr[data-attention-row="chat"]').get_attribute("class") == "active"
    page.locator('[data-target="le"]').click()
    assert page.locator("#s2s-context-value").inner_text() == "1.280"
    assert page.locator("#attention-readout").inner_text().endswith("1.00。")
    assert page.locator('[data-target="le"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#s2s-context-equation").inner_text().startswith("0.73×1")
    page.locator('[data-target="dort"]').focus()
    page.keyboard.press("Enter")
    assert page.locator("#s2s-context-value").inner_text() == "2.590"
    assert page.locator('[data-target="dort"]').get_attribute("aria-pressed") == "true"
    assert page.locator("#s2s-matrix-rows tr.active").get_attribute("data-attention-row") == "dort"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "fourth-batch")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.getenv("CHROMIUM_PATH", "/usr/bin/chromium"))
    opts = {"executable_path": str(executable)} if executable.exists() else {}
    checks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox"], **opts)
        for name, path in ARTICLES.items():
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                remote = []
                page.on("pageerror", lambda e, dest=errors: dest.append(str(e)))
                page.route("https?://**", lambda route, dest=remote: (
                    dest.append(route.request.url), route.abort()
                ))
                page.goto(path.as_uri(), wait_until="load")
                audit = page.evaluate("""() => {
                    const ids=[...document.querySelectorAll('[id]')].map(el=>el.id);
                    const anchors=[...document.querySelectorAll('a[href^="#"]')]
                        .map(a=>decodeURIComponent(a.hash.slice(1)));
                    return {
                        h1:document.querySelectorAll('h1').length,
                        main:!!document.querySelector('main'),
                        overflow:document.documentElement.scrollWidth-innerWidth,
                        duplicateIds:ids.length-new Set(ids).size,
                        badAnchors:anchors.filter(id=>id&&!document.getElementById(id)),
                        unrenderedSvg:[...document.querySelectorAll('svg')]
                            .filter(svg=>!svg.getBoundingClientRect().width||!svg.getBoundingClientRect().height).length
                    };
                }""")
                assert audit["h1"] == 1 and audit["main"], (name, width, audit)
                assert audit["overflow"] <= 1, (name, width, audit)
                assert audit["duplicateIds"] == 0 and not audit["badAnchors"], (name, width, audit)
                assert audit["unrenderedSvg"] == 0, (name, width, audit)
                if width in (1440, 360):
                    {"rnn": test_rnn, "lstm": test_lstm, "seq2seq": test_seq2seq}[name](page)
                assert not errors and not remote, (name, width, errors, remote)
                page.screenshot(path=str(args.output / f"{name}-{width}.png"), full_page=False)
                checks.append({"article": name, "width": width, "pass": True})
                page.close()
        browser.close()
    report = {"pass": True, "checks": checks}
    (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
