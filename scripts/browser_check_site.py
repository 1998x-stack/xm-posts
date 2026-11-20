#!/usr/bin/env python3
"""Exercise real generated Pages site at its /xm-posts/ project subpath."""
from __future__ import annotations
import argparse, contextlib, http.server, json, shutil, socket, tempfile, threading, os
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from build_site import ROOT

SIZES=[('desktop',1440,900),('tablet',768,1024),('mobile',390,844),('narrow',360,800)]

def offline_html(site:Path, page:Path):
    """Fallback when the container security policy blocks localhost and file:// URLs."""
    soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    for link in soup.select('link[rel="stylesheet"]'):
        css=(site/'assets/site.css').read_text(encoding='utf-8')
        tag=soup.new_tag('style');tag.string=css;link.replace_with(tag)
    for script in soup.select('script[src]'):
        js=(site/'assets/site.js').read_text(encoding='utf-8')
        tag=soup.new_tag('script');tag.string=js;script.decompose();soup.body.append(tag)
    return str(soup)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def run(output:Path, site:Path):
    output.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        parent=Path(temp);shutil.copytree(site,parent/'xm-posts')
        handler=lambda *args:Quiet(*args,directory=str(parent))
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_address[1]}/xm-posts/'
        report={'base':base,'viewports':{},'archive':{},'navigation':{},'errors':[],'pass':True,'mode':'http' if os.getenv('GITHUB_ACTIONS')=='true' else 'offline-emulated (local sandbox does not allow http/file navigation)'}
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=True,args=['--no-sandbox'],**({'executable_path':os.getenv('CHROMIUM_PATH','/usr/bin/chromium')} if Path(os.getenv('CHROMIUM_PATH','/usr/bin/chromium')).exists() else {}))
                for label,w,h in SIZES:
                    page=browser.new_page(viewport={'width':w,'height':h})
                    errors=[];status=[]
                    page.on('pageerror',lambda e,log=errors:log.append(str(e)))
                    page.on('console',lambda m,log=errors:log.append(m.text) if m.type=='error' else None)
                    page.on('response',lambda r,log=status:log.append((r.status,r.url)) if r.status>=400 else None)
                    try:
                        if report['mode']=='http':page.goto(base,wait_until='networkidle')
                        else:page.set_content(offline_html(site,site/'index.html'),wait_until='load')
                    except Exception as e:
                        if 'ERR_BLOCKED_BY_ADMINISTRATOR' not in str(e):raise
                        report['mode']='offline-emulated (sandbox policy blocks navigation)'
                        page.set_content(offline_html(site,site/'index.html'),wait_until='load')
                    page.screenshot(path=str(output/f'home-{label}.png'),full_page=False)
                    result=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth+1,h1:document.querySelectorAll('h1').length,cards:document.querySelectorAll('[data-post-card]').length,css:!!document.styleSheets.length})''')
                    okay=not result['overflow'] and result['h1']==1 and result['cards']>=2 and result['css'] and not status and not errors
                    report['viewports'][label]={**result,'pass':okay,'errors':errors,'http_errors':status}
                    if not okay:report['pass']=False
                    if label=='desktop':
                        total=page.locator('[data-post-card]').count()
                        assert page.locator('[data-post-card]:visible').count()==min(8,total)
                        more=page.locator('[data-load-more]')
                        if total>8:
                            assert more.is_visible()
                            more.click()
                            assert page.locator('[data-post-card]:visible').count()==min(16,total)
                        category=page.locator('[data-category-filter]')
                        category.select_option('architectures')
                        visible=page.locator('[data-post-card]:visible')
                        assert visible.count()>=1
                        assert all(visible.nth(i).get_attribute('data-category')=='architectures' for i in range(visible.count()))
                        category.select_option('')
                        search=page.locator('[data-search-input]')
                        search.fill('ResNet')
                        shown=page.locator('[data-post-card]:visible').count()
                        assert shown==1,f'expected 1 matching ResNet, got {shown}'
                        search.fill('no-article-matches-this')
                        assert page.locator('[data-no-results]').is_visible()
                        search.fill('')
                        assert page.locator('[data-post-card]:visible').count()>=2
                        link=page.locator('a[href="./categories/architectures/"]').first
                        assert link.count()>=1
                        if report['mode']=='http':
                            link.click();assert page.url.endswith('/categories/architectures/')
                        else:
                            page.set_content(offline_html(site,site/'categories/architectures/index.html'))
                        assert page.locator('.post-card').count()>=2
                        covers=page.locator('.post-card .cover-illustration img')
                        assert covers.count()==page.locator('.post-card').count()
                        srcs=covers.evaluate_all('(nodes) => nodes.map(n => n.getAttribute("src"))')
                        assert len(set(srcs))==len(srcs), 'Duplicate article cover URLs'
                        covers.first.scroll_into_view_if_needed()
                        if report['mode']=='http':
                            assert covers.first.evaluate('(img) => img.complete && img.naturalWidth > 0'), 'Cover did not load'
                        link=page.locator('a[href="../../posts/architectures/resnet/"]').first
                        assert link.count()>=1
                        if report['mode']=='http':
                            link.click();assert page.url.endswith('/posts/architectures/resnet/')
                        else:
                            page.set_content((site/'posts/architectures/resnet/index.html').read_text(encoding='utf-8'))
                        assert page.locator('svg').count()>=10
                        # CI must check real generated article cards, not only HTML strings.
                        if report['mode']=='http':
                            related=page.locator('[data-xm-related-reading]')
                            assert related.count()==1, 'ResNet: missing generated reading section'
                            assert page.locator('link[href="../../../assets/related-posts.css"]').count()==1
                            related.scroll_into_view_if_needed()
                            assert related.is_visible(), 'ResNet: reading section is hidden'
                            cards=related.locator('a.xm-related-card')
                            assert 2<=cards.count()<=4, 'Unexpected related card count'
                            for idx in range(cards.count()):
                                card=cards.nth(idx)
                                assert card.is_visible()
                                img=card.locator('img')
                                img.scroll_into_view_if_needed()
                                assert img.evaluate('(el) => el.complete && el.naturalWidth > 0'), 'Related SVG failed to load'
                                assert card.get_attribute('href').startswith('../../../posts/')
                            box=related.bounding_box()
                            assert box and box['width']>200, 'Related section has zero width'
                            page.screenshot(path=str(output/'related-desktop.png'),full_page=False)
                            report['navigation']['related_cards']='passed'
                        assert page.locator('.sitebar .brand').get_attribute('href')=='../../../'
                        if report['mode']=='http':
                            page.locator('.sitebar .brand').click();assert page.url.rstrip('/')==base.rstrip('/')
                        else:
                            page.set_content(offline_html(site,site/'index.html'))
                        assert page.locator('[data-post-card]').count()>=2
                        report['navigation'].update({'search':'passed','category':'passed','article':'passed','back_to_home':'passed'})
                    if label=='narrow':
                        toggle=page.locator('[data-menu-toggle]')
                        assert toggle.is_visible()
                        toggle.click()
                        assert toggle.get_attribute('aria-expanded')=='true'
                        assert page.locator('#site-nav').is_visible()
                        page.keyboard.press('Escape')
                        assert toggle.get_attribute('aria-expanded')=='false'
                        if report['mode']=='http':
                            page.goto(base+'categories/architectures/',wait_until='networkidle')
                            category_qa=page.evaluate('''() => ({overflow:document.documentElement.scrollWidth>innerWidth+1,covers:[...document.querySelectorAll('.cover-illustration img')].length})''')
                            assert not category_qa['overflow'], 'Category card covers overflow at 360px'
                            assert category_qa['covers']>=2
                            category_cover=page.locator('.cover-illustration img').first
                            category_cover.scroll_into_view_if_needed()
                            assert category_cover.evaluate('(img) => img.complete && img.naturalWidth > 0')
                            page.screenshot(path=str(output/'category-narrow.png'),full_page=False)
                            # Catch mobile-only CSS / clipping defects in the generated Post itself.
                            page.goto(base+'posts/architectures/resnet/',wait_until='networkidle')
                            section=page.locator('[data-xm-related-reading]')
                            assert section.count()==1 and section.is_visible()
                            section.scroll_into_view_if_needed()
                            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'), (
                                'Related reading causes mobile horizontal overflow')
                            assert section.locator('.xm-related-card').count()>=2
                            for image in section.locator('img').all():
                                image.scroll_into_view_if_needed()
                                assert image.evaluate('(el) => el.complete && el.naturalWidth > 0')
                            first=section.locator('a.xm-related-card').first
                            assert first.is_visible()
                            target=first.get_attribute('href')
                            first.focus()
                            assert first.evaluate('(el) => document.activeElement === el')
                            page.screenshot(path=str(output/'related-narrow.png'),full_page=False)
                            first.click()
                            assert page.url.endswith(target.removeprefix('../../../').rstrip('/')+'/'), (
                                'Related card click navigated to the wrong article')
                            report['navigation']['related_mobile']='passed'
                    # Verify the archive at each desktop/tablet/mobile width.
                    # CI uses HTTP mode; the offline sandbox checks layout + DOM.
                    # Previous article navigation may request its own absent favicon;
                    # don't misattribute that earlier 404 to the archive itself.
                    errors.clear()
                    status.clear()
                    if report['mode']=='http':
                        page.goto(base+'archive/',wait_until='networkidle')
                    else:
                        page.set_content(offline_html(site,site/'archive/index.html'),wait_until='load')
                    entries=page.locator('.archive-entry')
                    thumbs=page.locator('.archive-entry .archive-cover img')
                    assert entries.count()>=60 and thumbs.count()==entries.count()
                    paths=thumbs.evaluate_all('(images) => images.map(img => img.getAttribute("src"))')
                    assert len(set(paths))==len(paths), 'Archive has duplicate SVG cover paths'
                    assert all(path.startswith('../posts/') and path.endswith('.svg') for path in paths)
                    first=thumbs.first
                    first.scroll_into_view_if_needed()
                    if report['mode']=='http':
                        page.wait_for_function("() => {const img=document.querySelector('.archive-cover img'); return img && img.complete && img.naturalWidth > 0}")
                    archive_layout=page.evaluate('''() => ({
                        overflow:document.documentElement.scrollWidth>innerWidth+1,
                        h1:document.querySelectorAll('h1').length,
                        entries:document.querySelectorAll('.archive-entry').length,
                        thumbnails:document.querySelectorAll('.archive-cover img').length
                    })''')
                    assert not archive_layout['overflow'],f'Archive overflows at {w}px'
                    assert archive_layout['h1']==1
                    report['archive'][label]={**archive_layout,'pass':True}
                    page.screenshot(path=str(output/f'archive-{label}.png'),full_page=False)
                    if label=='desktop' and report['mode']=='http':
                        page.locator('.archive-cover').first.click()
                        assert '/posts/' in page.url, 'Archive thumbnail must navigate to article'
                        page.go_back(wait_until='networkidle')
                        assert page.url.endswith('/archive/')
                    assert not errors and not status,(errors,status)
                    page.close()
                browser.close()
        finally:server.shutdown();server.server_close()
        (output/'site-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))
        return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=Path('reports/site'))
    ap.add_argument('--site',type=Path,default=ROOT/'_site')
    args=ap.parse_args()
    r=run(args.output,args.site)
    raise SystemExit(0 if r['pass'] else 1)
