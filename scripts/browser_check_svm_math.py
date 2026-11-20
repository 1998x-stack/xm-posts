#!/usr/bin/env python3
"""Check real native MathML layout in Chromium, including narrow-screen math scroll."""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SIZES=[("desktop",1440,900),("tablet",768,1024),("mobile",390,844),("narrow",360,800)]

def check(html:Path,output:Path)->dict:
    output.mkdir(parents=True,exist_ok=True)
    report={"article":str(html),"pass":True,"viewports":{},"failures":[]}
    with sync_playwright() as p:
        bin_path=Path(os.getenv("CHROMIUM_PATH","/usr/bin/chromium"))
        opts={"headless":True,"args":["--no-sandbox"]}
        if bin_path.exists():opts["executable_path"]=str(bin_path)
        browser=p.chromium.launch(**opts)
        for label,width,height in SIZES:
            page=browser.new_page(viewport={"width":width,"height":height})
            errors=[]
            page.on("pageerror",lambda err,errors=errors:errors.append(str(err)))
            page.on("console",lambda m,errors=errors:errors.append(m.text) if m.type=="error" else None)
            page.route("https?://**",lambda route:(errors.append("network:"+route.request.url),route.abort()))
            page.set_content(html.read_text(encoding="utf-8"),wait_until="load")
            stats=page.evaluate("""() => {
              const math=[...document.querySelectorAll('math')],blocks=[...document.querySelectorAll('.eq')];
              const frac=document.querySelector('math mfrac');
              const top=frac?.firstElementChild?.getBoundingClientRect();
              const bottom=frac?.lastElementChild?.getBoundingClientRect();
              const dual=document.querySelector('#equation-4 .eq-scroll');
              return {
                mathCount:math.length,blockCount:blocks.length,
                zeroSizedMath:math.filter(e=>e.getBoundingClientRect().height<4||e.getBoundingClientRect().width<2).length,
                fractionStacked:!!top&&!!bottom&&top.top<bottom.top,
                pageOverflow:document.documentElement.scrollWidth>innerWidth+1,
                dualCanScroll:dual.scrollWidth>dual.clientWidth+2,
                dualScrollWidth:dual.scrollWidth,dualClientWidth:dual.clientWidth,
                mathNamespace:math.every(m=>m.namespaceURI==='http://www.w3.org/1998/Math/MathML')
              };
            }""")
            okay=(stats["mathCount"]>=50 and stats["blockCount"]==7
                  and stats["zeroSizedMath"]==0 and stats["fractionStacked"]
                  and not stats["pageOverflow"] and stats["mathNamespace"] and not errors)
            if width<=390 and not stats["dualCanScroll"]:
                okay=False
                errors.append("Expected dual formula internal scrolling at narrow width")
            if width==360 and stats["dualCanScroll"]:
                target=page.locator("#equation-4 .eq-scroll")
                target.focus()
                for _ in range(3):page.keyboard.press("ArrowRight")
                after=target.evaluate("(e)=>e.scrollLeft")
                stats["keyboardScrollLeft"]=after
                if after<=0:
                    okay=False
                    errors.append("Formula cannot be scrolled via keyboard")
            page.locator("#equation-4").scroll_into_view_if_needed()
            page.screenshot(path=str(output/f"math-{label}.png"),full_page=False)
            report["viewports"][label]={"pass":okay,**stats,"errors":errors}
            if not okay:
                report["pass"]=False
                report["failures"].append(label)
            page.close()
        browser.close()
    (output/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html",type=Path,default=ROOT/"posts/classical-ml/svm/index.html")
    parser.add_argument("--output",type=Path,default=ROOT/"reports/svm-math")
    args=parser.parse_args()
    raise SystemExit(0 if check(args.html,args.output)["pass"] else 1)
