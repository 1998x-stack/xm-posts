#!/usr/bin/env python3
"""Focused Chromium QA for the Knowledge Distillation article and temperature lab."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "posts/training/knowledge-distillation/index.html"
VIEWPORTS = ((1440, 900), (768, 1024), (390, 844), (360, 800))


def audit_page(page, width: int) -> dict:
    result = page.evaluate("""() => {
      const ids = [...document.querySelectorAll('[id]')].map(node => node.id);
      const anchors = [...document.querySelectorAll('a[href^="#"]')]
        .map(node => decodeURIComponent(node.hash.slice(1)));
      const images = [...document.querySelectorAll('img')].map(img => ({
        src: img.getAttribute('src'), alt: img.getAttribute('alt') || '',
        loaded: img.complete && img.naturalWidth > 0
      }));
      const maths = [...document.querySelectorAll('math')];
      const mathNamespaces = maths.every(node =>
        node.namespaceURI === 'http://www.w3.org/1998/Math/MathML'
      );
      const rawLatex = document.body.innerText.includes("\\\\(") || document.body.innerText.includes("\\\\)");
      const mathInsideSvg = [...document.querySelectorAll('svg math')].length;
      return {
        h1: document.querySelectorAll('h1').length,
        hasMain: !!document.querySelector('main#content'),
        overflow: document.documentElement.scrollWidth - window.innerWidth,
        duplicateIds: ids.length - new Set(ids).size,
        missingAnchors: anchors.filter(id => id && !document.getElementById(id)),
        images,
        mathCount: maths.length,
        mathNamespaces,
        rawLatex,
        mathInsideSvg
      };
    }""")
    assert result["h1"] == 1 and result["hasMain"], (width, result)
    assert result["overflow"] <= 1, (width, result)
    assert result["duplicateIds"] == 0 and not result["missingAnchors"], (width, result)
    assert result["images"] and all(img["alt"] and img["loaded"] for img in result["images"]), (width, result)
    assert result["mathCount"] >= 12 and result["mathNamespaces"], (width, result)
    assert not result["rawLatex"] and result["mathInsideSvg"] == 0, (width, result)
    return result


def check_temperature_lab(page) -> None:
    slider = page.locator("#temperature")
    status = page.locator("#temperature-status")
    assert page.locator("#temperature-value").inner_text() == "2.0"
    assert "猫 52.4%" in status.inner_text()
    width_t2 = float(page.locator("#bar-cat").get_attribute("width"))
    slider.evaluate("(el) => { el.value='4'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    assert page.locator("#temperature-value").inner_text() == "4.0"
    assert "猫 43.0%" in status.inner_text()
    width_t4 = float(page.locator("#bar-cat").get_attribute("width"))
    assert width_t4 < width_t2
    assert page.locator("#bar-fox").get_attribute("width") != "71.00"
    slider.focus()
    page.keyboard.press("ArrowRight")
    assert page.locator("#temperature-value").inner_text() == "4.5"
    slider.evaluate("(el) => { el.value='2'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
    assert page.locator("#temperature-value").inner_text() == "2.0"


def check_print_layout(page) -> None:
    page.emulate_media(media="print")
    assert page.locator(".toc").evaluate("(el) => getComputedStyle(el).display") == "none"
    assert page.locator("#temperature").evaluate("(el) => getComputedStyle(el).display") == "none"
    page.emulate_media(media="screen")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/knowledge-distillation")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    executable = Path(os.environ.get("CHROMIUM_PATH", "/usr/bin/chromium"))
    launch_options = {"executable_path": str(executable)} if executable.exists() else {}
    checks = []
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=["--no-sandbox"], **launch_options)
        try:
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height})
                page_errors, external_requests = [], []
                page.on("pageerror", lambda error, target=page_errors: target.append(str(error)))
                page.route("https?://**", lambda route, target=external_requests: (
                    target.append(route.request.url), route.abort()
                ))
                page.goto(ARTICLE.as_uri(), wait_until="load")
                audit = audit_page(page, width)
                if width == 1440:
                    check_temperature_lab(page)
                    check_print_layout(page)
                assert not page_errors, (width, page_errors)
                assert not external_requests, (width, external_requests)
                page.screenshot(path=str(args.output / f"knowledge-distillation-{width}.png"), full_page=False)
                checks.append({"width": width, "height": height, "pass": True, "audit": audit})
                page.close()
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            raise
        finally:
            browser.close()
    report = {"pass": not errors, "viewports": checks, "errors": errors}
    (args.output / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
