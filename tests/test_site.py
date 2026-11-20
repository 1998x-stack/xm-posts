from pathlib import Path
import json,sys
import pytest
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import data,build,DEFAULT_URL
from sync_skills import content_map,MIRRORS,SOURCE
from validate_site import source_articles,published_site


def test_manifest_and_taxonomy():
    cats,posts=data(ROOT)
    assert len(cats)>=9 and 'reasoning' in {c['slug'] for c in cats}
    assert {'resnet','transformer','svm','ppo','self-consistency'} <= {p['slug'] for p in posts if p['status']=='published'}
    for c in cats:assert (ROOT/'posts'/c['slug']/'README.md').is_file()


def test_skill_mirrors_are_real_copies():
    baseline=content_map(SOURCE)
    assert len(baseline)>=15
    for mirror in MIRRORS:
        assert mirror.is_dir() and not mirror.is_symlink()
        assert content_map(mirror)==baseline


def test_article_quality_and_no_process_chatter():
    source_articles()
    for slug,n in [('resnet',10),('transformer',13)]:
        s=BeautifulSoup((ROOT/'posts/architectures'/slug/'index.html').read_text(encoding='utf-8'),'html.parser')
        assert len(s.select('h1'))==1
        assert len(s.select('svg'))==n

def test_build_and_output(tmp_path):
    output=tmp_path/'site'
    build(ROOT,output,DEFAULT_URL)
    published_site(output)
    text=(output/'posts.json').read_text(encoding='utf-8')
    assert len(json.loads(text))==len([p for p in data(ROOT)[1] if p['status']=='published'])
    assert 'draft' not in text
    assert 'categories/architectures/' in (output/'index.html').read_text()


def test_no_placeholder_published(tmp_path):
    _,posts=data(ROOT)
    assert all(p['status'] in {'draft','published'} for p in posts)
    assert not (ROOT/'posts/foundations/index.html').exists()


def test_taxonomy_topic_placeholders_are_not_published(tmp_path):
    cats, posts = data(ROOT)
    by_slug = {c['slug']: c for c in cats}
    assert {'retrieval-rag', 'agents'} <= set(by_slug)
    planned = {
        'retrieval-rag': ['embedding-retrieval', 'ann', 'reranking', 'rag', 'grounding', 'hybrid-search'],
        'agents': ['react', 'planning', 'tool-calling', 'memory', 'agent-evaluation'],
        'training': ['distributed-training', 'training-parallelism', 'mixed-precision', 'checkpointing'],
        'architectures': ['moe', 'state-space-models', 'efficient-attention', 'long-context-architectures'],
        'inference': ['request-scheduling', 'continuous-batching', 'prefix-caching', 'speculative-decoding', 'prefill-decode-disaggregation'],
        'systems': ['gpu-memory', 'compiler-kernel-optimization', 'distributed-communication', 'performance-modeling'],
    }
    for category, slugs in planned.items():
        assert (ROOT / 'posts' / category / 'README.md').is_file()
        for slug in slugs:
            stub = ROOT / 'posts' / category / '_topics' / slug / 'README.md'
            assert stub.is_file(), stub
            assert not (stub.parent / 'index.html').exists()
    assert not [p for p in posts if p['category'] == 'retrieval-rag']
    assert any(p['category'] == 'agents' and p['slug'] == 'react' and p['status'] == 'published' for p in posts)
    output = tmp_path / 'site'
    build(ROOT, output, DEFAULT_URL)
    for slug in ('retrieval-rag', 'agents'):
        assert (output / 'categories' / slug / 'index.html').exists()
        if slug == 'retrieval-rag':
            assert not (output / 'posts' / slug).exists()
    assert (output / 'posts' / 'agents' / 'react' / 'index.html').is_file()
    assert not any('_topics' in path.parts for path in output.rglob('*'))


def test_second_level_taxonomy_and_deep_links(tmp_path):
    categories,posts=data(ROOT)
    assert len(categories)>=13
    assert sum(len(c['topics']) for c in categories)>=70
    assert {'retrieval-rag','agents'} <= {c['slug'] for c in categories}
    for c in categories:
        valid={t['slug'] for t in c['topics']}
        assert valid and len(valid)==len(c['topics'])
        for p in [p for p in posts if p['category']==c['slug']]:
            assert p['topic'] in valid, p['slug']
    output=tmp_path/'taxonomysite'
    build(ROOT,output,DEFAULT_URL)
    index=BeautifulSoup((output/'topics/index.html').read_text(encoding='utf-8'),'html.parser')
    assert len(index.select('.taxonomy-group'))==len(categories)
    assert len(index.select('.taxonomy-links a'))==sum(len(c['topics']) for c in categories)
    for c in categories:
        category_page=BeautifulSoup((output/'categories'/c['slug']/'index.html').read_text(encoding='utf-8'),'html.parser')
        assert len(category_page.select('.topic-section'))==len(c['topics'])
        assert len(category_page.select('.topic-jumps a'))==len(c['topics'])
        for topic in c['topics']:
            assert category_page.select_one(f'#topic-{topic["slug"]}')
        assert len(category_page.select('.post-card'))==sum(p['category']==c['slug'] and p['status']=='published' for p in posts)
    assert len(index.select('.taxonomy-links small'))>=70
    assert 'topics/' in (output/'sitemap.xml').read_text(encoding='utf-8')
    assert DEFAULT_URL in (output/'404.html').read_text(encoding='utf-8')
    published_site(output)


def test_home_editorial_discovery_and_manifest_consistency(tmp_path):
    categories, posts = data(ROOT)
    output = tmp_path / 'editorial-home'
    build(ROOT, output, DEFAULT_URL)
    home = BeautifulSoup((output / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    published = [p for p in posts if p['status'] == 'published']
    active = [c for c in categories if any(p['category'] == c['slug'] for p in published)]
    planned = [c for c in categories if c not in active]
    assert len(home.select('h1')) == 1
    assert home.select_one('.hero-feature a[href*="transformer/"]')
    assert len(home.select('.research-card')) == len(active)
    assert len(home.select('.planned-fields a')) == len(planned)
    assert len(home.select('.spotlight-card')) >= 2
    assert len(home.select('.route-card')) >= 4
    assert len(home.select('[data-post-card]')) == len(published)
    assert home.select_one('[data-search-input]')
    assert len(home.select('[data-category-filter] option')) == len(active) + 1
    assert home.select_one('[data-load-more]')
    assert home.select_one('[data-menu-toggle][aria-expanded="false"]')
    assert home.select_one('#latest') and home.select_one('#discover')
    indexed = {el.select_one('.index-main h3').get_text(strip=True) for el in home.select('.index-card')}
    assert indexed == {p['title'] for p in published}
    # A planned category must not masquerade as a published article collection.
    assert all(c['slug'] not in {x['data-category'] for x in home.select('[data-post-card]')} for c in planned)


def test_unique_article_specific_cover_manifest_and_rendering(tmp_path):
    from hashlib import sha256

    categories, posts = data(ROOT)
    published = [p for p in posts if p['status'] == 'published']
    assert len(published) >= 60
    assert all('cover' in p for p in published)
    assert all((ROOT / 'posts' / p['category'] / p['slug'] / p['cover']['src']).is_file() for p in published)
    assert len({p['cover']['caption'] for p in published}) == len(published)
    diagram_digests = {
        sha256((ROOT / 'posts' / p['category'] / p['slug'] / p['cover']['src']).read_bytes()).hexdigest()
        for p in published
    }
    assert len(diagram_digests) == len(published), "Every cover should be a distinct scientific diagram"

    output = tmp_path / 'cover-site'
    build(ROOT, output, DEFAULT_URL)
    for c in categories:
        page = BeautifulSoup((output / 'categories' / c['slug'] / 'index.html').read_text(encoding='utf-8'), 'html.parser')
        cards = page.select('.post-card .cover-figure')
        matching = [p for p in published if p['category'] == c['slug']]
        assert len(cards) == len(matching)
        assert 'Observe → Derive → Verify' not in str(page)
        for card in cards:
            image = card.select_one('.cover-illustration img')
            assert image and image.get('alt') and image.get('loading') == 'lazy'
            assert image.get('src','').startswith('../../posts/' + c['slug'] + '/')
            assert (output / 'categories' / c['slug'] / image['src']).resolve().is_file()
            assert card.select_one('.cover-caption').get_text(strip=True) == image['alt']

    home = BeautifulSoup((output / 'index.html').read_text(encoding='utf-8'), 'html.parser')
    assert len(home.select('.index-image-link img')) == len(published)
    assert len(home.select('.spotlight-cover-link img')) >= 2
    assert home.select_one('.hero-feature .feature-art--cover img')
    for p in published:
        thumb = home.select_one(f'.index-card a[href="posts/{p["category"]}/{p["slug"]}/"] img')
        assert thumb and thumb['src'].removeprefix('./') == 'posts/' + p['category'] + '/' + p['slug'] + '/' + p['cover']['src']
    assert 'Observe → Derive → Verify' not in home.get_text()


def test_archive_has_a_distinct_valid_svg_thumbnail_for_every_published_post(tmp_path):
    _, posts = data(ROOT)
    published = [p for p in posts if p['status'] == 'published']
    output = tmp_path / 'archive-with-covers'
    build(ROOT, output, DEFAULT_URL)
    page = output / 'archive' / 'index.html'
    archive = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
    entries = archive.select('.timeline > li.archive-entry')
    assert len(entries) == len(published)
    assert len(archive.select('h1')) == 1
    assert 'Observe → Derive → Verify' not in str(archive)
    images = archive.select('.archive-cover img.article-cover-thumb')
    assert len(images) == len(published)
    urls = [im['src'] for im in images]
    assert len(set(urls)) == len(urls)
    by_slug = {p['slug']: p for p in published}
    found = set()
    for entry in entries:
        figure_link = entry.select_one('a.archive-cover')
        img = figure_link.select_one('img') if figure_link else None
        title_link = entry.select_one('.archive-entry-copy h2 a')
        date = entry.select_one('time.timeline-date[datetime]')
        assert figure_link and img and title_link and date
        assert figure_link['href'] == title_link['href']
        assert img.get('loading') == 'lazy'
        assert img.get('decoding') == 'async'
        assert img['src'].endswith('.svg')
        assert img['src'].startswith('../posts/')
        assert (page.parent / img['src']).resolve().is_file()
        slug = title_link['href'].rstrip('/').split('/')[-1]
        post = by_slug[slug]
        found.add(slug)
        assert img['src'] == '../posts/' + post['category'] + '/' + slug + '/' + post['cover']['src']
        assert figure_link['title'] == post['cover']['caption']
        assert figure_link['aria-label'] == '阅读 ' + post['title']
        assert date['datetime'] == post['published']
    assert found == set(by_slug)
