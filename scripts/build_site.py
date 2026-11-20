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
    category_topics={}
    for c in categories:
        assert all(isinstance(c.get(k),str) and c[k].strip() for k in ('title','english','description')),c
        assert isinstance(c.get('topics'),list) and c['topics'],f'Missing topics: {c["slug"]}'
        topic_ids=[]
        for t in c['topics']:
            assert isinstance(t,dict) and VALID_SLUG.fullmatch(t.get('slug','')),t
            assert isinstance(t.get('title'),str) and t['title'].strip(),t
            topic_ids.append(t['slug'])
        assert len(topic_ids)==len(set(topic_ids)),f'Duplicate topic ID in {c["slug"]}'
        category_topics[c['slug']]=set(topic_ids)
        assert (root/'posts'/c['slug']/'README.md').is_file(),f'Category README missing: {c["slug"]}'
    assert len({p['slug'] for p in posts})==len(posts), 'Duplicate post slug'
    for p in posts:
        assert VALID_SLUG.fullmatch(p['slug']), p
        assert p['category'] in ids, p
        assert p.get('topic') in category_topics[p['category']],f'Invalid primary topic for {p["slug"]}: {p.get("topic")}'
        assert p['status'] in {'draft','published'}, p
        assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',p['published']),p
        datetime.fromisoformat(p['published'])
        assert p['title'] and p['summary'] and p['subtitle']
        assert isinstance(p.get('reading_minutes'),int) and p['reading_minutes']>=0,p
        assert isinstance(p.get('tags'),list) and all(isinstance(tag,str) and tag.strip() for tag in p['tags']),p
        if p['status']=='published':
            assert p['reading_minutes']>0,p
            assert isinstance(p.get('paper'),str) and urlparse(p['paper']).scheme=='https',p
            path=root/'posts'/p['category']/p['slug']/'index.html'
            assert path.is_file(),f'Article missing: {path}'
    return categories,posts


def url_join(base:str, path:str)->str:
    return base.rstrip('/')+'/'+path.lstrip('/')


def article_url(p):return f"posts/{p['category']}/{p['slug']}/"


def html_page(*,title,description,canonical,body,depth=0,active='home',lang='zh-CN',root_href=None):
    rel=root_href if root_href is not None else ('../'*depth or './')
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
<nav class="top-nav" aria-label="主导航"><a {'aria-current="page"' if active=='home' else ''} href="{rel}">首页</a><a {'aria-current="page"' if active=='archive' else ''} href="{rel}archive/">文章归档</a><a href="{rel}#categories">分类</a><a {'aria-current="page"' if active=='topics' else ''} href="{rel}topics/">知识地图</a><a href="{rel}#reading-paths">学习路径</a><a href="https://github.com/1998x-stack/xm-posts" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="container footer-main"><div><a class="wordmark" href="{rel}">xm<span>.</span>posts</a><p>从问题出发，经由图示、数学与实验，真正理解模型。</p></div><div><p class="footer-label">EXPLORE</p><a href="{rel}archive/">所有文章</a><a href="{rel}feed.xml">RSS 订阅</a><a href="https://github.com/1998x-stack/xm-posts">源代码</a></div></div><div class="container legal"><span>© xm-posts · Independent technical notes</span><span>Read deeply. Build carefully.</span></div></footer>
</body></html>'''


def category_pill(c, rel, count, active=False):
    return f'<a class="category-pill {"is-selected" if active else ""}" href="{rel}categories/{H(c["slug"])}/"><span>{H(c["title"])}</span><small>{count:02d}</small></a>'


def post_card(p,rel,ordinal=0,topic_title=None):
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
    topic_link=(f'<a class="card-topic" href="{rel}categories/{H(p["category"])}/#topic-{H(p["topic"])}">{H(topic_title)}</a>' if topic_title else '')
    poster=f'<div class="figure-abstract figure-{icon}" aria-hidden="true"><span class="accent-label">FIG. {ordinal or 1:02d}</span>{art}</div>'
    return f'''<article class="post-card" data-post-card data-search="{H((p['title']+' '+p['summary']+' '+' '.join(p['tags'])+' '+p['category']+' '+p['topic']+' '+(topic_title or '')).lower(),quote=True)}" data-category="{H(p['category'])}">
<a class="card-hit" href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">{poster}</a>
<div class="card-body"><div class="card-topline"><span>MODEL STUDY / {H(p['category']).upper()}</span><span>{H(p['published'])}</span></div>
{topic_link}<h3><a href="{path}">{H(p['title'])}</a></h3><p class="card-subtitle">{H(p['subtitle'])}</p>
<p class="card-summary">{H(p['summary'])}</p><div class="card-bottom"><span>{p['reading_minutes']} 分钟阅读</span><span class="card-actions"><a class="paper-source" href="{H(p.get('paper',''),quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="原始论文：{H(p['title'],quote=True)}">原论文</a><a href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">阅读全文 <span aria-hidden="true">↗</span></a></span></div></div></article>'''


def build_home(categories,posts,base):
    published=[p for p in posts if p['status']=='published']
    published.sort(key=lambda p:(p['published'],p['slug']),reverse=True)
    cats=''.join(category_pill(c,'./',sum(p['category']==c['slug'] for p in published)) for c in categories)
    topic_labels={(c['slug'],t['slug']):t['title'] for c in categories for t in c['topics']}
    cards=''.join(post_card(p,'./',i+1,topic_labels[(p['category'],p['topic'])]) for i,p in enumerate(published))
    count=len(published)

    by_slug={p['slug']:p for p in published}
    learning_paths=[
        ('01 · 经典机器学习与数学直觉','从线性模型、概率假设、间隔到树集成。',['linear-regression','naive-bayes','svm','pca','xgboost']),
        ('02 · 视觉、序列与 Attention','沿 CNN、残差、循环记忆与序列转换理解 Transformer。',['cnn','resnet','rnn','lstm','seq2seq','transformer']),
        ('03 · 优化、预训练与微调','理解梯度优化、语言模型训练，以及参数高效适配。',['sgd','adam','adamw','gpt-1','lora','qlora']),
        ('04 · 数据与计算最优训练','从多来源语料治理走向训练数据与模型规模权衡。',['the-pile','fineweb','chinchilla']),
        ('05 · 对齐、策略与推理','连接 CoT 采样、偏好目标与强化学习优化。',['chain-of-thought','self-consistency','ppo','rlhf','dpo','grpo']),
        ('06 · 高效 Attention 与 Serving','从基础注意力进入旋转位置、GPU Kernel 和 KV 内存管理。',['transformer','rope','gqa','flashattention','kv-cache','pagedattention']),
        ('07 · 深度强化学习','由 DQN 价值学习，走向确定性与随机 Actor–Critic。',['dqn','ddpg','ppo','sac'])
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
<section id="categories" class="category-band"><div class="container"><div class="section-header"><div><div class="eyebrow muted">EXPLORE BY SUBJECT</div><h2>沿着问题脉络阅读</h2></div><p>一级分类是领域，二级主题是可直达文章的研究路径。<a href="topics/">查看完整知识地图 ↗</a></p></div><div class="category-grid">{cats}</div></div></section>
<section id="reading-paths" class="container learning-paths"><div class="section-header"><div><div class="eyebrow muted">GUIDED STUDY ROUTES</div><h2>按学习目标，串起论文</h2></div><p>每条路线由已发布文章组成；不是用目录占位凑篇数。</p></div><div class="learning-grid">{path_cards}</div></section>
<section id="latest" class="container latest"><div class="section-header"><div><div class="eyebrow muted">ESSAYS & VISUAL EXPLANATIONS</div><h2>全部论文解读 <span class="count">{count:02d}</span></h2></div><p>完整文章、可独立查看的 SVG 与论文证据。</p></div>
<div class="browse-controls"><label class="search-field" for="search-posts"><span aria-hidden="true">⌕</span><input id="search-posts" type="search" placeholder="搜索模型、术语或论文关键词" autocomplete="off" data-search-input></label><span class="visible-count" aria-live="polite" data-visible-count>共 {count} 篇文章</span></div>
<div class="post-grid" data-post-grid>{cards}</div><p class="empty-result" hidden data-no-results>没有找到匹配的文章，可以尝试其他关键词。</p>
<div class="section-more"><a href="archive/">查看所有文章与时间索引 <span>↗</span></a></div></section>
<section class="closing"><div class="container"><div class="eyebrow">AN ONGOING NOTEBOOK</div><h2>每一篇新文章，都是一条可追溯的理解路径。</h2><p>分类会持续扩展。所有正式发布文章都经由代码验证与浏览器检查后自动加入索引。</p><a href="https://github.com/1998x-stack/xm-posts">查看项目与贡献规范 ↗</a></div></section>'''
    return html_page(title='xm-posts · 深度学习论文图解',description='图解深度学习与 LLM 基础论文：从直觉到结构图、数学与可运行代码，附原论文证据与验证。',canonical=base,body=body)


def topic_labels(categories):
    return {(c['slug'],t['slug']):t['title'] for c in categories for t in c['topics']}


def build_topics(categories,posts,base):
    published=[p for p in posts if p['status']=='published']
    summary=''.join(
        f'<a href="#category-{H(c["slug"])}">{H(c["title"])} <small>{sum(p["category"]==c["slug"] for p in published):02d}</small></a>'
        for c in categories
    )
    groups=[]
    for c in categories:
        related=[p for p in published if p['category']==c['slug']]
        links=''.join(
            f'<li><a href="../categories/{H(c["slug"])}/#topic-{H(t["slug"])}"><span>{H(t["title"])}</span>'
            f'<small>{"%02d 篇" % sum(p["topic"]==t["slug"] for p in related) if any(p["topic"]==t["slug"] for p in related) else "规划中"}</small></a></li>'
            for t in c['topics']
        )
        groups.append(
            f'<section class="taxonomy-group" id="category-{H(c["slug"])}" aria-labelledby="taxonomy-{H(c["slug"])}">'
            f'<div class="taxonomy-group-title"><h2 id="taxonomy-{H(c["slug"])}"><a href="../categories/{H(c["slug"])}/">{H(c["title"])}'
            f' <span class="faded-en">/ {H(c["english"])}</span></a></h2><span>{len(related)} 篇 · {len(c["topics"])} 个二级主题</span></div>'
            f'<p>{H(c["description"])}</p><ul class="taxonomy-links">{links}</ul></section>'
        )
    body=(
        '<div class="container taxonomy-page"><div class="breadcrumb"><a href="../">首页</a> <span>/</span> 知识地图</div>'
        '<div class="eyebrow muted">RESEARCH TAXONOMY · KNOWLEDGE MAP</div><h1>知识地图</h1>'
        f'<p class="category-description">覆盖 {len(categories)} 个一级研究领域、{sum(len(c["topics"]) for c in categories)} 个二级主题、'
        f'{len(published)} 篇正式发布文章。每篇文章归属一个主主题；交叉学科通过标签和学习路径相互连接。'
        '“规划中”代表尚无文章，不代表已有解读。</p>'
        f'<nav class="taxonomy-overview" aria-label="跳转至一级分类">{summary}</nav>'
        +''.join(groups)+'</div>'
    )
    return html_page(title='知识地图 · xm-posts',description='xm-posts 全部一级分类与二级主题、已发布文章数量及规划中研究方向。',canonical=url_join(base,'topics/'),body=body,depth=1,active='topics')


def build_category(c,posts,categories,base):
    listing=sorted([p for p in posts if p['status']=='published' and p['category']==c['slug']],key=lambda p:(p['published'],p['slug']),reverse=True)
    rel='../../'
    pills=''.join(category_pill(x,rel,sum(p['status']=='published' and p['category']==x['slug'] for p in posts),x['slug']==c['slug']) for x in categories)
    jumps=''.join(
        f'<a href="#topic-{H(t["slug"])}"><span>{H(t["title"])}</span><small>{sum(p["topic"]==t["slug"] for p in listing):02d} 篇</small></a>'
        for t in c['topics']
    )
    sections=[]
    for t in c['topics']:
        group=[p for p in listing if p['topic']==t['slug']]
        content=(
            '<div class="post-grid">'+''.join(post_card(p,rel,i+1,t['title']) for i,p in enumerate(group))+'</div>'
            if group else '<p class="topic-empty">该研究方向正在规划中，尚无正式发布的文章。</p>'
        )
        sections.append(
            f'<section class="topic-section" id="topic-{H(t["slug"])}" aria-labelledby="heading-{H(t["slug"])}">'
            f'<div class="topic-section-heading"><h2 id="heading-{H(t["slug"])}">{H(t["title"])}</h2>'
            f'<span>{"%02d 篇文章" % len(group) if group else "规划中"}</span></div>{content}</section>'
        )
    body=f'''<div class="container category-page"><div class="breadcrumb"><a href="{rel}">首页</a> <span>/</span> <a href="{rel}topics/">知识地图</a> <span>/</span> {H(c['title'])}</div>
<div class="eyebrow muted">TOPIC COLLECTION · {H(c['english']).upper()}</div><h1>{H(c['title'])}<span class="faded-en"> / {H(c['english'])}</span></h1><p class="category-description">{H(c['description'])}</p>
<p class="taxonomy-hint">{len(listing)} 篇文章 · {len(c['topics'])} 个二级主题 · <a href="{rel}topics/#category-{H(c['slug'])}">查看完整知识地图 ↗</a></p>
<nav class="topic-jumps" aria-label="本分类二级主题导航">{jumps}</nav>
{''.join(sections)}
<div class="category-nav"><div class="eyebrow muted">MORE TOPICS</div>{pills}</div></div>'''
    return html_page(title=f"{c['title']} · xm-posts",description=c['description'],canonical=url_join(base,f'categories/{c["slug"]}/'),body=body,depth=2)


def build_archive(posts,categories,base):
    published=sorted([p for p in posts if p['status']=='published'],key=lambda p:(p['published'],p['title']),reverse=True)
    labels=topic_labels(categories)
    cards=''.join(f'''<li><span class="timeline-date">{H(p['published'])}</span><div><h2><a href="../{article_url(p)}">{H(p['title'])}</a></h2><p>{H(p['subtitle'])}</p><a class="archive-topic" href="../categories/{H(p['category'])}/#topic-{H(p['topic'])}">{H(labels[(p['category'],p['topic'])])}</a></div><span class="timeline-time">{p['reading_minutes']} min <span aria-hidden="true">↗</span></span></li>''' for p in published)
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
    write(out,'archive/index.html',build_archive(posts,categories,base))
    write(out,'topics/index.html',build_topics(categories,posts,base))
    for c in categories:write(out,f'categories/{c["slug"]}/index.html',build_category(c,posts,categories,base))
    published=[p for p in posts if p['status']=='published']
    for p in published:
        src=root/'posts'/p['category']/p['slug'];dst=out/'posts'/p['category']/p['slug']
        shutil.copytree(src,dst,ignore=shutil.ignore_patterns('README.md','*.pyc','__pycache__','*.py','evidence.json'))
        published_html=dst/'index.html'
        published_html.write_text(enrich_article_head(published_html.read_text(encoding='utf-8'),p,base),encoding='utf-8')
    shutil.copytree(root/'site/assets',out/'assets')
    write(out,'.nojekyll','')
    write(out,'404.html',html_page(title='页面未找到 · xm-posts',description='你访问的页面不存在。',canonical=url_join(base,'404.html'),body='<div class="container category-empty not-found"><h1>这条路径尚未被写下。</h1><p>页面可能移动了，或文章尚未正式发布。</p><a href="'+H(base,quote=True)+'">回到首页 ↗</a></div>',root_href=base))
    search=[{k:p[k] for k in ['title','slug','subtitle','summary','category','topic','tags','published','reading_minutes']}|{'url':article_url(p)} for p in published]
    write(out,'posts.json',json.dumps(search,ensure_ascii=False,indent=2)+'\n')
    urls=[base,url_join(base,'archive/'),url_join(base,'topics/')]+[url_join(base,f'categories/{c["slug"]}/') for c in categories]+[url_join(base,article_url(p)) for p in published]
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
