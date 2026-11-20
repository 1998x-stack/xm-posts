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
from xml.etree import ElementTree as ET

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
            assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',p.get('updated','')),f'Missing ISO updated date: {p["slug"]}'
            datetime.fromisoformat(p['updated'])
            assert p['updated']>=p['published'],f'Updated before published: {p["slug"]}'
            assert p['reading_minutes']>0,p
            assert isinstance(p.get('paper'),str) and urlparse(p['paper']).scheme=='https',p
            path=root/'posts'/p['category']/p['slug']/'index.html'
            assert path.is_file(),f'Article missing: {path}'
            # Covers are editorial decisions, never a generic visual fallback.
            cover=p.get('cover')
            assert isinstance(cover,dict),f'Missing curated cover for {p["slug"]}'
            assert re.fullmatch(r'assets/[a-zA-Z0-9][a-zA-Z0-9_.-]*\.svg',cover.get('src','')),f'Invalid SVG cover path: {p["slug"]}'
            assert isinstance(cover.get('caption'),str) and 8<=len(cover['caption'])<=80,f'Missing cover explanation: {p["slug"]}'
            assert 'observe' not in cover['caption'].lower() and 'derive' not in cover['caption'].lower(),f'Generic cover: {p["slug"]}'
            assert (path.parent/cover['src']).is_file(),f'Cover SVG missing: {p["slug"]}: {cover["src"]}'
    cover_captions=[p['cover']['caption'] for p in posts if p['status']=='published']
    assert len(cover_captions)==len(set(cover_captions)),'Published cover explanations must be unique'
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
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" data-menu-toggle><span aria-hidden="true">☰</span><span class="menu-label">菜单</span></button><nav id="site-nav" class="top-nav" aria-label="主导航"><a {'aria-current="page"' if active=='home' else ''} href="{rel}">首页</a><a {'aria-current="page"' if active=='topics' else ''} href="{rel}topics/">知识地图</a><a href="{rel}#categories">研究领域</a><a href="{rel}#reading-paths">学习路径</a><a href="{rel}#discover">文章索引</a><a {'aria-current="page"' if active=='archive' else ''} href="{rel}archive/">归档</a><a href="https://github.com/1998x-stack/xm-posts" target="_blank" rel="noopener noreferrer">GitHub ↗</a></nav></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="container footer-main"><div><a class="wordmark" href="{rel}">xm<span>.</span>posts</a><p>从问题出发，经由图示、数学与实验，真正理解模型。</p></div><div><p class="footer-label">EXPLORE</p><a href="{rel}archive/">所有文章</a><a href="{rel}feed.xml">RSS 订阅</a><a href="https://github.com/1998x-stack/xm-posts">源代码</a></div></div><div class="container legal"><span>© xm-posts · Independent technical notes</span><span>Read deeply. Build carefully.</span></div></footer>
</body></html>'''


def category_pill(c, rel, count, active=False):
    return f'<a class="category-pill {"is-selected" if active else ""}" href="{rel}categories/{H(c["slug"])}/"><span>{H(c["title"])}</span><small>{count:02d}</small></a>'


def cover_art(p,rel,*,compact=False):
    """Article's own curated, existing mechanism SVG; no repeated placeholder."""
    cover=p['cover']
    src=rel+article_url(p)+cover['src']
    caption=H(cover['caption'])
    if compact:
        return f'<img class="article-cover-thumb" src="{H(src,quote=True)}" alt="" loading="lazy" decoding="async">'
    return (
        f'<div class="figure-abstract cover-figure">'
        f'<div class="cover-illustration"><img src="{H(src,quote=True)}" alt="{H(cover["caption"],quote=True)}" loading="lazy" decoding="async"></div>'
        f'<span class="cover-caption">{caption}</span></div>'
    )


def post_card(p,rel,ordinal=0,topic_title=None):
    path=rel+article_url(p)
    topic_link=(f'<a class="card-topic" href="{rel}categories/{H(p["category"])}/#topic-{H(p["topic"])}">{H(topic_title)}</a>' if topic_title else '')
    return f'''<article class="post-card" data-post-card data-search="{H((p['title']+' '+p['summary']+' '+' '.join(p['tags'])+' '+p['category']+' '+p['topic']+' '+(topic_title or '')).lower(),quote=True)}" data-category="{H(p['category'])}">
<a class="card-hit" href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">{cover_art(p,rel)}</a>
<div class="card-body"><div class="card-topline"><span>MODEL STUDY / {H(p['category']).upper()}</span><span>{H(p['published'])}</span></div>
{topic_link}<h3><a href="{path}">{H(p['title'])}</a></h3><p class="card-subtitle">{H(p['subtitle'])}</p>
<p class="card-summary">{H(p['summary'])}</p><div class="card-bottom"><span>{p['reading_minutes']} 分钟阅读</span><span class="card-actions"><a class="paper-source" href="{H(p.get('paper',''),quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="原始论文：{H(p['title'],quote=True)}">原论文</a><a href="{path}" aria-label="阅读 {H(p['title'],quote=True)}">阅读全文 <span aria-hidden="true">↗</span></a></span></div></div></article>'''


def build_home(categories,posts,base):
    """Editorial home: fast routes into the corpus, full local search, no draft links."""
    published=[p for p in posts if p['status']=='published']
    published.sort(key=lambda p:(p['published'],p['slug']),reverse=True)
    by_slug={p['slug']:p for p in published}
    labels=topic_labels(categories)
    counts={c['slug']:sum(p['category']==c['slug'] for p in published) for c in categories}
    active=[c for c in categories if counts[c['slug']]]
    planned=[c for c in categories if not counts[c['slug']]]
    count=len(published)

    # Editorial starting points are real, already-published essays; the manifest
    # remains the only source of URLs and metadata. No placeholders are linked.
    feature=by_slug.get('transformer') or by_slug.get('resnet') or (published[0] if published else None)
    if feature:
        feature_markup=f'''<aside class="hero-feature" aria-label="推荐阅读">
            <div class="feature-top"><span>EDITOR'S STARTING POINT</span><span>01 / GUIDE</span></div>
            <div class="feature-art feature-art--cover"><img src="{article_url(feature)+feature['cover']['src']}" alt="{H(feature['cover']['caption'],quote=True)}" loading="eager" decoding="async"></div>
            <div class="feature-copy"><span class="feature-kicker">本期精选 · {H(labels[(feature['category'],feature['topic'])])}</span>
                <h2><a href="{article_url(feature)}">{H(feature['title'])} <span aria-hidden="true">↗</span></a></h2>
                <p>{H(feature['subtitle'])}</p>
                <div class="feature-foot"><span>{feature['reading_minutes']} 分钟深度阅读</span><a href="{article_url(feature)}">进入这篇研究笔记 →</a></div>
            </div></aside>'''
    else:
        feature_markup=''

    subject_cards=''.join(
        f'''<a class="research-card" href="./categories/{H(c['slug'])}/">
            <span class="research-card-top"><span class="research-num">{i:02d} / FIELD</span><span class="research-count">{counts[c['slug']]:02d} 篇</span></span>
            <strong>{H(c['title'])}</strong><span class="research-english">{H(c['english'])}</span>
            <span class="research-description">{H(c['description'])}</span>
            <span class="research-enter">探索领域 <span aria-hidden="true">↗</span></span>
        </a>''' for i,c in enumerate(sorted(active,key=lambda c:-counts[c['slug']]),1)
    )
    planned_links=''.join(
        f'<a href="categories/{H(c["slug"])}/">{H(c["title"])} <span>规划中 ↗</span></a>'
        for c in planned
    )

    learning_paths=[
        ('从经典机器学习出发','看见线性模型、概率假设、最大间隔与树提升的共同问题。',['linear-regression','logistic-regression','naive-bayes','svm','pca','xgboost']),
        ('构建模型架构直觉','从卷积与残差，沿序列记忆走向 Attention。',['cnn','resnet','rnn','lstm','seq2seq','transformer']),
        ('理解优化与高效微调','从梯度与优化器到预训练和参数高效适配。',['sgd','adam','adamw','gpt-1','lora','qlora']),
        ('追溯数据与计算规律','讨论训练语料、数据治理与计算最优的边界。',['the-pile','fineweb','chinchilla']),
        ('学习对齐与策略优化','连接偏好反馈、奖励目标与策略梯度。',['reinforce','ppo','rlhf','dpo','grpo']),
        ('进入高效推理系统','从注意力基础到位置表示、缓存与推理内存。',['transformer','rope','gqa','flashattention','kv-cache','pagedattention']),
        ('系统理解强化学习','先掌握价值函数，再进入 Actor–Critic 与连续控制。',['dqn','ddpg','td3','sac'])
    ]
    route_cards=[]
    for number,(name,description,slugs) in enumerate(learning_paths,1):
        available=[by_slug[slug] for slug in slugs if slug in by_slug]
        if not available:continue
        steps=''.join(f'<li><a href="{article_url(p)}">{H(p["title"])}</a></li>' for p in available[:3])
        extra=f'<span class="route-extra">另有 {len(available)-3} 篇已收录</span>' if len(available)>3 else ''
        route_cards.append(
            f'<article class="route-card learning-card"><div class="route-top"><span>ROUTE {number:02d}</span><span>{len(available)} 篇已收录</span></div>'
            f'<h3>{H(name)}</h3><p>{H(description)}</p><ol>{steps}</ol>{extra}'
            f'<a class="route-start" href="{article_url(available[0])}">从第一篇开始 <span aria-hidden="true">↗</span></a></article>'
        )

    spotlight=[]
    for slug,eyebrow in [('resnet','架构直觉'),('xgboost','经典机器学习'),('ppo','强化学习')]:
        if slug not in by_slug:continue
        p=by_slug[slug]
        spotlight.append(
            f'''<article class="spotlight-card"><a class="spotlight-cover-link" href="{article_url(p)}" aria-label="阅读 {H(p['title'],quote=True)}">{cover_art(p,'./',compact=True)}</a><div class="spotlight-top"><span>{H(eyebrow)}</span><span>{p['reading_minutes']} MIN READ</span></div>
                <h3><a href="{article_url(p)}">{H(p['title'])}</a></h3>
                <p>{H(p['subtitle'])}</p>
                <a class="spotlight-link" href="{article_url(p)}">阅读全文 <span aria-hidden="true">↗</span></a>
            </article>'''
        )

    search_cards=[]
    for i,p in enumerate(published):
        topic=labels[(p['category'],p['topic'])]
        category=next(c['title'] for c in categories if c['slug']==p['category'])
        tokens=' '.join([p['title'],p['subtitle'],p['summary'],p['category'],category,topic,
                         p['topic'],*p['tags']]).lower()
        search_cards.append(
            f'''<article class="index-card post-card" data-post-card data-category="{H(p['category'],quote=True)}" data-search="{H(tokens,quote=True)}">
            <span class="index-order">{i+1:02d}</span><a class="index-image-link" href="{article_url(p)}" aria-label="阅读 {H(p['title'],quote=True)}">{cover_art(p,'./',compact=True)}</a>
            <div class="index-main"><div class="index-kicker">{H(category)} <span>/</span> {H(topic)}</div>
                <h3><a href="{article_url(p)}">{H(p['title'])}</a></h3><p>{H(p['subtitle'])}</p>
                <div class="index-tags"><span>{p['reading_minutes']} 分钟</span><span>{H(p['published'])}</span><a class="paper-source" href="{H(p['paper'],quote=True)}" target="_blank" rel="noopener noreferrer" aria-label="原始论文：{H(p['title'],quote=True)}">原始论文 ↗</a></div>
            </div><a class="index-arrow" href="{article_url(p)}" aria-label="阅读 {H(p['title'],quote=True)}">↗</a>
            </article>'''
        )
    options=''.join(
        f'<option value="{H(c["slug"])}">{H(c["title"])} · {counts[c["slug"]]}</option>' for c in active
    )

    body=f'''<section class="hero container" aria-labelledby="home-title">
      <div class="hero-left">
        <div class="eyebrow"><span class="eyebrow-dot"></span> XM / RESEARCH ATLAS</div>
        <h1 id="home-title">让复杂的模型，<br>变成<span class="marker">可以推演</span>的直觉。</h1>
        <p class="hero-text">从一个真正的问题出发，读懂一篇论文。沿着机制图解、逐步推导与可验证的代码，建立能够迁移的理解。</p>
        <div class="hero-actions"><a class="primary-link" href="#reading-paths">选择一条学习路径 <span aria-hidden="true">↗</span></a><a class="secondary-link" href="#discover">查找具体论文 ↗</a></div>
        <div class="hero-stats" aria-label="知识库概览"><div><strong>{count}</strong><span>篇研究笔记</span></div><div><strong>{len(active)}</strong><span>个已有内容的领域</span></div><div><strong>{len(route_cards)}</strong><span>条学习路径</span></div></div>
      </div>{feature_markup}
    </section>
    <nav class="entry-strip" aria-label="探索方式"><div class="container entry-grid">
      <a href="#categories"><span class="entry-index">01 / SUBJECTS</span><strong>按研究领域探索</strong><span>查看不同问题的完整分类 ↗</span></a>
      <a href="#reading-paths"><span class="entry-index">02 / PATHS</span><strong>按学习顺序阅读</strong><span>沿着关键论文逐步进阶 ↗</span></a>
      <a href="#discover"><span class="entry-index">03 / INDEX</span><strong>直接查找一篇文章</strong><span>按关键词与主题筛选 ↗</span></a>
    </div></nav>
    <section class="container spotlight-section" aria-labelledby="spotlight-title">
      <div class="section-header"><div><div class="eyebrow muted">SELECTED STARTING POINTS</div><h2 id="spotlight-title">三篇值得作为起点的研究</h2></div><p>不只追最新：先建立能够复用的概念，再深入具体模型。</p></div>
      <div class="spotlight-grid">{''.join(spotlight)}</div>
    </section>
    <section id="categories" class="category-band" aria-labelledby="subjects-title"><div class="container">
      <div class="section-header"><div><div class="eyebrow muted">FIELDS OF STUDY</div><h2 id="subjects-title">从研究领域进入知识网络</h2></div><p>有内容的领域优先展示；尚在筹备的方向清晰标注。<a href="topics/">完整知识地图 ↗</a></p></div>
      <div class="research-grid">{subject_cards}</div>
      {f'<div class="planned-fields"><span>持续建设中的方向</span>{planned_links}</div>' if planned else ''}
    </div></section>
    <section id="reading-paths" class="container learning-paths" aria-labelledby="paths-title">
      <div class="section-header"><div><div class="eyebrow muted">GUIDED READING / LEARNING ROUTES</div><h2 id="paths-title">以问题串起论文，而非孤立记忆</h2></div><p>学习路线只连接已发布的内容；每一步都可以独立阅读。</p></div>
      <div class="route-grid">{''.join(route_cards)}</div>
    </section>
    <section id="discover" class="container latest" aria-labelledby="index-title"><span id="latest" class="anchor-alias" aria-hidden="true"></span>
      <div class="section-header"><div><div class="eyebrow muted">COMPLETE ARTICLE INDEX</div><h2 id="index-title">查找你的下一篇研究笔记 <span class="count">{count:02d}</span></h2></div><p>全部已发布文章均可搜索；默认只展开前 8 篇，避免无限滚动。</p></div>
      <div class="browse-controls">
        <label class="search-field" for="search-posts"><span aria-hidden="true">⌕</span><input id="search-posts" type="search" placeholder="搜索论文、模型、关键词或概念" autocomplete="off" data-search-input></label>
        <label class="filter-field" for="category-filter"><span>研究领域</span><select id="category-filter" data-category-filter><option value="">全部领域</option>{options}</select></label>
        <span class="visible-count" aria-live="polite" data-visible-count>共 {count} 篇文章</span>
      </div>
      <div class="index-list" data-post-grid>{''.join(search_cards)}</div>
      <p class="empty-result" hidden data-no-results>没有找到匹配的文章。试试更简短的关键词，或清除筛选条件。</p>
      <div class="index-footer"><button class="load-more" type="button" data-load-more hidden>继续浏览更多文章 ↓</button><a href="archive/">查看完整时间归档 ↗</a></div>
    </section>
    <section class="closing"><div class="container"><div class="eyebrow">AN OPEN, TRACEABLE NOTEBOOK</div>
      <h2>可解释的理解，需要可追溯的证据。</h2>
      <p>文章连接原始论文、数学推导与代码验证。想按知识体系检索？前往知识地图；想了解内容生产方式？阅读仓库规范。</p>
      <div class="closing-actions"><a href="topics/">探索知识地图 ↗</a><a href="https://github.com/1998x-stack/xm-posts">查看研究笔记仓库 ↗</a></div>
    </div></section>'''
    return html_page(title='xm-posts · 深度学习与机器学习研究图谱',description='深度学习、机器学习、LLM、强化学习与系统技术研究笔记：按领域、学习路径或论文关键词发现原理、图解、推导与可运行代码。',canonical=base,body=body)

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
    # Individual paper pages also advertise the same canonical site-wide RSS feed.
    if not re.search(r'<link\b[^>]*application/rss\+xml',head,re.I):
        additions.append('<link rel="alternate" type="application/rss+xml" title="xm-posts RSS" href="'+H(url_join(base,'feed.xml'),quote=True)+'">')
    if not additions:return html
    return re.sub(r'</head>',lambda m:'\n'.join(additions)+'\n'+m.group(0),html,count=1,flags=re.I)


def build_feed(categories:list,posts:list,base:str)->str:
    """Deterministic RSS 2.0 from published manifest entries only.

    Manifest dates are calendar dates, not event timestamps. RSS requires a
    datetime for pubDate, so encode midnight UTC consistently; do not present
    this as the actual publication time. Modified dates retain day precision.
    """
    atom_ns='http://www.w3.org/2005/Atom'
    dcterms_ns='http://purl.org/dc/terms/'
    ET.register_namespace('atom',atom_ns)
    ET.register_namespace('dcterms',dcterms_ns)
    rss=ET.Element('rss',{'version':'2.0'})
    channel=ET.SubElement(rss,'channel')
    ET.SubElement(channel,'title').text='xm-posts'
    ET.SubElement(channel,'link').text=base
    ET.SubElement(channel,'description').text='以图解、数学推导与论文证据理解机器学习、LLM 和系统技术。'
    ET.SubElement(channel,'language').text='zh-cn'
    ET.SubElement(channel,f'{{{atom_ns}}}link',{
        'href':url_join(base,'feed.xml'),
        'rel':'self',
        'type':'application/rss+xml',
    })

    category_titles={c['slug']:c['title'] for c in categories}
    topic_titles=topic_labels(categories)
    published=(p for p in posts if p['status']=='published')
    for p in sorted(published,key=lambda p:(p.get('updated') or p['published'],p['published'],p['slug']),reverse=True):
        url=url_join(base,article_url(p))
        item=ET.SubElement(channel,'item')
        ET.SubElement(item,'title').text=p['title']
        ET.SubElement(item,'link').text=url
        ET.SubElement(item,'guid',{'isPermaLink':'true'}).text=url
        ET.SubElement(item,'description').text=p['summary']
        day=datetime.fromisoformat(p['published']).replace(tzinfo=timezone.utc)
        ET.SubElement(item,'pubDate').text=format_datetime(day,usegmt=True)
        ET.SubElement(item,f'{{{dcterms_ns}}}modified').text=p.get('updated') or p['published']
        ET.SubElement(item,'category',{
            'domain':url_join(base,f'categories/{p["category"]}/'),
        }).text=category_titles[p['category']]
        ET.SubElement(item,'category',{
            'domain':url_join(base,f'categories/{p["category"]}/#topic-{p["topic"]}'),
        }).text=topic_titles[(p['category'],p['topic'])]

    ET.indent(rss,space='  ')
    return ET.tostring(rss,encoding='utf-8',xml_declaration=True).decode('utf-8')+'\n'


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
    write(out,'feed.xml',build_feed(categories,posts,base))
    print(json.dumps({'build':str(out),'base':base,'categories':len(categories),'published':len(published),'files':len(list(out.rglob('*')))},ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'_site')
    parser.add_argument('--base-url',default=os.getenv('SITE_URL',DEFAULT_URL))
    args=parser.parse_args();build(ROOT,args.output,args.base_url)
