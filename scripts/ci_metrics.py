#!/usr/bin/env python3
"""Fail-visible CI timing and PDF cache telemetry without changing build outputs."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


def _write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def record_start(directory: Path) -> None:
    _write(directory / "start.json", {
        "epoch": time.time(),
        "start_utc": datetime.now(timezone.utc).isoformat(),
        "sha": os.environ.get("GITHUB_SHA", "local"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "local"),
    })


def run_step(directory: Path, name: str, command: list[str], log: Path | None = None) -> int:
    if not re.fullmatch(r"[a-z][a-z0-9-]*", name):
        raise ValueError("Invalid CI metric name")
    if not command:
        raise ValueError("Missing command after --")
    directory.mkdir(parents=True, exist_ok=True)
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    started = datetime.now(timezone.utc).isoformat()
    return_code = 1
    try:
        if log is None:
            return_code = subprocess.run(command, check=False).returncode
        else:
            with log.open("w", encoding="utf-8") as handle:
                process = subprocess.Popen(
                    command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace", bufsize=1,
                )
                assert process.stdout is not None
                for line in process.stdout:
                    handle.write(line)
                    print(line, end="", flush=True)
                return_code = process.wait()
        return return_code
    finally:
        elapsed = round(time.perf_counter() - start, 3)
        _write(directory / (name + ".json"), {
            "name": name, "seconds": elapsed, "exit_code": return_code,
            "started_at_utc": started, "command": command,
        })
        print(f"CI TIMING {name}: {elapsed:.3f}s / exit={return_code}", flush=True)


def pdf_from_log(path: Path) -> dict | None:
    """Find the render_pdfs.py terminal JSON. Missing results remain unknown."""
    if not path.is_file():
        return None
    for line in reversed(path.read_text(encoding="utf-8").splitlines()):
        try:
            item = json.loads(line)
        except (ValueError, TypeError):
            continue
        if isinstance(item, dict) and all(k in item for k in ("pdf_count", "cached", "rendered", "total_bytes")):
            values = [item[k] for k in ("pdf_count", "cached", "rendered", "total_bytes")]
            if not all(isinstance(v, int) and v >= 0 for v in values):
                return None
            if item["cached"] + item["rendered"] != item["pdf_count"]:
                return None
            return item
    return None


def report(directory: Path, pdf_log: Path, browser_report: Path, site: Path) -> tuple[str, dict]:
    phase_files = sorted(directory.glob("*.json"))
    phases = []
    for path in phase_files:
        if path.name == "start.json":
            continue
        item = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(item, dict) and {"name", "seconds", "exit_code"} <= item.keys():
            phases.append(item)
    # Execution order rather than lexical order; write-once per logical phase.
    phases.sort(key=lambda item: item.get("started_at_utc", ""))
    begin_path = directory / "start.json"
    begin = json.loads(begin_path.read_text(encoding="utf-8")) if begin_path.is_file() else {}
    wallclock = round(time.time() - begin["epoch"], 2) if isinstance(begin.get("epoch"), (int, float)) else None
    pdf = pdf_from_log(pdf_log)
    browser = json.loads(browser_report.read_text(encoding="utf-8")) if browser_report.is_file() else None
    site_size = sum(p.stat().st_size for p in site.rglob("*") if p.is_file()) if site.is_dir() else None
    metrics = {
        "measured_wall_seconds": wallclock,
        "sum_timed_seconds": round(sum(p["seconds"] for p in phases), 2),
        "phases": phases,
        "pdf": pdf,
        "browser": None if not browser else {
            k: browser.get(k) for k in
            ("pass", "expected_articles", "verified_articles", "workers", "browser_launches", "elapsed_seconds")
        },
        "site_bytes": site_size,
    }
    lines = ["## xm-posts CI performance", "",
             "Timing begins after Python setup; excludes runner queue, provisioning, and the separate Pages deployment job.", "",
             "| Phase | Seconds | Result |", "|:--|--:|:--|"]
    for entry in phases:
        lines.append(f"| {entry['name']} | {entry['seconds']:.1f} | {'PASS' if entry['exit_code']==0 else 'FAIL'} |")
    lines += ["", f"**Observed execution window:** {f'{wallclock:.1f}s' if wallclock is not None else 'Unavailable'}",
              f"**Sum of timed phases:** {metrics['sum_timed_seconds']:.1f}s", ""]
    if pdf is None:
        lines.append("**PDF cache:** unavailable (PDF step incomplete or no summary).")
    else:
        hit_rate = 100 * pdf["cached"] / pdf["pdf_count"] if pdf["pdf_count"] else 0
        lines.append(
            f"**PDF:** {pdf['pdf_count']} published / {pdf['cached']} cached "
            f"/ {pdf['rendered']} rendered / **{hit_rate:.1f}% cache hits** "
            f"/ {pdf['total_bytes']/1048576:.1f} MiB."
        )
    if browser is None:
        lines.append("**Article browser QA:** unavailable.")
    else:
        lines.append(
            f"**Article browser QA:** {browser.get('verified_articles', '?')}/"
            f"{browser.get('expected_articles', '?')} posts, "
            f"{browser.get('workers', '?')} workers, "
            f"{browser.get('browser_launches', '?')} Chromium launches."
        )
    if site_size is not None:
        lines.append(f"**Built site size:** {site_size/1048576:.1f} MiB.")
    lines += ["", "_Cache hits and elapsed times are observed results; an absent result is not treated as zero._", ""]
    return "\n".join(lines), metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="action", required=True)
    for action in ("start", "run", "summary"):
        part = subs.add_parser(action)
        part.add_argument("--directory", type=Path, default=Path("reports/ci"))
        if action == "run":
            part.add_argument("--name", required=True)
            part.add_argument("--log", type=Path)
            part.add_argument("command", nargs=argparse.REMAINDER)
        if action == "summary":
            part.add_argument("--pdf-log", type=Path, default=Path("reports/ci/pdf-render.log"))
            part.add_argument("--browser-report", type=Path, default=Path("reports/browser-all-summary.json"))
            part.add_argument("--site", type=Path, default=Path("_site"))
            part.add_argument("--write", type=Path)
    args = parser.parse_args()
    if args.action == "start":
        record_start(args.directory)
        return 0
    if args.action == "run":
        command = args.command[1:] if args.command and args.command[0] == "--" else args.command
        return run_step(args.directory, args.name, command, args.log)
    markdown, metrics = report(args.directory, args.pdf_log, args.browser_report, args.site)
    args.directory.mkdir(parents=True, exist_ok=True)
    (args.directory / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.directory / "summary.md").write_text(markdown, encoding="utf-8")
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        with args.write.open("a", encoding="utf-8") as output:
            output.write(markdown + "\n")
    print(markdown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
