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
