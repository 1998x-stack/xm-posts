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
    assert len(cats)==8
    assert {'resnet','transformer','svm'} <= {p['slug'] for p in posts if p['status']=='published'}
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
