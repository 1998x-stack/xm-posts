#!/usr/bin/env python3
"""Static article quality gate. Exit nonzero on critical failures; write JSON with --report."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Production-process labels are disallowed inside an article; they belong in project docs.
BANNED = (
    '原创图解 · 单文件离线 HTML',
    '用直觉 → 图示 → 数学 → 工程实现，理解残差网络 · 参考 Colah 风格，非原文翻译',

)

ALLOWED_EVIDENCE_STATUS = {"verified", "derived", "illustrative", "unverified"}
REQUIRED_EVIDENCE_FIELDS = ("id", "claim", "kind", "source_url", "locator", "status")


def validate_evidence_ledger(path: Path) -> dict:
    """Validate the traceability structure without pretending to verify claims."""
    failures, warnings = [], []
    evidence = validate_evidence_ledger(path.parent / 'evidence.json')
    failures.extend(evidence['failures'])
    warnings.extend(evidence['warnings'])
    if not path.is_file():
        return {"pass": False, "claim_count": 0,
                "failures": [f"Missing evidence ledger: {path}"], "warnings": []}
    try:
        entries = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"pass": False, "claim_count": 0,
                "failures": [f"Invalid evidence JSON: {exc}"], "warnings": []}
    if not isinstance(entries, list) or not entries:
        return {"pass": False, "claim_count": 0,
                "failures": ["Evidence ledger must be a non-empty JSON array"], "warnings": []}
    seen_ids = set()
    for index, entry in enumerate(entries, 1):
        label = f"evidence entry {index}"
        if not isinstance(entry, dict):
            failures.append(f"{label}: expected an object")
            continue
        for field in REQUIRED_EVIDENCE_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                failures.append(f"{label}: missing or empty {field}")
        identifier = entry.get("id")
        if isinstance(identifier, str) and identifier.strip():
            if identifier in seen_ids:
                failures.append(f"{label}: duplicate id {identifier}")
            seen_ids.add(identifier)
        status = entry.get("status")
        if status not in ALLOWED_EVIDENCE_STATUS:
            failures.append(f"{label}: invalid status {status!r}")
        source = entry.get("source_url")
        if isinstance(source, str) and source.strip():
            parsed = urlparse(source)
            if parsed.scheme != "https" or not parsed.netloc:
                failures.append(f"{label}: source_url must be an absolute HTTPS URL")
        notes = entry.get("notes")
        if not isinstance(notes, str) or not notes.strip():
            warnings.append(f"{label}: notes should explain scope, caveat, or verification boundary")
        if status == "unverified":
            warnings.append(f"{label}: claim is explicitly marked unverified")
    return {"pass": not failures, "claim_count": len(entries),
            "failures": failures, "warnings": warnings}


def validate(path: Path) -> dict:
    html = path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    failures, warnings = [], []
    h1 = soup.find_all('h1')
    if len(h1) != 1: failures.append(f'Expected exactly one h1, found {len(h1)}')
    if not soup.find('main'): failures.append('Missing semantic main')
    if not soup.find('nav'): warnings.append('No navigable table of contents')
    if not soup.find('meta', attrs={'name': 'viewport'}): failures.append('Missing mobile viewport meta')
    if len(soup.find_all('h2')) < 2: failures.append('Expected at least two instructional sections')
    for phrase in BANNED:
        if phrase in soup.get_text(' ', strip=True) or phrase in html:
            failures.append('Banned production/process copy found: ' + phrase)
    anchors = {tag.get('id') for tag in soup.select('[id]')}
    for a in soup.select('a[href^="#"]'):
        target = a['href'][1:]
        if target and target not in anchors: failures.append('Broken local anchor #' + target)
    figures = soup.find_all('figure')
    if not figures: failures.append('No semantic figures')
    for index, figure in enumerate(figures, 1):
        if not figure.find('svg') and not figure.find('img'):
            failures.append(f'Figure {index} has no image or SVG')
        caption = figure.find('figcaption')
        if not caption or not caption.get_text(strip=True):
            failures.append(f'Figure {index} has no nonempty figcaption')
    svgs = soup.find_all('svg')
    if not svgs: failures.append('No SVG illustrations')
    for index, svg in enumerate(svgs, 1):
        if not svg.has_attr('viewbox'): failures.append(f'SVG {index} missing viewBox')
        if not (svg.get('aria-label') or svg.get('aria-labelledby') or svg.find('title')):
            failures.append(f'SVG {index} missing accessible label/title')
    for i, img in enumerate(soup.find_all('img'), 1):
        if not img.get('alt'): warnings.append(f'Image {i} missing alt text')
        src = img.get('src', '')
        if src and not re.match(r'^(?:data:|https?://)', src) and not (path.parent / src).exists():
            failures.append('Missing image: ' + src)
    for script in soup.find_all('script', src=True):
        if script['src'].startswith('http'): warnings.append('External JS dependency: ' + script['src'])
    for link in soup.find_all('link', href=True):
        if link['href'].startswith('http'): warnings.append('External stylesheet dependency: ' + link['href'])
    # Every published article carries at least one semantic MathML expression.
    maths = soup.find_all('math')
    if not maths: failures.append('Missing native MathML; published articles require semantic math')
    for idx, math in enumerate(maths, 1):
        if math.find_parent('svg'):
            failures.append(f'MathML {idx} nested inside SVG (invalid namespace)')
        if not (math.get('aria-label') or math.get('aria-labelledby')):
            failures.append(f'MathML {idx} missing accessible description')
        if not math.find(['mi', 'mn', 'mo', 'mrow', 'mfrac', 'msup', 'msub', 'munder', 'munderover', 'mtable']):
            failures.append(f'MathML {idx} has no mathematical structure')
        if math.get('display') not in (None, 'inline', 'block'):
            failures.append(f'MathML {idx} invalid display attribute')
        for name, arity in [('mfrac', 2), ('msub', 2), ('msup', 2),
                            ('msubsup', 3), ('munder', 2), ('mover', 2), ('munderover', 3)]:
            for node in math.find_all(name):
                children = [child for child in node.children if getattr(child, 'name', None)]
                if len(children) != arity:
                    failures.append(f'MathML {idx} malformed {name}: expected {arity} children, got {len(children)}')
        if math.get('display') == 'block':
            region = math.find_parent(attrs={'data-math-scroll': True})
            if region is None:
                region = math.find_parent(class_=['math-scroll', 'eq-scroll'])
            if region is None or region.get('tabindex') != '0' or region.get('role') != 'region':
                failures.append(f'MathML {idx} display equation needs a keyboard-focusable scroll region')
    if not soup.find('a', href=re.compile('arxiv.org|doi.org|thecvf.com')):
        warnings.append('No obvious primary-paper reference in article')
    return {
        'path': str(path), 'pass': not failures,
        'counts': {'h2': len(soup.find_all('h2')), 'figures': len(figures), 'svg': len(svgs), 'buttons': len(soup.find_all('button')), 'mathml': len(maths), 'evidence_claims': evidence['claim_count']},
        'failures': failures, 'warnings': warnings,
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('html', type=Path)
    p.add_argument('--report', type=Path)
    args = p.parse_args()
    report = validate(args.html.resolve())
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report['pass'] else 1

if __name__ == '__main__': sys.exit(main())
