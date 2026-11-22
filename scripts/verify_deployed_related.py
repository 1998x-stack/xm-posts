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
from urllib.parse import urldefrag, urljoin
from xml.etree import ElementTree as ET
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



class ArchiveParser(HTMLParser):
    """Read article links and the explicit next-page link from one archive page."""
    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.next_href: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        values = dict(attrs)
        href = values.get('href', '')
        if href:
            self.links.append(href)
        rel = set((values.get('rel') or '').lower().split())
        if 'next' in rel:
            self.next_href = href


def archive_contains_c51(base: str, fetcher=None, max_pages: int = 100) -> int:
    """Follow rel=next until C51 is found or the published archive ends.

    Returns the number of pages visited. The traversal is deliberately based
    on the site's navigational contract, not on a guessed last-page link.
    """
    if max_pages < 1:
        raise ValueError('max_pages must be positive')
    fetch_page = fetch if fetcher is None else fetcher
    expected = urljoin(base, C51)
    current = urljoin(base, 'archive/')
    visited: set[str] = set()

    for _ in range(max_pages):
        if not current.startswith(base):
            raise AssertionError(f'Archive pagination escaped the site: {current}')
        if current in visited:
            raise AssertionError(f'Archive pagination loop detected at {current}')
        visited.add(current)

        parser = ArchiveParser()
        parser.feed(fetch_page(current).decode('utf-8'))
        for href in parser.links:
            candidate, _fragment = urldefrag(urljoin(current, href))
            if candidate.rstrip('/') == expected.rstrip('/'):
                return len(visited)

        if not parser.next_href:
            return 0
        next_url, _fragment = urldefrag(urljoin(current, parser.next_href))
        if not next_url.startswith(base):
            raise AssertionError(f'Archive next-page link escaped the site: {next_url}')
        if next_url in visited:
            raise AssertionError(f'Archive pagination loop detected at {next_url}')
        current = next_url

    raise AssertionError(f'Archive pagination exceeded the {max_pages}-page safety limit')


def feed_contains_c51(feed: bytes, base: str) -> bool:
    """Check the exact canonical C51 GUID in the complete RSS 2.0 feed."""
    root = ET.fromstring(feed)
    if root.tag != 'rss':
        raise AssertionError(f'Unexpected RSS root element: {root.tag}')
    expected = urljoin(base, C51)
    channel = root.find('channel')
    if channel is None:
        raise AssertionError('RSS feed is missing its channel')
    return any(
        (item.findtext('guid') or item.findtext('link')) == expected
        for item in channel.findall('item')
    )


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

    # Follow the explicit rel=next chain instead of guessing the final
    # page number from links that happen to be visible on page one.
    archive_pages = archive_contains_c51(base)
    assert archive_pages > 0, 'C51 missing from all linked public archive pages'
    rss = fetch(urljoin(base, 'feed.xml'))
    assert feed_contains_c51(rss, base), 'C51 missing from the complete public RSS feed'
    print(f'PUBLIC C51 VERIFIED: HTML, MathML, SVG, PDF ({len(reader.pages)} pages), archive ({archive_pages} pages), topic and RSS')


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
