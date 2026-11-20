#!/usr/bin/env python3
"""Focused Chromium QA for the Agent Evaluation article."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "posts/agents/agent-evaluation/index.html"
SVG_DIR = ARTICLE.parent / "assets"
VIEWPORTS = ((1440, 900), (768, 1024), (390, 844), (360, 800))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "reports/agent-evaluation")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"))
    launcher = {"executable_path": str(executable)} if executable.exists() else {}
    checks: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"], **launcher)
        for width, height in VIEWPORTS:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors: list[str] = []
            external_requests: list[str] = []
            page.on("pageerror", lambda error, target=errors: target.append(str(error)))
            page.route(
                "https?://**",
                lambda route, target=external_requests: (
                    target.append(route.request.url), route.abort()
                ),
            )
            page.goto(ARTICLE.as_uri(), wait_until="load")

            audit = page.evaluate("""() => {
                const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
                const anchors = [...document.querySelectorAll('a[href^="#"]')]
                    .map(anchor => decodeURIComponent(anchor.hash.slice(1)));
                const images = [...document.images].map(image => ({
                    src: image.getAttribute('src'),
                    loaded: image.complete && image.naturalWidth > 0
                }));
                const math = [...document.querySelectorAll('math')].map(node => {
                    const box = node.getBoundingClientRect();
                    return {width: box.width, height: box.height};
                });
                return {
                    h1: document.querySelectorAll('h1').length,
                    main: !!document.querySelector('main'),
                    svgCount: document.querySelectorAll('svg').length,
                    duplicateIds: ids.length - new Set(ids).size,
                    overflow: document.documentElement.scrollWidth - innerWidth,
                    duplicateIds: ids.length - new Set(ids).size,
                    missingAnchors: anchors.filter(id => id && !document.getElementById(id)),
                    images,
                    math,
                    remoteScripts: [...document.scripts].filter(script =>
                        script.src && /^https?:/.test(script.src)
                    ).map(script => script.src)
                };
            }""")
            assert audit["h1"] == 1 and audit["main"], (width, audit)
            assert audit["svgCount"] == 6 and audit["duplicateIds"] == 0, (width, audit)
            assert audit["overflow"] <= 1, (width, audit)
            assert audit["duplicateIds"] == 0, (width, audit)
            assert not audit["missingAnchors"], (width, audit)
            assert all(item["loaded"] for item in audit["images"]), (width, audit)
            assert all(item["width"] > 0 and item["height"] > 0 for item in audit["math"]), (width, audit)
            assert not audit["remoteScripts"], (width, audit)
            assert not errors and not external_requests, (width, errors, external_requests)

            if width == 1440:
                assert page.locator("#pass-at-k").inner_text() == "99.968%"
                assert page.locator("#pass-all-k").inner_text() == "32.768%"
                page.locator("#success-p").evaluate(
                    "(node) => { node.value='0.70'; node.dispatchEvent(new Event('input', {bubbles:true})); }"
                )
                page.locator("#attempt-k").evaluate(
                    "(node) => { node.value='3'; node.dispatchEvent(new Event('input', {bubbles:true})); }"
                )
                assert page.locator("#pass-at-k").inner_text() == "97.300%"
                assert page.locator("#pass-all-k").inner_text() == "34.300%"
                page.locator("#success-p").focus()
                page.keyboard.press("Home")
                assert page.locator("#success-p-value").inner_text() == "50%"
                page.locator("#success-p").evaluate(
                    "(node) => { node.value='0.80'; node.dispatchEvent(new Event('input', {bubbles:true})); }"
                )
                page.locator("#attempt-k").evaluate(
                    "(node) => { node.value='5'; node.dispatchEvent(new Event('input', {bubbles:true})); }"
                )
                assert page.locator("#pass-at-k").inner_text() == "99.968%"

            page.screenshot(path=str(args.output / f"agent-evaluation-{width}.png"), full_page=False)
            checks.append({"viewport": width, "height": height, "pass": True})
            if width == 1440:
                page.emulate_media(media="print")
                assert page.locator(".sitebar").evaluate(
                    "node => getComputedStyle(node).display"
                ) == "none"
                page.screenshot(path=str(args.output / "agent-evaluation-print.png"), full_page=False)
            page.close()

        standalone_svgs = []
        for svg_file in sorted(SVG_DIR.glob("*.svg")):
            svg_page = browser.new_page(viewport={"width": 1200, "height": 700})
            svg_page.goto(svg_file.as_uri(), wait_until="load")
            svg_audit = svg_page.evaluate("""() => {
                const svg = document.querySelector("svg");
                const ids = [...document.querySelectorAll("[id]")].map(node => node.id);
                const refs = (svg?.getAttribute("aria-labelledby") || "").split(/\\s+/).filter(Boolean);
                const box = svg?.getBoundingClientRect();
                return {
                    rootIsSvg: document.documentElement.localName === "svg",
                    viewBox: svg?.getAttribute("viewBox") || "",
                    title: !!svg?.querySelector("title"),
                    desc: !!svg?.querySelector("desc"),
                    labelTargetsExist: refs.every(id => document.getElementById(id)),
                    duplicateIds: ids.length - new Set(ids).size,
                    width: box?.width || 0,
                    height: box?.height || 0
                };
            }""")
            assert svg_audit["rootIsSvg"] and svg_audit["viewBox"], (svg_file.name, svg_audit)
            assert svg_audit["title"] and svg_audit["desc"] and svg_audit["labelTargetsExist"], (svg_file.name, svg_audit)
            assert svg_audit["duplicateIds"] == 0 and svg_audit["width"] > 0 and svg_audit["height"] > 0, (svg_file.name, svg_audit)
            svg_page.screenshot(path=str(args.output / f"standalone-{svg_file.stem}.png"))
            standalone_svgs.append({"file": svg_file.name, "pass": True})
            svg_page.close()
        browser.close()

    report = {"pass": True, "article": str(ARTICLE.relative_to(ROOT)), "checks": checks, "standalone_svgs": standalone_svgs}
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
