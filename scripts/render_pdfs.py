#!/usr/bin/env python3
"""Render one downloadable PDF for every *published* article, without rewriting source HTML.

Run after scripts/build_site.py. Uses the browser's existing print CSS, so inline
SVG and MathML remain browser-rendered; the download control is injected only
into generated _site/ HTML after the PDF is successfully written.
"""
from __future__ import annotations

import argparse
from io import BytesIO
from hashlib import sha256
from html import escape
import json
from pathlib import Path
import re

from pdf_fingerprint import fingerprint

from playwright.sync_api import sync_playwright
from pypdf import PdfReader

from build_site import ROOT, DEFAULT_URL, article_url, data

PDF_NAME = "article.pdf"
DOWNLOAD_CSS = "../../../assets/pdf-download.css"

# Complement individual articles' own @media print rules, not a new PDF template.
# Keep SVG, MathML, figures and article typography in the original document.
PRINT_CSS = """
@page { size: A4; }
@media print {
  html, body { overflow: visible !important; }
  body { background: white !important; print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  *, *::before, *::after { animation: none !important; transition: none !important; }
  .side, .toc, .sidebar, .sitebar, .mast, .banner, .site-header,
  .skip, .skip-link, nav[aria-label="文章目录"], nav[aria-label="目录"] {
    display: none !important;
  }
  .layout, .shell, .page-layout, .article-layout, .reading-layout, .post-layout {
    display: block !important;
    width: 100% !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  main, article, .article, .article-body, .post-body, .article-main {
    max-width: none !important;
    min-width: 0 !important;
  }
  img, svg { max-width: 100% !important; }
  h1, h2, h3 { break-after: avoid-page; }
  figure, .figure, .diagram { break-inside: avoid-page; box-shadow: none !important; }
  pre { white-space: pre-wrap !important; overflow-wrap: anywhere !important; }
  button, input, select, textarea { display: none !important; }
}
"""


def with_download_link(html: str, title: str, slug: str) -> str:
    """Inject an accessible, layout-neutral floating link into built HTML only."""
    if 'data-pdf-download' in html:
        raise ValueError(f"PDF button already exists for {slug}")
    stylesheet = f'<link rel="stylesheet" href="{DOWNLOAD_CSS}">'
    alternate = f'<link rel="alternate" type="application/pdf" title="{escape(title, quote=True)} PDF" href="{PDF_NAME}">'
    html, head_count = re.subn(r"</head\s*>", lambda m: stylesheet + "\n" + alternate + "\n" + m.group(0), html, count=1, flags=re.I)
    filename = escape(f"xm-posts-{slug}.pdf", quote=True)
    button = (f'<a class="xm-pdf-download" data-pdf-download href="{PDF_NAME}" '
              f'download="{filename}" type="application/pdf" '
              f'aria-label="下载《{escape(title, quote=True)}》PDF 版本">'
              f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
              f'<path d="M12 3v12m0 0 5-5m-5 5-5-5M4 17v3h16v-3" /></svg>'
              f'<span>下载 PDF</span></a>')
    html, body_count = re.subn(r"<body\b[^>]*>", lambda m: m.group(0) + "\n" + button, html, count=1, flags=re.I)
    if head_count != 1 or body_count != 1:
        raise ValueError(f"Missing or malformed head/body for {slug}")
    return html


def wait_for_visual_assets(page, slug: str):
    """Eager-load all images before printing, including below-the-fold lazy assets."""
    missing = page.evaluate("""async () => {
      const images = [...document.images];
      images.forEach(img => { img.loading = 'eager'; });
      await document.fonts.ready;
      await Promise.all(images.map(img => img.decode().catch(() => null)));
      return images.filter(img => !img.complete || img.naturalWidth === 0)
        .map(img => img.getAttribute('src'));
    }""")
    if missing:
        raise RuntimeError(f"{slug}: image assets failed to load: {missing}")



CACHE_FORMAT = 1


def inspect_pdf(pdf: bytes, slug: str) -> int:
    """Validate both freshly rendered and restored PDFs before publishing."""
    if not pdf.startswith(b"%PDF-") or len(pdf) < 4096:
        raise ValueError(f"{slug}: invalid or unexpectedly empty PDF")
    reader = PdfReader(BytesIO(pdf))
    pages = len(reader.pages)
    if pages < 2 or not (reader.pages[0].extract_text() or "").strip():
        raise ValueError(f"{slug}: empty or unsearchable document")
    return pages


class PdfCache:
    """Best-effort untrusted cache. Corrupt/stale entries trigger re-rendering."""

    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.manifest_path = self.directory / "manifest.json"
        self.entries = {}
        try:
            manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if manifest.get("format") == CACHE_FORMAT and isinstance(manifest.get("entries"), dict):
                self.entries = manifest["entries"]
        except (OSError, ValueError, AttributeError):
            pass

    def pdf_path(self, slug: str) -> Path:
        # The post registry validates unique lowercase kebab-case slugs.
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError(f"Invalid PDF cache slug: {slug!r}")
        return self.directory / "pdfs" / (slug + ".pdf")

    def restore(self, slug: str, expected_fingerprint: str) -> tuple[bytes, int] | None:
        entry = self.entries.get(slug)
        if not isinstance(entry, dict) or entry.get("fingerprint") != expected_fingerprint:
            return None
        try:
            payload = self.pdf_path(slug).read_bytes()
            if len(payload) != entry.get("bytes"):
                raise ValueError("byte count mismatch")
            if sha256(payload).hexdigest() != entry.get("sha256"):
                raise ValueError("SHA-256 mismatch")
            pages = inspect_pdf(payload, slug)
            if pages != entry.get("pages"):
                raise ValueError("page count mismatch")
            return payload, pages
        except Exception as exc:
            # pypdf may raise library-specific parsing errors for damaged
            # cache bytes. Cache failures must never block fresh rendering.
            print(f"PDF CACHE INVALID {slug}: {exc}; rebuilding", flush=True)
            return None

    def store(self, slug: str, input_fingerprint: str, pdf: bytes, pages: int) -> None:
        target = self.pdf_path(slug)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(pdf)
        self.entries[slug] = {
            "fingerprint": input_fingerprint,
            "sha256": sha256(pdf).hexdigest(),
            "bytes": len(pdf),
            "pages": pages,
        }

    def save(self, active_slugs: set[str] | None = None) -> None:
        if active_slugs is not None:
            for slug in set(self.entries) - active_slugs:
                if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                    self.pdf_path(slug).unlink(missing_ok=True)
                del self.entries[slug]
        self.directory.mkdir(parents=True, exist_ok=True)
        pending = self.manifest_path.with_suffix(".tmp")
        pending.write_text(
            json.dumps({"format": CACHE_FORMAT, "entries": self.entries},
                       indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        pending.replace(self.manifest_path)


def export(out: Path, base_url: str = DEFAULT_URL, only: str | None = None,
           cache_dir: Path | None = None, force: bool = False) -> list[dict]:
    out = out.resolve()
    _, posts = data(ROOT)
    all_published = [p for p in posts if p["status"] == "published"]
    published = all_published
    if only:
        published = [p for p in published if p["slug"] == only]
        if len(published) != 1:
            raise ValueError(f"No unique published post with slug {only!r}")
    if not (out / "index.html").is_file():
        raise FileNotFoundError("Build site first: python scripts/build_site.py")

    cache = PdfCache(cache_dir or ROOT / ".pdf-cache")
    report = []
    # Playwright's driver is inexpensive compared with launching Chromium.
    # Start Chromium lazily only on the first cache miss.
    with sync_playwright() as playwright:
        browser = None
        page = None
        try:
            for p in published:
                directory = out / article_url(p)
                html_path = directory / "index.html"
                pdf_path = directory / PDF_NAME
                if not html_path.is_file():
                    raise FileNotFoundError(html_path)
                public_url = base_url.rstrip("/") + "/" + article_url(p)
                input_fingerprint = fingerprint(ROOT, out, directory, public_url)
                cached = None if force else cache.restore(p["slug"], input_fingerprint)
                if cached is not None:
                    pdf, page_count = cached
                    outcome = "cached"
                else:
                    if browser is None:
                        browser = playwright.chromium.launch()
                        context = browser.new_context(
                            viewport={"width": 1280, "height": 900},
                            device_scale_factor=1, locale="zh-CN",
                        )
                        page = context.new_page()
                        page.emulate_media(
                            media="print", color_scheme="light", reduced_motion="reduce"
                        )
                    # Local build only: never load an older public deployment.
                    page.goto(html_path.as_uri(), wait_until="load", timeout=45000)
                    wait_for_visual_assets(page, p["slug"])
                    # Preserve working links inside the offline PDF.
                    page.evaluate("""base => {
                      for (const a of document.querySelectorAll('a[href]')) {
                        const raw = a.getAttribute('href');
                        if (raw && !raw.startsWith('#') &&
                            !/^[a-z][a-z0-9+.-]*:/i.test(raw) && !raw.startsWith('//')) {
                          a.href = new URL(raw, base).href;
                        }
                      }
                    }""", public_url)
                    page.add_style_tag(content=PRINT_CSS)
                    pdf = page.pdf(
                        format="A4", print_background=True, prefer_css_page_size=True,
                        display_header_footer=True,
                        header_template="<span></span>",
                        footer_template=(
                            '<div style="width:100%;text-align:center;'
                            'font:8px Arial,sans-serif;color:#889998">'
                            '<span class="pageNumber"></span> / '
                            '<span class="totalPages"></span></div>'
                        ),
                        margin={
                            "top": "12mm", "right": "12mm",
                            "bottom": "16mm", "left": "12mm"
                        },
                    )
                    page_count = inspect_pdf(pdf, p["slug"])
                    cache.store(p["slug"], input_fingerprint, pdf, page_count)
                    outcome = "rendered"

                pdf_path.write_bytes(pdf)
                # Every build starts from clean source HTML. Even a cache hit must
                # insert the exact same layout-neutral download button.
                original_html = html_path.read_text(encoding="utf-8")
                html_path.write_text(
                    with_download_link(original_html, p["title"], p["slug"]),
                    encoding="utf-8",
                )
                report.append({
                    "slug": p["slug"], "pdf": str(pdf_path.relative_to(out)),
                    "bytes": len(pdf), "pages": page_count, "cache": outcome,
                })
                print(
                    f"PDF {outcome.upper()} {p['slug']}: "
                    f"{page_count} pages / {len(pdf):,} bytes",
                    flush=True,
                )
            # Full builds prune unpublished/renamed entries; --only keeps them.
            cache.save(None if only else {p["slug"] for p in all_published})
        finally:
            if browser is not None:
                browser.close()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--base-url", default=DEFAULT_URL)
    parser.add_argument("--only", help="Render one published slug for local inspection")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".pdf-cache")
    parser.add_argument("--force", action="store_true", help="Ignore cached PDFs and re-render")
    args = parser.parse_args()
    report = export(args.output, base_url=args.base_url, only=args.only,
                    cache_dir=args.cache_dir, force=args.force)
    print(json.dumps({
        "pdf_count": len(report),
        "cached": sum(x["cache"] == "cached" for x in report),
        "rendered": sum(x["cache"] == "rendered" for x in report),
        "total_bytes": sum(x["bytes"] for x in report),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
