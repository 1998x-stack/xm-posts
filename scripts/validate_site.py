#!/usr/bin/env python3
"""Fail closed for missing links, articles, skills or forbidden production copy."""
from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
import importlib.util,json,sys
from urllib.parse import urlparse,urljoin,unquote
from build_site import ROOT,data,DEFAULT_URL,article_url
from sync_skills import run as check_mirrors

BAD_COPY=['原创图解 · 单文件离线 HTML','用直觉 → 图示 → 数学 → 工程实现，理解残差网络 · 参考 Colah 风格，非原文翻译','原创教程 · 单 HTML 文件','参考 Colah 风格，非原文翻译','原创 SVG，可在浏览器内放大','图形均为独立绘制的 SVG，可无损放大','文章中的教学简化已单独注明']

def source_articles(root=ROOT):
    spec=importlib.util.spec_from_file_location('upstream_validator',root/'skills/olah-style-paper-posts/scripts/validate.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    _,posts=data(root)
    for p in posts:
        if p['status']!='published':continue
        f=root/'posts'/p['category']/p['slug']/'index.html'
        article=f.read_text(encoding='utf-8')
        for bad in BAD_COPY:
            assert bad not in article,f'Forbidden production text: {bad} in {f}'
        result=mod.validate(f)
        assert result['pass'],result
        assert (f.parent/'evidence.json').exists()
        assert len(list((f.parent/'assets').glob('*.svg'))) >= 3,'Need multiple standalone SVGs'
        print('ARTICLE OK',p['slug'],result['counts'])


def published_site(out:Path,base:str=DEFAULT_URL):
    cats,posts=data(ROOT)
    pub=[p for p in posts if p['status']=='published']
    expect=['index.html','archive/index.html','404.html','sitemap.xml','feed.xml','posts.json','robots.txt']+[f'categories/{c["slug"]}/index.html' for c in cats]+[article_url(p)+'index.html' for p in pub]
    for f in expect:assert (out/f).is_file(),f'Missing output: {f}'
    sitemap=(out/'sitemap.xml').read_text(encoding='utf-8')
    for p in pub:assert article_url(p) in sitemap,p
    for p in posts:
        if p['status']=='draft':assert article_url(p) not in sitemap,f'Leaked draft {p}'
    bad=[]
    for path in out.rglob('*.html'):
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        if len(soup.select('h1')) != 1:bad.append(f'{path}: expected 1 H1')
        if not soup.find('main'):bad.append(f'{path}: no main')
        ids=[x.get('id') for x in soup.select('[id]')]
        if len(ids)!=len(set(ids)):bad.append(f'{path}: duplicate ids')
        for link in soup.select('a[href],link[href],script[src],img[src]'):
            href=link.get('href') or link.get('src') or ''
            if not href or href.startswith(('#','mailto:','tel:','data:','javascript:')):continue
            parsed=urlparse(href)
            if parsed.scheme or href.startswith('//'):continue
            dest=(path.parent/unquote(parsed.path)).resolve()
            if dest.is_dir():dest/= 'index.html'
            if not dest.is_file():bad.append(f'broken link: {path.relative_to(out)} -> {href}')
        if path.parent != out and path.name=='index.html' and 'posts' in path.parts:
            if 'source-code' in path.name:bad.append('never')
    assert not bad,'\n'.join(bad)
    assert not any(out.rglob('*.py')) and not any(out.rglob('SKILL.md')) and not any(out.rglob('README.md')),'Non-public tooling leaked into site'
    print('SITE OK',len(list(out.rglob('*.html'))),'HTML pages and',len(pub),'posts')

if __name__=='__main__':
    check_mirrors(check=True)
    source_articles()
    published_site(ROOT/'_site')
