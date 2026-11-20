#!/usr/bin/env python3
"""Reproducible, zero-dependency static build for xm-posts GitHub Pages.

Author in posts/<category>/<slug>/index.html, register in content/posts.json,
and let Actions build a complete _site/ bundle. Never deploy drafts or tooling.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape as H
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlparse
from xml.sax.saxutils import escape as X

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_URL='https://1998x-stack.github.io/xm-posts/'
VALID_SLUG=re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def data(root:Path):
    categories=json.loads((root/'content/categories.json').read_text(encoding='utf-8'))
    posts=json.loads((root/'content/posts.json').read_text(encoding='utf-8'))
    assert isinstance(categories,list) and isinstance(posts,list)
    ids=[c['slug'] for c in categories]
    assert len(set(ids))==len(ids) and all(VALID_SLUG.fullmatch(x) for x in ids), 'Bad category slug'
    assert len({p['slug'] for p in posts})==len(posts), 'Duplicate post slug'
    for p in posts:
        assert VALID_SLUG.fullmatch(p['slug']), p
        assert p['category'] in ids, p
        assert p['status'] in {'draft','published'}, p
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',p['published']),p
        datetime.fromisoformat(p['published'])
        assert p['title'] and p['summary'] and p['subtitle']
        if p['status']=='published':
            path=root/'posts'/p['category']/p['slug']/'index.html'
            assert path.is_file(),f'Article missing: {path}'
    return categories,posts


def url_join(base:str, path:str)->str:
    return base.rstrip('/')+'/'+path.lstrip('/')


def article_url(p):return f"posts/{p['category']}/{p['slug']}/"


def html_page(*,title,description,canonical,body,depth=0,active='home',lang='zh-CN'):
    rel='../'*depth or './'
    desc=H(description,quote=True)
    return f'''<!doctype html>
<html lang="{lang}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><meta name="theme-color" content="#f8f7f2">
<meta name="description" content="{desc}"><meta name="robots" content="index,follow">
<meta property="og:type" content="website"><meta property="og:title" content="{H(title,quote=True)}">
<meta property="og:description" content="{desc}"><meta property="og:url" content="{H(canonical,quote=True)}">
<meta name="twitter:card" content="summary"><link rel="canonical" href="{H(canonical,quote=True)}">
<link rel="alternate" type="application/rss+xml" title="xm-posts RSS" href="{rel}feed.xml">
<link rel="icon" href="{rel}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{rel}assets/site.css"><script src="{rel}assets/site.js" defer></script>
<title>{H(title)}</title></head><body>
<a class="skip-link" href="#main">跳至正文</a>
<header class="site-header"><div class="container header-row"><a class="wordmark" href="{rel}" aria-label="xm.posts 首页">xm<span>.</span>posts</a>
<nav class="top-nav" aria-label="主导航"><a {'aria-current="page"' if active=='home' else ''} href="{rel}">首页</a><a {'aria-current="page"' if active=='archive' else ''} href="{rel}archive/">文章归档</a><a href="{rel}#categories">分类</a><a href="{rel}#reading-paths">学习路径</a><a href="https://github.com/1998x-stack/xm-posts" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="container footer-main"><div><a class="wordmark" href="{rel}">xm<span>.</span>posts</a><p>从问题出发，经由图示、数学与实验，真正理解模型。</p></div><div><p class="footer-label">EXPLORE</p><a href="{rel}archive/">所有文章</a><a href="{rel}feed.xml">RSS 订阅</a><a href="https://github.com/1998x-stack/xm-posts">源代码</a></div></div><div class="container legal"><span>© xm-posts · Independent technical notes</span><span>Read deeply. Build carefully.</span></div></footer>
</body></html>'''


def category_pill(c, rel, count, active=False):
    return f'<a class="category-pill {"is-selected" if active else ""}" href="{rel}categories/{H(c["slug"])}/"><span>{H(c["title"])}</span><small>{count:02d}</small></a>'


def post_card(p,rel,ordinal=0):
    path=rel+article_url(p)
    if p['slug'] == 'resnet':
        icon, art = 'residual', '<span class="math-mark">H(x) = x + F(x)</span><span class="pathline pathline-a"></span><span class="pathline pathline-b"></span><span class="pathline pathline-c"></span>'
    elif p['slug'] == 'transformer':
        icon, art = 'attention', '<span class="math-mark">softmax(QKᵀ / √dₖ)V</span><span class="attention-dots">● · ● · ● · ● · ●</span>'
    elif p['slug'] == 'adamw':
        icon, art = 'generic', '<span class="math-mark">θ ← θ − α·Adam(g) − α·λθ</span>'
    elif p['slug'] == 'rope':
        icon, art = 'generic', '<span class="math-mark">R(m)ᵀR(n) = R(n−m)</span>'
    elif p['slug'] == 'self-consistency':
        icon, art = 'consistency', '<span class="math-mark">argmaxₐ Σᵢ 𝟙[aᵢ = a]</span><span class="attention-dots">10 · 13 · 10 · 10 → 10</span>'
    elif p['slug'] == 'svm':
        icon, art = 'margin', '<span class="math-mark">margin = 2 / ||w||</span><span class="svm-boundary svm-left"></span><span class="svm-boundary svm-center"></span><span class="svm-boundary svm-right"></span><span class="svm-point point-blue"></span><span class="svm-point point-orange"></span>'
    elif p['slug'] == 'lora':
        icon, art = 'lowrank', '<span class="math-mark">ΔW = BA</span><span class="lowrank-base">W₀</span><span class="lowrank-a">A</span><span class="lowrank-b">B</span><span class="lowrank-plus">+</span>'
    elif p['slug'] == 'understanding-word2vec':
        icon, art = 'embedding', '<span class="math-mark">P(context | center)</span><span class="embedding-dots">● ● ● ● ●</span><span class="embedding-eq">positive + k negatives</span>'
    else:
        icon, art = 'generic', '<span class="math-mark">Observe → Derive → Verify</span>'
    poster=f'<div class="figure-abstract figure-{icon}" aria-hidden="true"><span class="accent-label">FIG. {ordinal or 1:02d}</span>{art}</div>'
    return f'''<article class="post-card" data-post-card data-search="{H((p['title']+' '+p['summary']+' '+' '.join(p['tags'])).lower(),quote=True)}" data-category="{H(p['category'])}">
<a class="card-hit" href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">{poster}</a>
<div class="card-body"><div class="card-topline"><span>MODEL STUDY / {H(p['category']).upper()}</span><span>{H(p['published'])}</span></div>
<h3><a href="{path}">{H(p['title'])}</a></h3><p class="card-subtitle">{H(p['subtitle'])}</p>
<p class="card-summary">{H(p['summary'])}</p><div class="card-bottom"><span>{p['reading_minutes']} 分钟阅读</span><span class="card-actions"><a class="paper-source" href="{H(p.get('paper',''),quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="原始论文：{H(p['title'],quote=True)}">原论文</a><a href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">阅读全文 <span aria-hidden="true">↗</span></a></span></div></div></article>'''


def build_home(categories,posts,base):
    published=[p for p in posts if p['status']=='published']
    published.sort(key=lambda p:(p['published'],p['slug']),reverse=True)
    cats=''.join(category_pill(c,'./',sum(p['category']==c['slug'] for p in published)) for c in categories)
    cards=''.join(post_card(p,'./',i+1) for i,p in enumerate(published))
    count=len(published)

    by_slug={p['slug']:p for p in published}
    learning_paths=[
        ('01 · 建立表征与架构直觉','从词向量走向残差网络，再理解自注意力。',['understanding-word2vec','resnet','transformer']),
        ('02 · 理解训练中的优化','比较随机梯度、适应性动量、解耦权重衰减。',['sgd','adam','adamw']),
        ('03 · 从模型到高效推理','从 Transformer 到注意力 Kernel，再到 KV 管理与分页。',['transformer','flashattention','kv-cache','pagedattention']),
        ('04 · 对齐与策略优化','区分强化学习基线、偏好训练与组内优势。',['ppo','rlhf','dpo','grpo'])
    ]
    path_cards=''.join(
        '<article class="learning-card"><div class="learning-number">'+H(title)+'</div>'
        +'<p>'+H(description)+'</p><ol>'
        +''.join('<li><a href="'+article_url(by_slug[slug])+'">'+H(by_slug[slug]['title'])+'</a></li>'
                 for slug in slugs if slug in by_slug)
        +'</ol></article>'
        for title,description,slugs in learning_paths
        if all(slug in by_slug for slug in slugs)
    )
    body=f'''<section class="hero container"><div class="hero-left"><div class="eyebrow"><span class="eyebrow-dot"></span> RESEARCH NOTES · TECHNICAL EXPLAINERS</div>
<h1>把模型的<span class="marker">「为什么」</span><br>讲到<span class="serif-ital">可计算。</span></h1>
<p class="hero-text">不从繁复符号开始，而从一个具体困惑开始。沿着原始论文的证据、逐步展开的结构图与可运行代码，理解深度学习的关键思想。</p>
<div class="hero-actions"><a class="primary-link" href="#latest">开始阅读 <span>↗</span></a><a class="secondary-link" href="archive/">浏览全部 {count} 篇 ↗</a></div>
</div><div class="hero-visual" aria-hidden="true"><div class="visual-caption">ANATOMY OF AN IDEA <span>№ 001</span></div><div class="visual-model"><div class="diagram-node">Input<br><small>x</small></div><div class="diagram-mid"><span class="thin-line">Identity</span><div class="diagram-box">Transformation<br><small>F(x)</small></div></div><div class="diagram-node out">Output<br><small>x + F(x)</small></div></div><div class="visual-bottom">OBSERVE → FORMALIZE → IMPLEMENT<span>·</span>VERIFY</div></div></section>
<section id="categories" class="category-band"><div class="container"><div class="section-header"><div><div class="eyebrow muted">EXPLORE BY SUBJECT</div><h2>沿着问题脉络阅读</h2></div><p>持续生长的研究主题，而不只是按时间堆叠的文章。</p></div><div class="category-grid">{cats}</div></div></section>
<section id="reading-paths" class="container learning-paths"><div class="section-header"><div><div class="eyebrow muted">GUIDED STUDY ROUTES</div><h2>按学习目标，串起论文</h2></div><p>每条路线由已发布文章组成；不是用目录占位凑篇数。</p></div><div class="learning-grid">{path_cards}</div></section>
<section id="latest" class="container latest"><div class="section-header"><div><div class="eyebrow muted">ESSAYS & VISUAL EXPLANATIONS</div><h2>全部论文解读 <span class="count">{count:02d}</span></h2></div><p>完整文章、可独立查看的 SVG 与论文证据。</p></div>
<div class="browse-controls"><label class="search-field" for="search-posts"><span aria-hidden="true">⌕</span><input id="search-posts" type="search" placeholder="搜索模型、术语或论文关键词" autocomplete="off" data-search-input></label><span class="visible-count" aria-live="polite" data-visible-count>共 {count} 篇文章</span></div>
<div class="post-grid" data-post-grid>{cards}</div><p class="empty-result" hidden data-no-results>没有找到匹配的文章，可以尝试其他关键词。</p>
<div class="section-more"><a href="archive/">查看所有文章与时间索引 <span>↗</span></a></div></section>
<section class="closing"><div class="container"><div class="eyebrow">AN ONGOING NOTEBOOK</div><h2>每一篇新文章，都是一条可追溯的理解路径。</h2><p>分类会持续扩展。所有正式发布文章都经由代码验证与浏览器检查后自动加入索引。</p><a href="https://github.com/1998x-stack/xm-posts">查看项目与贡献规范 ↗</a></div></section>'''
    return html_page(title='xm-posts · 深度学习论文图解',description='图解深度学习与 LLM 基础论文：从直觉到结构图、数学与可运行代码，附原论文证据与验证。',canonical=base,body=body)


def build_category(c,posts,categories,base):
    listing=sorted([p for p in posts if p['status']=='published' and p['category']==c['slug']],key=lambda p:p['published'],reverse=True)
    rel='../../'
    pills=''.join(category_pill(x,rel,sum(p['status']=='published' and p['category']==x['slug'] for p in posts),x['slug']==c['slug']) for x in categories)
    if listing:
        content='<div class="post-grid">'+''.join(post_card(p,rel,i+1) for i,p in enumerate(listing))+'</div>'
    else:
        content='<div class="category-empty"><span aria-hidden="true">◇</span><h2>这个主题的笔记还在路上。</h2><p>目录已经建立，后续文章通过 GitHub Actions 自动发布。这里不会把占位文件当成正式文章。</p><a href="'+rel+'archive/">先看看已发布的文章 ↗</a></div>'
    body=f'''<div class="container category-page"><div class="breadcrumb"><a href="{rel}">首页</a> <span>/</span> 分类 <span>/</span> {H(c['title'])}</div>
<div class="eyebrow muted">TOPIC COLLECTION · {H(c['english']).upper()}</div><h1>{H(c['title'])}<span class="faded-en"> / {H(c['english'])}</span></h1><p class="category-description">{H(c['description'])}</p>
<div class="topic-tracks">{''.join(f'<span>{H(x)}</span>' for x in c['topics'])}</div>
<div class="divider-title"><h2>相关文章</h2><span>{len(listing):02d} POSTS</span></div>{content}
<div class="category-nav"><div class="eyebrow muted">MORE TOPICS</div>{pills}</div></div>'''
    return html_page(title=f"{c['title']} · xm-posts",description=c['description'],canonical=url_join(base,f'categories/{c["slug"]}/'),body=body,depth=2)


def build_archive(posts,base):
    published=sorted([p for p in posts if p['status']=='published'],key=lambda p:(p['published'],p['title']),reverse=True)
    cards=''.join(f'''<li><span class="timeline-date">{H(p['published'])}</span><div><h2><a href="../{article_url(p)}">{H(p['title'])}</a></h2><p>{H(p['subtitle'])}</p></div><span class="timeline-time">{p['reading_minutes']} min <span aria-hidden="true">↗</span></span></li>''' for p in published)
    body=f'''<div class="container archive-page"><div class="breadcrumb"><a href="../">首页</a> <span>/</span> 文章归档</div><div class="eyebrow muted">ALL EXPLAINERS · CHRONOLOGICAL</div><h1>研究笔记归档<span class="count">{len(published):02d}</span></h1><p class="category-description">所有已发布的长文。草稿与目录占位不会出现在这里。</p><ol class="timeline">{cards}</ol></div>'''
    return html_page(title='文章归档 · xm-posts',description='按时间浏览 xm-posts 全部深度学习论文图解文章。',canonical=url_join(base,'archive/'),body=body,depth=1,active='archive')


def write(out:Path,path:str,content:str):
    dest=out/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content,encoding='utf-8')


def enrich_article_head(html:str,p:dict,base:str)->str:
    """Add missing social/canonical tags to deployed articles, never duplicate existing ones."""
    canonical=url_join(base,article_url(p))
    head=html.split('</head>',1)[0] if '</head>' in html else html.split('</HEAD>',1)[0]
    specs=[
        (r'<link\b[^>]*rel=[^ >]+canonical[^ >]*',
         '<link rel="canonical" href="'+H(canonical,quote=True)+'">'),
        (r'<meta\b[^>]*property=[^ >]+og:url[^ >]*',
         '<meta property="og:url" content="'+H(canonical,quote=True)+'">'),
        (r'<meta\b[^>]*property=[^ >]+og:type[^ >]*',
         '<meta property="og:type" content="article">'),
        (r'<meta\b[^>]*property=[^ >]+og:title[^ >]*',
         '<meta property="og:title" content="'+H(p['title'],quote=True)+'">'),
        (r'<meta\b[^>]*property=[^ >]+og:description[^ >]*',
         '<meta property="og:description" content="'+H(p['summary'],quote=True)+'">'),
        (r'<meta\b[^>]*name=[^ >]+twitter:card[^ >]*',
         '<meta name="twitter:card" content="summary">'),
    ]
    additions=[value for regex,value in specs if not re.search(regex,head,re.I)]
    if not additions:return html
    return re.sub(r'</head>',lambda m:'\n'.join(additions)+'\n'+m.group(0),html,count=1,flags=re.I)


def build(root:Path,out:Path,base:str):
    base=base.rstrip('/')+'/'
    assert base.startswith('https://') or base.startswith('http://localhost:'), 'Provide valid HTTPS base URL'
    if out.exists():shutil.rmtree(out)
    out.mkdir(parents=True)
    categories,posts=data(root)
    write(out,'index.html',build_home(categories,posts,base))
    write(out,'archive/index.html',build_archive(posts,base))
    for c in categories:write(out,f'categories/{c["slug"]}/index.html',build_category(c,posts,categories,base))
    published=[p for p in posts if p['status']=='published']
    for p in published:
        src=root/'posts'/p['category']/p['slug'];dst=out/'posts'/p['category']/p['slug']
        shutil.copytree(src,dst,ignore=shutil.ignore_patterns('README.md','*.pyc','__pycache__','*.py','evidence.json'))
        published_html=dst/'index.html'
        published_html.write_text(enrich_article_head(published_html.read_text(encoding='utf-8'),p,base),encoding='utf-8')
    shutil.copytree(root/'site/assets',out/'assets')
    write(out,'.nojekyll','')
    write(out,'404.html',html_page(title='页面未找到 · xm-posts',description='你访问的页面不存在。',canonical=url_join(base,'404.html'),body='<div class="container category-empty not-found"><h1>这条路径尚未被写下。</h1><p>页面可能移动了，或文章尚未正式发布。</p><a href="./">回到首页 ↗</a></div>'))
    search=[{k:p[k] for k in ['title','slug','subtitle','summary','category','tags','published','reading_minutes']}|{'url':article_url(p)} for p in published]
    write(out,'posts.json',json.dumps(search,ensure_ascii=False,indent=2)+'\n')
    urls=[base,url_join(base,'archive/')]+[url_join(base,f'categories/{c["slug"]}/') for c in categories]+[url_join(base,article_url(p)) for p in published]
    sitemap=''.join(f'<url><loc>{X(u)}</loc></url>' for u in urls)
    write(out,'sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+sitemap+'</urlset>')
    write(out,'robots.txt',f'User-agent: *\nAllow: /\nSitemap: {url_join(base,"sitemap.xml")}\n')
    rss=''.join(f'<item><title>{X(p["title"])}</title><link>{X(url_join(base,article_url(p)))}</link><guid isPermaLink="true">{X(url_join(base,article_url(p)))}</guid><description>{X(p["summary"])}</description><pubDate>{format_datetime(datetime.fromisoformat(p["published"]).replace(tzinfo=timezone.utc))}</pubDate></item>' for p in sorted(published,key=lambda x:x['published'],reverse=True))
    write(out,'feed.xml',f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>xm-posts</title><link>{X(base)}</link><description>Evidence-grounded model explainers</description>{rss}</channel></rss>')
    print(json.dumps({'build':str(out),'base':base,'categories':len(categories),'published':len(published),'files':len(list(out.rglob('*')))},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'_site')
    parser.add_argument('--base-url',default=os.getenv('SITE_URL',DEFAULT_URL))
    args=parser.parse_args();build(ROOT,args.output,args.base_url)
