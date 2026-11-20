#!/usr/bin/env python3
"""Invoke the full Olah Skill Playwright test for every published article."""
from pathlib import Path
import subprocess,sys
from build_site import ROOT,data

if __name__=='__main__':
    _,posts=data(ROOT)
    checker=ROOT/'skills/olah-style-paper-posts/scripts/browser_check.py'
    for p in posts:
        if p['status']!='published':continue
        src=ROOT/'posts'/p['category']/p['slug']/'index.html'
        out=ROOT/'reports'/'articles'/p['slug']
        subprocess.run([sys.executable,str(checker),str(src),'--output',str(out)],check=True)
    print('BROWSER QA COMPLETE for all published posts')
