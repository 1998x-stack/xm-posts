"""Deterministic PDF cache fingerprints for built article inputs.

Hash the *built* HTML, local article assets, externally referenced local assets
(e.g. related-post covers), linked stylesheets and their url()/@import assets,
and the PDF renderer environment. Unrelated homepage/archive edits do not
invalidate article PDFs.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup

FINGERPRINT_VERSION = "xm-pdf-input-v3"
CSS_URL = re.compile(r"""url\(\s*(['"]?)(.*?)\1\s*\)""", re.I)
CSS_IMPORT = re.compile(r"""@import\s+(?:url\()?\s*['"]?([^'")\s;]+)""", re.I)


def _local_path(site_root: Path, owner: Path, reference: str) -> Path | None:
    reference = reference.strip()
    if not reference or reference.startswith(("#", "//")):
        return None
    url = urlsplit(reference)
    if url.scheme or url.netloc or not url.path:
        return None
    # GitHub Pages is a project site: a leading slash is a site-absolute URL,
    # not a path relative to the current article. Existing posts use relative
    # references; ignore web-root absolute paths rather than escaping _site/.
    if url.path.startswith("/"):
        return None
    path = (owner.parent / unquote(url.path)).resolve()
    if not path.is_relative_to(site_root):
        return None
    return path


def _css_references(css: str) -> list[str]:
    return [match.group(2) for match in CSS_URL.finditer(css)] + CSS_IMPORT.findall(css)


def _linked_files(site_root: Path, html_path: Path) -> set[Path]:
    """Find non-article dependencies that can visibly affect printed HTML."""
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    pending: list[Path] = []
    found: set[Path] = set()

    def add(owner: Path, reference: str) -> None:
        path = _local_path(site_root, owner, reference)
        if path is not None and path not in found:
            found.add(path)
            if path.suffix.lower() == ".css" and path.is_file():
                pending.append(path)

    for tag in soup.find_all(True):
        name = tag.name.lower()
        if name in ("img", "script", "source", "video", "audio"):
            for attr in ("src", "poster"):
                if isinstance(tag.get(attr), str):
                    add(html_path, tag[attr])
        elif name == "link" and "stylesheet" in (tag.get("rel") or []):
            if isinstance(tag.get("href"), str):
                add(html_path, tag["href"])
        elif name == "object" and isinstance(tag.get("data"), str):
            add(html_path, tag["data"])
        elif name in ("image", "use"):
            for attr in ("href", "xlink:href"):
                if isinstance(tag.get(attr), str):
                    add(html_path, tag[attr])
        if name in ("img", "source") and tag.get("srcset"):
            for candidate in tag["srcset"].split(","):
                tokens = candidate.strip().split()
                if tokens:
                    add(html_path, tokens[0])
        if tag.get("style"):
            for ref in _css_references(str(tag["style"])):
                add(html_path, ref)

    for style in soup.find_all("style"):
        for ref in _css_references(style.get_text()):
            add(html_path, ref)
    while pending:
        css_path = pending.pop()
        for ref in _css_references(css_path.read_text(encoding="utf-8")):
            add(css_path, ref)
    return found


def fingerprint(root: Path, out: Path, article_dir: Path, public_url: str) -> str:
    """Stable across build directories; changes only for print-relevant inputs."""
    root, out, article_dir = root.resolve(), out.resolve(), article_dir.resolve()
    if not article_dir.is_relative_to(out) or not (article_dir / "index.html").is_file():
        raise ValueError(f"Invalid built article directory: {article_dir}")

    inputs: set[Path] = {
        root / "scripts" / "render_pdfs.py",
        root / "scripts" / "pdf_fingerprint.py",
        root / "requirements-dev.txt",
    }
    inputs.update(p for p in article_dir.rglob("*") if p.is_file() and p.name != "article.pdf")
    inputs.update(_linked_files(out, article_dir / "index.html"))

    config = {
        "format": FINGERPRINT_VERSION,
        "public_url": public_url,
        "playwright": version("playwright"),
        "fonts": os.environ.get("PDF_FONT_SIGNATURE", "local-default"),
        "print_locale": "zh-CN",
    }
    digest = sha256(json.dumps(config, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    for path in sorted(inputs):
        if path.is_relative_to(out):
            label = "site/" + path.relative_to(out).as_posix()
        elif path.is_relative_to(root):
            label = "repo/" + path.relative_to(root).as_posix()
        else:
            raise ValueError(f"Out-of-root PDF input: {path}")
        digest.update(b"\x00PATH\x00" + label.encode("utf-8") + b"\x00")
        if path.is_file():
            digest.update(sha256(path.read_bytes()).digest())
        else:
            # A newly added reference must change the fingerprint.
            digest.update(b"missing")
    return digest.hexdigest()
