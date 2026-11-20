#!/usr/bin/env python3
"""Scaffold a draft paper explainer; requires explicit promotion to published."""
from __future__ import annotations
import argparse,json,re
from datetime import datetime,timezone
from pathlib import Path
from html import escape
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('category');ap.add_argument('slug');ap.add_argument('--topic',required=True,help='Registered second-level topic slug');ap.add_argument('--title',required=True);ap.add_argument('--subtitle',required=True);ap.add_argument('--paper',default='')
    a=ap.parse_args()
    cats=json.loads((ROOT/'content/categories.json').read_text(encoding='utf-8'))
    if a.category not in {c['slug'] for c in cats}:ap.error('category not registered')
    selected=next(c for c in cats if c['slug']==a.category)
    if a.topic not in {t['slug'] for t in selected['topics']}:ap.error('topic not registered in category; see content/categories.json')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',a.slug):ap.error('slug must be lowercase kebab-case')
    postlist=ROOT/'content/posts.json'; posts=json.loads(postlist.read_text(encoding='utf-8'))
    if any(p['slug']==a.slug for p in posts):ap.error('slug already exists')
    path=ROOT/'posts'/a.category/a.slug
    if path.exists():ap.error('directory already exists')
    path.mkdir(parents=True);(path/'assets').mkdir()
    (path/'assets'/'first-concept.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 180" role="img" aria-labelledby="diagram-title"><title id="diagram-title">待替换：机制图</title><rect x="30" y="40" width="580" height="100" rx="12" fill="#e0eee9" stroke="#99c5b7"/><text x="320" y="96" text-anchor="middle" font-size="21" fill="#24545a">在此绘制机制示意图</text></svg>\n''',encoding='utf-8')
    (path/'index.html').write_text(f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(a.title)}</title></head><body><nav><a href="../../../">返回全部文章</a></nav><main><article><h1>{escape(a.title)}</h1><p>{escape(a.subtitle)}</p><section><h2>问题从何而来</h2><p>TODO: 用论文证据回答问题。</p><figure><img src="assets/first-concept.svg" alt="待绘制的机制示意图"><figcaption>TODO: 解释输入、变换和输出。</figcaption></figure></section><section><h2>机制与证据</h2><p>TODO: 数学、代码与限制。</p></section></article></main></body></html>\n''',encoding='utf-8')
    (path/'evidence.json').write_text('[]\n',encoding='utf-8')
    posts.append({'slug':a.slug,'title':a.title,'subtitle':a.subtitle,'category':a.category,'topic':a.topic,'status':'draft','published':datetime.now(timezone.utc).date().isoformat(),'updated':datetime.now(timezone.utc).date().isoformat(),'reading_minutes':0,'tags':[],'summary':'TODO: 摘要','paper':a.paper,'illustration':a.slug})
    postlist.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Created DRAFT:',path.relative_to(ROOT),'(not published until status=published)')
if __name__=='__main__':main()
