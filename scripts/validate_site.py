#!/usr/bin/env python3
"""Fail closed for missing links, articles, skills or forbidden production copy."""
from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
import argparse
import importlib.util,json,sys,re
from urllib.parse import urlparse,urljoin,unquote
from build_site import ROOT,data,DEFAULT_URL,article_url,archive_page_count,archive_page_url,ARCHIVE_PAGE_SIZE,HOME_PAGE_SIZE
from sync_skills import run as check_mirrors

BAD_COPY=['原创图解 · 单文件离线 HTML','用直觉 → 图示 → 数学 → 工程实现，理解残差网络 · 参考 Colah 风格，非原文翻译','原创教程 · 单 HTML 文件','参考 Colah 风格，非原文翻译','原创 SVG，可在浏览器内放大','图形均为独立绘制的 SVG，可无损放大','文章中的教学简化已单独注明']



def check_article_layout(html: str, filename: str) -> None:
    """Catch document-mode, heading-order, print and reduced-motion regressions."""
    doctypes = re.findall(r'<!doctype\s+html\s*>', html, re.IGNORECASE)
    assert len(doctypes) == 1, f'{filename}: expected one HTML5 doctype, found {len(doctypes)}'
    soup = BeautifulSoup(html, 'html.parser')
    styles = '\n'.join(style.get_text() for style in soup.find_all('style'))
    assert re.search(r'@media\s+print\s*\{', styles), f'{filename}: missing valid print stylesheet'
    assert re.search(r'@media\s*\(\s*prefers-reduced-motion\s*:', styles), f'{filename}: missing reduced-motion stylesheet'
    assert not re.search(r'@media\s*\(\s*print\s*\)', styles), f'{filename}: invalid @media(print) syntax'
    headings = list(soup.find_all(re.compile(r'^h[1-6]$')))
    for previous, current in zip(headings, headings[1:]):
        if int(current.name[1]) > int(previous.name[1]) + 1:
            label = current.get_text(" ", strip=True)[:70]
            raise AssertionError(f'{filename}: heading skips {previous.name} to {current.name}: {label}')


def source_articles(root=ROOT):
    spec=importlib.util.spec_from_file_location('upstream_validator',root/'skills/olah-style-paper-posts/scripts/validate.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    _,posts=data(root)
    for p in posts:
        if p['status']!='published':continue
        f=root/'posts'/p['category']/p['slug']/'index.html'
        article=f.read_text(encoding='utf-8')
        check_article_layout(article, str(f.relative_to(root)))
        for bad in BAD_COPY:
            assert bad not in article,f'Forbidden production text: {bad} in {f}'
        result=mod.validate(f)
        assert result['pass'],result
        for warning in result.get('warnings', []):
            print('ARTICLE WARN', p['slug'], warning)
        assert (f.parent/'evidence.json').exists()
        assert len(list((f.parent/'assets').glob('*.svg'))) >= 3,'Need multiple standalone SVGs'
        print('ARTICLE OK',p['slug'],result['counts'])


def published_site(out:Path,base:str=DEFAULT_URL,require_pdfs:bool=False):
    cats,posts=data(ROOT)
    pub=[p for p in posts if p['status']=='published']
    expect=['index.html','archive/index.html','topics/index.html','404.html','sitemap.xml','feed.xml','posts.json','robots.txt']+[f'categories/{c["slug"]}/index.html' for c in cats]+[article_url(p)+'index.html' for p in pub]
    expect += [archive_page_url(i)+'index.html' for i in range(2,archive_page_count(posts)+1)]
    for f in expect:assert (out/f).is_file(),f'Missing output: {f}'
    sitemap=(out/'sitemap.xml').read_text(encoding='utf-8')
    assert '/topics/' in sitemap,'Taxonomy page absent from sitemap'
    for p in pub:assert article_url(p) in sitemap,p
    for i in range(1,archive_page_count(posts)+1):
        assert archive_page_url(i) in sitemap,f'Missing archive page {i} in sitemap'
        page=out/archive_page_url(i)/'index.html'
        soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
        assert len(soup.select('.archive-entry')) <= ARCHIVE_PAGE_SIZE,f'Archive page {i} exceeds thumbnail budget'
    home=BeautifulSoup((out/'index.html').read_text(encoding='utf-8'),'html.parser')
    assert len(home.select('.index-card')) <= HOME_PAGE_SIZE,'Homepage embeds too many index thumbnails'
    for p in posts:
        if p['status']=='draft':assert article_url(p) not in sitemap,f'Leaked draft {p}'
    bad=[]
    anchor_cache={}
    def page_ids(page:Path):
        if page not in anchor_cache:
            anchor_cache[page]={node.get('id') for node in BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser').select('[id]')}
        return anchor_cache[page]
    for path in out.rglob('*.html'):
        soup=BeautifulSoup(path.read_text(encoding='utf-8'),'html.parser')
        if len(soup.select('h1')) != 1:bad.append(f'{path}: expected 1 H1')
        if not soup.find('main'):bad.append(f'{path}: no main')
        ids=[x.get('id') for x in soup.select('[id]')]
        if len(ids)!=len(set(ids)):bad.append(f'{path}: duplicate ids')
        for link in soup.select('a[href],link[href],script[src],img[src],source[src],object[data]'):
            href=link.get('href') or link.get('src') or link.get('data') or ''
            if not href or href.startswith(('mailto:','tel:','data:','javascript:')):continue
            parsed=urlparse(href)
            if parsed.scheme or parsed.netloc or href.startswith('//'):continue
            dest=(path.parent/unquote(parsed.path)).resolve() if parsed.path else path.resolve()
            if dest.is_dir():dest/= 'index.html'
            if not dest.is_relative_to(out.resolve()):
                bad.append(f'out-of-root link: {path.relative_to(out)} -> {href}')
                continue
            # PDF files are generated after the initial HTML build. In pre-PDF
            # validation, defer only explicitly marked article PDF downloads;
            # --require-pdfs must still check their existence and integrity.
            if not dest.is_file() and not (not require_pdfs and link.name == 'a' and link.has_attr('data-pdf-download') and parsed.path == 'article.pdf'):
                bad.append(f'broken link: {path.relative_to(out)} -> {href}')
                continue
            if link.name=='a' and parsed.fragment:
                anchor=unquote(parsed.fragment)
                if anchor not in page_ids(dest):
                    bad.append(f'broken fragment: {path.relative_to(out)} -> {href}')

        if path.parent != out and path.name=='index.html' and 'posts' in path.parts:
            if 'source-code' in path.name:bad.append('never')
    assert not bad,'\n'.join(bad)
    if require_pdfs:
        for p in pub:
            article_dir = out / article_url(p)
            pdf = article_dir / "article.pdf"
            assert pdf.is_file() and pdf.stat().st_size >= 4096, f'Missing PDF: {p["slug"]}'
            assert pdf.open("rb").read(5) == b"%PDF-", f'Invalid PDF header: {p["slug"]}'
            html = BeautifulSoup((article_dir / "index.html").read_text(encoding="utf-8"), "html.parser")
            buttons = html.select('a[data-pdf-download]')
            assert len(buttons) == 1 and buttons[0].get("href") == "article.pdf", (
                f'Missing or duplicated PDF download button: {p["slug"]}'
            )
    assert not any(out.rglob('*.py')) and not any(out.rglob('SKILL.md')) and not any(out.rglob('README.md')),'Non-public tooling leaked into site'
    print('SITE OK',len(list(out.rglob('*.html'))),'HTML pages and',len(pub),'posts')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-pdfs", action="store_true",
                        help="Fail if any published article lacks a PDF or download button")
    args = parser.parse_args()
    check_mirrors(check=True)
    source_articles()
    published_site(ROOT/'_site', require_pdfs=args.require_pdfs)
