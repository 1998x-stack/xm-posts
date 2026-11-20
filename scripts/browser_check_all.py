#!/usr/bin/env python3
"""Full published-article Playwright QA with reused Chromium and bounded workers.

The same canonical Skill checker still validates desktop/tablet/390px/360px,
math, SVG, interactions, and print. We change scheduling, never test coverage.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import os
from pathlib import Path
import sys
import time
import traceback

from build_site import ROOT, data

CHECKER_DIR = ROOT / "skills" / "olah-style-paper-posts" / "scripts"
DEFAULT_WORKERS = 2


def partition_articles(articles: list[tuple[str, str]], shards: int) -> list[list[tuple[str, str]]]:
    """One and only one shard per published article; stable when inputs reorder."""
    if shards < 1 or len({slug for slug, _ in articles}) != len(articles):
        raise ValueError("Invalid QA shard count or duplicated slugs")
    ordered = sorted(articles, key=lambda pair: pair[0])
    return [ordered[i::shards] for i in range(shards)]


def _check_shard(shard: int, articles: list[tuple[str, str]], output: str) -> dict:
    # Do not construct a Playwright driver in the parent process. Its sync API
    # is process-local, and each worker owns and closes exactly one Chromium.
    from playwright.sync_api import sync_playwright
    sys.path.insert(0, str(CHECKER_DIR))
    from browser_check import SIZES, check_article, launch_browser

    output_dir = Path(output)
    started = time.perf_counter()
    checked, failures = [], []
    with sync_playwright() as playwright:
        browser = launch_browser(playwright)
        try:
            for slug, category in articles:
                path = ROOT / "posts" / category / slug / "index.html"
                report_file = output_dir / slug / "report.json"
                try:
                    report = check_article(path, output_dir / slug, browser)
                    if set(report["viewports"]) != {label for label, _, _ in SIZES}:
                        raise ValueError(f"{slug}: missing viewport evidence")
                    if not report["pass"]:
                        failures.append(f"{slug}: semantic/visual/interactivity QA failed")
                    else:
                        checked.append(slug)
                    print(f"SHARD {shard} {'OK' if report['pass'] else 'FAIL'} {slug}", flush=True)
                except Exception as exc:
                    # Fail closed, but continue collecting evidence for the other
                    # articles in this shard. Missing reports never count as pass.
                    failures.append(f"{slug}: {type(exc).__name__}: {exc}")
                    report_file.parent.mkdir(parents=True, exist_ok=True)
                    report_file.write_text(json.dumps({
                        "file": str(path), "pass": False,
                        "error": traceback.format_exc(),
                    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    print(f"SHARD {shard} ERROR {slug}: {exc}", flush=True)
        finally:
            browser.close()
    return {
        "shard": shard, "assigned": len(articles), "passed": checked,
        "failures": failures, "seconds": round(time.perf_counter() - started, 3),
        "browser_launches": 1,
    }


def run(workers: int, output: Path) -> dict:
    if not 1 <= workers <= 4:
        raise ValueError("The supported worker count is 1–4 (resource bounded)")
    _, posts = data(ROOT)
    articles = [(p["slug"], p["category"]) for p in posts if p["status"] == "published"]
    if not articles:
        raise ValueError("No published articles found; cannot silently skip QA")
    shards = partition_articles(articles, min(workers, len(articles)))
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    completed, failures = [], []
    # Each worker retains its own Playwright Chromium process across all
    # assigned articles; no browser object is shared across processes.
    with ProcessPoolExecutor(max_workers=len(shards)) as executor:
        futures = {
            executor.submit(_check_shard, i, group, str(output)): i
            for i, group in enumerate(shards)
        }
        for future in as_completed(futures):
            shard = futures[future]
            try:
                result = future.result()
                completed.append(result)
                failures.extend(result["failures"])
            except Exception as exc:
                failures.append(f"shard {shard} crashed: {type(exc).__name__}: {exc}")
    passed = [slug for entry in completed for slug in entry["passed"]]
    expected = {slug for slug, _ in articles}
    if len(passed) != len(set(passed)):
        failures.append("Duplicate completed articles")
    if set(passed) != expected:
        failures.append(f"Unverified published articles: {sorted(expected-set(passed))}")
    summary = {
        "pass": not failures, "expected_articles": len(articles),
        "verified_articles": len(set(passed)), "viewports_per_article": 4,
        "workers": len(shards), "browser_launches": sum(x["browser_launches"] for x in completed),
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "shards": sorted(completed, key=lambda x: x["shard"]),
        "failures": failures,
    }
    (output.parent / "browser-all-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("BROWSER QA COMPLETE", json.dumps({
        key: summary[key] for key in (
            "pass", "expected_articles", "verified_articles", "workers",
            "browser_launches", "elapsed_seconds", "failures"
        )
    }, ensure_ascii=False), flush=True)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int,
                        default=int(os.environ.get("BROWSER_QA_WORKERS", DEFAULT_WORKERS)))
    parser.add_argument("--output", type=Path, default=ROOT / "reports" / "articles")
    args = parser.parse_args()
    return 0 if run(args.workers, args.output)["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
