#!/usr/bin/env python3
"""Post-deployment smoke test against the *public* GitHub Pages site.

This supplements CI's local static-build/link checks. It fails if Pages still
serves the previous version, hides the related section, or serves broken assets.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import time
from urllib.parse import urljoin
from urllib.request import Request, urlopen

ARTICLES = (
    'posts/architectures/transformer/',
    'posts/architectures/resnet/',
    'posts/reinforcement-learning/mcts/',
)
CSS = 'assets/related-posts.css'


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


def verify(base: str):
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
