#!/usr/bin/env python3
"""Audit embedded and standalone SVGs for broken references and accessibility.

Run from the repo root: python scripts/audit_svg.py
Warnings do not fail legacy posts; errors fail CI. --strict-desc can opt in
once all legacy standalone diagrams have meaningful descriptions.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
FRAGMENT_URL = re.compile(r"url\(\s*['\"]?#([A-Za-z_][\w:.-]*)['\"]?\s*\)")
SIZE_ATTR = re.compile(r"\bfont-size\s*[:=]\s*['\"]?(\d+(?:\.\d+)?)", re.I)


def local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def examine(svg, label: str, *, xml: bool, strict_desc: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if xml:
        nodes = list(svg.iter())
        attrs = lambda n: n.attrib
        name = lambda n: local(n.tag)
        raw = ET.tostring(svg, encoding="unicode")
    else:
        nodes = [svg, *svg.find_all(True)]
        attrs = lambda n: n.attrs
        name = lambda n: n.name
        raw = str(svg)

    ids = [str(attrs(n).get("id")) for n in nodes if attrs(n).get("id")]
    duplicates = [i for i, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"{label}: duplicate SVG IDs {duplicates[:8]}")

    view = attrs(svg).get("viewBox") or attrs(svg).get("viewbox")
    if not view:
        errors.append(f"{label}: SVG missing viewBox")
    else:
        try:
            x, y, w, h = map(float, re.split(r"[\s,]+", str(view).strip()))
            if not all(map(lambda v: abs(v) < 1e9, (x, y, w, h))) or w <= 0 or h <= 0:
                raise ValueError("non-positive or unreasonable dimensions")
        except (ValueError, TypeError):
            errors.append(f"{label}: invalid viewBox {view!r}")

    titles = [n for n in nodes[1:] if name(n) == "title"]
    descriptions = [n for n in nodes[1:] if name(n) == "desc"]
    if not titles and not attrs(svg).get("aria-label"):
        errors.append(f"{label}: no SVG title or accessible name")
    if not descriptions:
        message = f"{label}: missing SVG description"
        (errors if strict_desc else warnings).append(message)

    known = set(ids)
    for n in nodes:
        for prop in ("aria-labelledby", "aria-describedby"):
            for target in str(attrs(n).get(prop) or "").split():
                if target not in known:
                    errors.append(f"{label}: broken {prop} reference #{target}")
    for target in FRAGMENT_URL.findall(raw):
        if target not in known:
            errors.append(f"{label}: broken paint/marker reference url(#{target})")

    if any(name(n) in ("script", "foreignObject") for n in nodes):
        errors.append(f"{label}: executable or foreign SVG content")
    if re.search(r"(?i)\b(?:href|xlink:href)\s*=\s*['\"](?:https?:|javascript:)", raw):
        warnings.append(f"{label}: external SVG reference")

    tiny = sum(float(m.group(1)) < 11 for m in SIZE_ATTR.finditer(raw))
    if tiny:
        warnings.append(f"{label}: {tiny} font declarations below 11px; review legibility")
    return errors, warnings


def audit(root: Path, strict_desc: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    totals = {"articles": 0, "inline_svg": 0, "standalone_svg": 0}

    for page in sorted((root / "posts").glob("*/*/index.html")):
        totals["articles"] += 1
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        all_ids = [n.get("id") for n in soup.select("[id]")]
        duplicates = [x for x, count in Counter(all_ids).items() if count > 1]
        if duplicates:
            errors.append(f"{page.relative_to(root)}: duplicate HTML/SVG IDs {duplicates[:8]}")
        for i, svg in enumerate(soup.find_all("svg"), 1):
            totals["inline_svg"] += 1
            bad, warn = examine(svg, f"{page.relative_to(root)} SVG #{i}",
                                 xml=False, strict_desc=strict_desc)
            errors.extend(bad)
            warnings.extend(warn)

    for asset in sorted((root / "posts").glob("*/*/assets/*.svg")):
        totals["standalone_svg"] += 1
        label = str(asset.relative_to(root))
        try:
            raw = asset.read_text(encoding="utf-8")
            svg = ET.fromstring(raw)
            if local(svg.tag) != "svg":
                raise ValueError("root element is not SVG")
        except (UnicodeError, ET.ParseError, ValueError) as exc:
            errors.append(f"{label}: invalid standalone SVG XML: {exc}")
            continue
        if 'xmlns="http://www.w3.org/2000/svg"' not in raw[:300]:
            warnings.append(f"{label}: explicit SVG namespace missing")
        bad, warn = examine(svg, label, xml=True, strict_desc=strict_desc)
        errors.extend(bad)
        warnings.extend(warn)

    return {"pass": not errors, "counts": totals, "errors": errors, "warnings": warnings}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict-desc", action="store_true")
    p.add_argument("--report", type=Path, default=Path("reports/svg-audit.json"))
    args = p.parse_args()
    result = audit(ROOT, args.strict_desc)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SVG audit:", result["counts"], f"errors={len(result['errors'])}",
          f"warnings={len(result['warnings'])}")
    for item in result["errors"][:80]:
        print("ERROR", item)
    for item in result["warnings"][:24]:
        print("WARN ", item)
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
