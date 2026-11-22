#!/usr/bin/env python3
"""Post-deployment smoke test against the *public* GitHub Pages site.

This supplements CI's local static-build/link checks. It fails if Pages still
serves the previous version, hides the related section, or serves broken assets.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from io import BytesIO
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ARTICLES = (
    'posts/architectures/transformer/',
    'posts/architectures/resnet/',
    'posts/reinforcement-learning/mcts/',
)
CSS = 'assets/related-posts.css'
C51 = 'posts/reinforcement-learning/c51/'


class ReadingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_related = False
        self.depth = 0
        self.count = 0
        self.links: list[str] = []
        self.images: list[str] = []
        self.stylesheets: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'link' and a.get('rel') == 'stylesheet':
            self.stylesheets.append(a.get('href', ''))
        if tag == 'section' and 'data-xm-related-reading' in a:
            self.in_related = True
            self.depth = 1
            self.count += 1
            return
        if not self.in_related:
            return
        if tag not in ('img', 'input', 'source', 'meta', 'link', 'br', 'hr'):
            self.depth += 1
        if tag == 'a' and 'xm-related-card' in a.get('class', '').split():
            self.links.append(a.get('href', ''))
        if tag == 'img':
            self.images.append(a.get('src', ''))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self.in_related:
            return
        if tag not in ('img', 'input', 'source', 'meta', 'link', 'br', 'hr'):
            self.depth -= 1
            if self.depth <= 0:
                self.in_related = False
                self.depth = 0


def fetch(url: str) -> bytes:
    request = Request(url, headers={
        'User-Agent': 'xm-posts-deploy-qa/1.0',
        'Cache-Control': 'no-cache',
    })
    with urlopen(request, timeout=20) as result:
        if result.status != 200:
            raise AssertionError(f'Unexpected HTTP {result.status}: {url}')
        return result.read()



class C51Parser(HTMLParser):
    """Collect article navigation, formulas, SVG and downloadable PDF links."""
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.math_count = 0
        self.svg_count = 0
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a':
            self.links.append(a.get('href', ''))
        elif tag == 'img':
            self.images.append(a.get('src', ''))
        elif tag == 'math':
            self.math_count += 1
        elif tag == 'svg':
            self.svg_count += 1
        elif tag == 'h1':
            self.headings += 1


def verify_c51(base: str):
    """Verify the *deployed* C51 article, PDF, illustrations and site indexes.

    PDF parsing here complements (not replaces) the PR's full PDF and
    browser/visual checks; the deploy job installs pypdf for this step.
    """
    from pypdf import PdfReader

    url = urljoin(base, C51)
    parser = C51Parser()
    html = fetch(url).decode('utf-8')
    parser.feed(html)
    assert parser.headings == 1, f'{url}: expected one h1'
    assert parser.math_count >= 1, f'{url}: no MathML formulas'
    assert parser.svg_count >= 1, f'{url}: no inline SVG'
    assert 'C51' in html, f'{url}: wrong or stale article'

    pdf_url = urljoin(url, 'article.pdf')
    assert any(urljoin(url, href) == pdf_url for href in parser.links), (
        f'{url}: missing live PDF download link'
    )
    pdf = fetch(pdf_url)
    assert pdf.startswith(b'%PDF-') and len(pdf) > 10000, (
        f'{pdf_url}: missing or truncated PDF'
    )
    reader = PdfReader(BytesIO(pdf), strict=False)
    assert not reader.is_encrypted, f'{pdf_url}: encrypted PDF'
    assert len(reader.pages) >= 2, f'{pdf_url}: suspicious page count'
    extracted = ''.join(page.extract_text() or '' for page in reader.pages)
    assert len(extracted.strip()) >= 500, f'{pdf_url}: no readable text'

    for path in parser.images:
        if not path or path.startswith('data:'):
            continue
        target = urljoin(url, path)
        assert target.startswith(base), f'{url}: external illustration {path}'
        assert fetch(target), f'{url}: empty illustration {target}'

    for suffix in ('archive/', 'topics/', 'feed.xml', 'categories/reinforcement-learning/'):
        target = urljoin(base, suffix)
        data = fetch(target)
        assert data, f'{target}: empty index'

    # The archive is paginated (16 posts per page); C51 need not be on page 1.
    # Read the published archive pagination instead of assuming the first page
    # is a complete index. RSS is not paginated.
    import re
    archive = fetch(urljoin(base, 'archive/')).decode('utf-8')
    page_numbers = [int(n) for n in re.findall(r'archive/page/(\\d+)/', archive)]
    last_page = max([1, *page_numbers])
    assert last_page <= 100, f'Unexpected archive page count: {last_page}'
    found = 'posts/reinforcement-learning/c51/' in archive.lower()
    for page in range(2, last_page + 1):
        if found:
            break
        content = fetch(urljoin(base, f'archive/page/{page}/')).decode('utf-8')
        found = 'posts/reinforcement-learning/c51/' in content.lower()
    assert found, f'C51 missing from all {last_page} public archive pages'
    rss = fetch(urljoin(base, 'feed.xml')).decode('utf-8')
    assert 'posts/reinforcement-learning/c51/' in rss.lower(), 'C51 missing from RSS'
    print(f'PUBLIC C51 VERIFIED: HTML, MathML, SVG, PDF ({len(reader.pages)} pages), archive, topic and RSS')


def verify(base: str):
    verify_c51(base)
    stylesheet = fetch(urljoin(base, CSS))
    assert b'.xm-related-reading' in stylesheet, 'Missing related card stylesheet'
    for suffix in ARTICLES:
        url = urljoin(base, suffix)
        parser = ReadingParser()
        parser.feed(fetch(url).decode('utf-8'))
        assert parser.count == 1, f'{url}: expected one related reading section, got {parser.count}'
        assert 2 <= len(parser.links) <= 4, f'{url}: bad card count: {len(parser.links)}'
        assert len(parser.images) == len(parser.links), f'{url}: missing thumbnails'
        assert any(CSS in href for href in parser.stylesheets), f'{url}: missing CSS link'
        for path in parser.links + parser.images:
            dest = urljoin(url, path)
            assert dest.startswith(base), f'{url}: external or out-of-scope card: {path}'
            assert fetch(dest), f'{url}: empty target: {dest}'
        print(f'PUBLIC OK {suffix}: {len(parser.links)} cards, all links and SVGs return 200')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base-url', required=True)
    ap.add_argument('--attempts', type=int, default=8)
    ap.add_argument('--interval', type=int, default=12)
    args = ap.parse_args()
    base = args.base_url.rstrip('/') + '/'
    assert base.startswith('https://'), 'The post-deploy URL must be HTTPS'
    for attempt in range(1, args.attempts + 1):
        try:
            verify(base)
            print('PUBLIC SITE VERIFIED:', base)
            break
        except Exception as exc:
            print(f'Public verification attempt {attempt}/{args.attempts}: {exc}', flush=True)
            if attempt == args.attempts:
                raise
            time.sleep(args.interval)
