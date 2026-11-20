"""Whole-site math coverage and information-architecture regression checks.

All checks use actual published manifests. Rendering geometry is covered by the
existing per-article Playwright Chromium workflow, not by HTML parsing.
"""
from pathlib import Path
import sys
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_site import data,build,DEFAULT_URL,article_url

def test_all_published_articles_have_semantic_math():
    categories,posts=data(ROOT)
    published=[p for p in posts if p['status']=='published']
    assert len(published)>=19
    assert len(categories)>=10
    for p in published:
        file=ROOT/'posts'/p['category']/p['slug']/'index.html'
        html=file.read_text(encoding='utf-8')
        soup=BeautifulSoup(html,'html.parser')
        math=soup.find_all('math')
        assert math,f'Missing native MathML: {p["slug"]}'
        assert all(m.get('aria-label') or m.get('aria-labelledby') for m in math),p['slug']
        assert not soup.select('svg math'),f'MathML nested inside SVG: {p["slug"]}'
        assert '<mi>¤</mi>' not in html,f'Leaked conversion marker: {p["slug"]}'
        for formula in soup.select('math[display="block"]'):
            region=formula.find_parent(attrs={'data-math-scroll':True})
            if region is None:
                region=formula.find_parent(class_=['math-scroll','eq-scroll'])
            assert region is not None and region.get('tabindex')=='0',p['slug']
            assert region.get('role')=='region',p['slug']
        for frac in soup.select('math mfrac'):
            assert len(frac.find_all(recursive=False))==2,p['slug']
        if p['slug'] not in {'svm','alexnet'}:
            assert soup.select('[data-math-enhanced]'),p['slug']
        for block in soup.select('div.eq, div.equation, div.formula, div.math, div.keyformula'):
            assert block.find('math'),f'Flat formula block: {p["slug"]}'
    rope=BeautifulSoup((ROOT/'posts/architectures/rope/index.html').read_text(encoding='utf-8'),'html.parser')
    assert len(rope.select('math mtable mtr'))>=2
    transformer=BeautifulSoup((ROOT/'posts/architectures/transformer/index.html').read_text(encoding='utf-8'),'html.parser')
    assert transformer.select('math msqrt msub'), 'Expected correctly scripted attention denominator'

def test_site_study_routes_paper_sources_and_article_metadata(tmp_path):
    cats,posts=data(ROOT)
    published=[p for p in posts if p['status']=='published']
    out=tmp_path/'site'
    build(ROOT,out,DEFAULT_URL)
    home=BeautifulSoup((out/'index.html').read_text(encoding='utf-8'),'html.parser')
    cards=home.select('[data-post-card]')
    assert len(cards)==len(published)
    assert len(home.select('#reading-paths .learning-card'))>=4
    for link in home.select('#reading-paths a'):
        assert (out/link['href'].rstrip('/')/'index.html').is_file(),link
    assert len(home.select('[data-post-card] .paper-source'))==len(published)
    for p in published:
        path=out/article_url(p)/'index.html'
        assert path.exists(),p['slug']
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        canonical=DEFAULT_URL+article_url(p)
        cs=soup.select('link[rel="canonical"]')
        assert len(cs)==1 and cs[0].get('href')==canonical,p['slug']
        urls=soup.select('meta[property="og:url"]')
        assert len(urls)==1 and urls[0].get('content')==canonical,p['slug']
        for prop in ['og:title','og:description','og:type']:
            assert len(soup.select('meta[property="'+prop+'"]'))==1,(p['slug'],prop)
        assert soup.select('meta[name="twitter:card"]'),p['slug']

def test_readme_is_complete_for_published_articles():
    _,posts=data(ROOT)
    text=(ROOT/'README.md').read_text(encoding='utf-8')
    for p in posts:
        if p['status']=='published':
            assert f'posts/{p["category"]}/{p["slug"]}/' in text,p['slug']
    assert 'posts/reasoning/' in text
