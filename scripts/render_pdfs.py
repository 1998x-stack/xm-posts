#!/usr/bin/env python3
"""Render one downloadable PDF for every *published* article, without rewriting source HTML.

Run after scripts/build_site.py. Uses the browser's existing print CSS, so inline
SVG and MathML remain browser-rendered; the download control is injected only
into generated _site/ HTML after the PDF is successfully written.
"""
from __future__ import annotations

import argparse
from io import BytesIO
from html import escape
import json
from pathlib import Path
import re

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


def export(out: Path, base_url: str = DEFAULT_URL, only: str | None = None) -> list[dict]:
    out = out.resolve()
    _, posts = data(ROOT)
    published = [p for p in posts if p["status"] == "published"]
    if only:
        published = [p for p in published if p["slug"] == only]
        if len(published) != 1:
            raise ValueError(f"No unique published post with slug {only!r}")
    if not (out / "index.html").is_file():
        raise FileNotFoundError("Build site first: python scripts/build_site.py")
    report = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1, locale="zh-CN")
        page = context.new_page()
        page.emulate_media(media="print", color_scheme="light", reduced_motion="reduce")
        try:
            for p in published:
                directory = out / article_url(p)
                html_path = directory / "index.html"
                pdf_path = directory / PDF_NAME
                if not html_path.is_file():
                    raise FileNotFoundError(html_path)
                # Load local built assets, never fetch an old remote deployment.
                page.goto(html_path.as_uri(), wait_until="load", timeout=45000)
                wait_for_visual_assets(page, p["slug"])
                # Preserve working public hyperlinks inside the offline PDF.
                public_url = base_url.rstrip("/") + "/" + article_url(p)
                page.evaluate("""base => {
                  for (const a of document.querySelectorAll('a[href]')) {
                    const raw = a.getAttribute('href');
                    if (raw && !raw.startsWith('#') && !/^[a-z][a-z0-9+.-]*:/i.test(raw) && !raw.startsWith('//')) {
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
                        '<span class="pageNumber"></span> / <span class="totalPages"></span></div>'
                    ),
                    margin={"top": "12mm", "right": "12mm", "bottom": "16mm", "left": "12mm"},
                )
                if not pdf.startswith(b"%PDF-") or len(pdf) < 4096:
                    raise RuntimeError(f"{p['slug']}: invalid or unexpectedly empty PDF")
                reader = PdfReader(BytesIO(pdf))
                page_count = len(reader.pages)
                if page_count < 2 or not (reader.pages[0].extract_text() or "").strip():
                    raise RuntimeError(f"{p['slug']}: empty or unsearchable document")
                pdf_path.write_bytes(pdf)
                # Inject the link only after its downloadable file exists.
                original_html = html_path.read_text(encoding="utf-8")
                html_path.write_text(with_download_link(original_html, p["title"], p["slug"]), encoding="utf-8")
                report.append({"slug": p["slug"], "pdf": str(pdf_path.relative_to(out)), "bytes": len(pdf), "pages": page_count})
                print(f"PDF OK {p['slug']}: {page_count} pages / {len(pdf):,} bytes", flush=True)
        finally:
            browser.close()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    parser.add_argument("--base-url", default=DEFAULT_URL)
    parser.add_argument("--only", help="Render only a single published slug for local inspection")
    args = parser.parse_args()
    report = export(args.output, base_url=args.base_url, only=args.only)
    print(json.dumps({"pdf_count": len(report), "total_bytes": sum(x["bytes"] for x in report)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
