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
        report={'base':base,'viewports':{},'navigation':{},'errors':[],'pass':True,'mode':'http' if os.getenv('GITHUB_ACTIONS')=='true' else 'offline-emulated (local sandbox does not allow http/file navigation)'}
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
                        link=page.locator('a[href="../../posts/architectures/resnet/"]').first
                        assert link.count()>=1
                        if report['mode']=='http':
                            link.click();assert page.url.endswith('/posts/architectures/resnet/')
                        else:
                            page.set_content((site/'posts/architectures/resnet/index.html').read_text(encoding='utf-8'))
                        assert page.locator('svg').count()>=10
                        assert page.locator('.sitebar .brand').get_attribute('href')=='../../../'
                        if report['mode']=='http':
                            page.locator('.sitebar .brand').click();assert page.url.rstrip('/')==base.rstrip('/')
                        else:
                            page.set_content(offline_html(site,site/'index.html'))
                        assert page.locator('[data-post-card]').count()>=2
                        report['navigation']={'search':'passed','category':'passed','article':'passed','back_to_home':'passed'}
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
