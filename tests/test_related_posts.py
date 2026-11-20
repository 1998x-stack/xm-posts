"""Regression checks for the generated related-reading section."""
from pathlib import Path
import sys

from bs4 import BeautifulSoup
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_site import build, data, DEFAULT_URL
from related_posts import (
    choose_related, enrich_article_related, load_reading_paths, MAX_CARDS
)


def corpus():
    _, posts = data(ROOT)
    published = [post for post in posts if post['status'] == 'published']
    return published, load_reading_paths(ROOT, published)


def test_editorial_paths_reference_published_posts_only():
    posts, routes = corpus()
    assert len(routes) >= 20
    slugs = {post['slug'] for post in posts}
    assert all(len(route['posts']) == len(set(route['posts'])) for route in routes)
    assert all(set(route['posts']) <= slugs for route in routes)


def test_recommendations_are_relevant_deterministic_and_distinct():
    posts, routes = corpus()
    by_slug = {post['slug']: post for post in posts}
    for post in posts:
        first = choose_related(post, posts, routes)
        again = choose_related(post, posts, routes)
        targets = [card['post']['slug'] for card in first]
        assert targets == [card['post']['slug'] for card in again]
        assert len(targets) == len(set(targets))
        assert 0 <= len(targets) <= MAX_CARDS
        assert post['slug'] not in targets
        for target in targets:
            article = by_slug[target]
            assert (ROOT / 'posts' / article['category']
                    / article['slug'] / article['cover']['src']).is_file()

    assert 'multi-head-attention' in [
        card['post']['slug'] for card in choose_related(by_slug['transformer'], posts, routes)
    ]
    assert 'alphago' in [
        card['post']['slug'] for card in choose_related(by_slug['mcts'], posts, routes)
    ]
    # An isolated storage-system article should not get an unrelated ML tree card.
    assert choose_related(by_slug['b-plus-tree'], posts, routes) == []


def test_recommender_never_leaks_drafts_or_alone_category():
    published = [
        {'slug':'a', 'category':'test', 'topic':'one', 'tags':['isolated'],
         'cover':{'src':'assets/a.svg'}},
        {'slug':'b', 'category':'test', 'topic':'two', 'tags':['unrelated'],
         'cover':{'src':'assets/b.svg'}},
    ]
    assert choose_related(published[0], published, []) == []
    assert choose_related(published[0], published, [{'posts':['a','draft'], 'title':'bad'}]) == []
    assert choose_related({**published[0], 'slug':'draft'}, published, []) == []


def test_generated_article_links_images_and_semantics(tmp_path):
    published, routes = corpus()
    site = tmp_path / 'site'
    build(ROOT, site, DEFAULT_URL)
    cards_found = 0
    for post in published:
        path = site / 'posts' / post['category'] / post['slug'] / 'index.html'
        soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        section = soup.select_one('[data-xm-related-reading]')
        expected = choose_related(post, published, routes)
        if not expected:
            assert section is None
            continue
        cards_found += 1
        assert section is not None
        assert section.find_parent('main') is not None
        assert len(soup.select('[data-xm-related-reading]')) == 1
        assert len(section.select('.xm-related-card')) == len(expected)
        assert soup.select_one('link[href="../../../assets/related-posts.css"]')
        assert len(soup.select('h1')) == 1
        for anchor, card in zip(section.select('.xm-related-card'), expected):
            target = card['post']
            assert anchor['href'] == '../../../posts/{}/{}/'.format(
                target['category'], target['slug'])
            assert anchor.select_one('img')['src'] == (
                anchor['href'] + target['cover']['src'])
            assert target['title'] in anchor.get_text(' ', strip=True)
            assert (path.parent / anchor['href'] / 'index.html').resolve().is_file()
    assert cards_found >= len(published) - 2
    assert (site / 'assets/related-posts.css').is_file()


def test_markup_is_idempotent():
    published, routes = corpus()
    current = next(p for p in published if p['slug'] == 'transformer')
    source = '<!doctype html><html><head></head><body><main><h1>测试</h1></main></body></html>'
    first = enrich_article_related(source, current, published, routes)
    assert first.count('data-xm-related-reading') == 1
    assert first.count('related-posts.css') == 1
    assert enrich_article_related(first, current, published, routes) == first


def test_invalid_reading_path_fails_closed(tmp_path):
    folder = tmp_path / 'content'
    folder.mkdir()
    (folder / 'reading_paths.json').write_text(
        '[{"id":"bad","title":"bad","posts":["published","draft"]}]',
        encoding='utf-8')
    with pytest.raises(AssertionError, match='unpublished'):
        load_reading_paths(tmp_path, [{'slug':'published'}])
