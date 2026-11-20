"""Curated, deterministic reading suggestions for published article pages.

Only published manifest entries may appear. Ordered editorial paths take priority;
shared primary topics or unusually specific tags supply conservative fallbacks.
"""
from __future__ import annotations

from collections import Counter
from html import escape as html_escape
import json
from pathlib import Path
import re

MAX_CARDS = 4
RELATED_MARKER = 'data-xm-related-reading'
STYLESHEET = '../../../assets/related-posts.css'


def load_reading_paths(root: Path, published: list[dict]) -> list[dict]:
    routes = json.loads((root / 'content/reading_paths.json').read_text(encoding='utf-8'))
    allowed = {post['slug'] for post in published}
    assert isinstance(routes, list), 'Reading paths must be an array'
    ids = set()
    for route in routes:
        assert isinstance(route, dict), 'Invalid reading path'
        route_id, title, entries = route.get('id'), route.get('title'), route.get('posts')
        assert isinstance(route_id, str) and re.fullmatch(r'[a-z0-9-]+', route_id), route
        assert route_id not in ids, f'Duplicate reading path: {route_id}'
        ids.add(route_id)
        assert isinstance(title, str) and title.strip(), route
        assert isinstance(entries, list) and len(entries) >= 2, route
        assert len(set(entries)) == len(entries), f'Duplicate post in {route_id}'
        assert all(isinstance(slug, str) and slug in allowed for slug in entries), (
            f'{route_id} links a missing or unpublished post'
        )
    return routes


def choose_related(current: dict, published: list[dict], routes: list[dict],
                   limit: int = MAX_CARDS) -> list[dict]:
    """Choose up to four distinct, meaningful cards without random suggestions."""
    if limit <= 0:
        return []
    posts = {post['slug']: post for post in published}
    slug = current['slug']
    if slug not in posts:
        return []
    candidates = {}

    def offer(target_slug: str, score: float, kind: str, explanation: str):
        if target_slug == slug or target_slug not in posts:
            return
        existing = candidates.get(target_slug)
        if existing is None or score > existing['score']:
            candidates[target_slug] = {
                'post': posts[target_slug],
                'score': score,
                'kind': kind,
                'explanation': explanation,
            }

    # Nearby posts on an explicitly reviewed, ordered learning route win.
    for route in routes:
        steps = route['posts']
        if slug not in steps:
            continue
        pos = steps.index(slug)
        for distance in (1, 2):
            for direction in (1, -1):
                other = pos + distance * direction
                if not 0 <= other < len(steps):
                    continue
                kind = '继续深入' if direction > 0 else '补充基础'
                offer(steps[other], 20 - distance * 4 + (1 if direction > 0 else 0),
                      kind, route['title'])

    # Fallback needs a shared registered topic or a *specific* tag overlap.
    # Never recommend merely because two articles share a broad top-level category.
    tag_frequency = Counter(tag.casefold().strip()
                            for post in published for tag in set(post['tags']))
    our_tags = {tag.casefold().strip() for tag in current['tags']}
    for other in published:
        if other['slug'] == slug or other['slug'] in candidates:
            continue
        same_topic = (current['category'] == other['category']
                      and current['topic'] == other['topic'])
        common = our_tags & {tag.casefold().strip() for tag in other['tags']}
        specificity = sum(2.0 / max(1, tag_frequency[tag] - 1) for tag in common)
        if not same_topic and specificity < 3.0:
            continue
        if current['category'] != other['category'] and specificity < 4.0:
            continue
        offer(other['slug'], 4 + (4 if same_topic else 0) + min(specificity, 4.0),
              '同主题延伸' if same_topic else '相关概念',
              '同一个知识主题' if same_topic else '共享关键技术概念')

    ranking = sorted(candidates.values(),
                     key=lambda entry: (-entry['score'], entry['post']['slug']))
    return ranking[:min(limit, MAX_CARDS)]


def render_related(cards: list[dict]) -> str:
    if not cards:
        return ''
    rendered = []
    for entry in cards:
        post = entry['post']
        target = '../../../posts/{}/{}/'.format(post['category'], post['slug'])
        cover = target + post['cover']['src']
        kind = html_escape(entry['kind'])
        path = html_escape(entry['explanation'])
        rendered.append(
            '<a class="xm-related-card" href="{url}">'
            '<span class="xm-related-media"><img src="{cover}" alt="" loading="lazy" decoding="async"></span>'
            '<span class="xm-related-card-content">'
            '<span class="xm-related-label">{kind} <span aria-hidden="true">·</span> {path}</span>'
            '<strong class="xm-related-card-title">{title}</strong>'
            '<span class="xm-related-card-description">{subtitle}</span>'
            '<span class="xm-related-card-bottom">{minutes} 分钟阅读'
            '<span aria-hidden="true"> ↗</span></span>'
            '</span></a>'.format(
                url=html_escape(target, quote=True),
                cover=html_escape(cover, quote=True),
                kind=kind, path=path,
                title=html_escape(post['title']),
                subtitle=html_escape(post['subtitle']),
                minutes=post['reading_minutes'],
            )
        )
    return (
        '<section class="xm-related-reading" data-xm-related-reading '
        'aria-labelledby="xm-related-reading-heading">'
        '<div class="xm-related-header"><span class="xm-related-eyebrow">'
        'EXPLORE NEXT / 知识延伸</span>'
        '<h2 id="xm-related-reading-heading">接下来，读什么？</h2>'
        '<p>从当前知识点出发，沿着相关机制和学习路径继续探索。</p></div>'
        '<div class="xm-related-grid">' + ''.join(rendered) + '</div>'
        '</section>'
    )


def enrich_article_related(html: str, current: dict, published: list[dict],
                           routes: list[dict]) -> str:
    """Append inside the last article/main; keep original source HTML untouched."""
    if RELATED_MARKER in html:
        return html
    cards = choose_related(current, published, routes)
    block = render_related(cards)
    if not block:
        return html
    matches = list(re.finditer(r'</article\s*>', html, flags=re.IGNORECASE))
    if not matches:
        matches = list(re.finditer(r'</main\s*>', html, flags=re.IGNORECASE))
    if not matches:
        raise ValueError(f'Article {current["slug"]} lacks a closing article/main')
    end = matches[-1].start()
    html = html[:end] + '\n' + block + '\n' + html[end:]
    if not re.search(r'assets/related-posts\.css', html, re.IGNORECASE):
        link = '<link rel="stylesheet" href="' + STYLESHEET + '">'
        html, count = re.subn(r'</head\s*>', lambda m: link + '\n' + m.group(0),
                              html, count=1, flags=re.IGNORECASE)
        if count != 1:
            raise ValueError(f'Article {current["slug"]} lacks </head>')
    return html
