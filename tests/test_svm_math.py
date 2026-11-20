"""SVM mathematical typography and fallback-free offline rendering gate."""
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"posts/classical-ml/svm/index.html"

def test_mathml_blocks_have_fraction_and_limits():
    soup=BeautifulSoup(FILE.read_text(encoding="utf-8"),"html.parser")
    blocks=soup.select(".eq")
    assert len(blocks)==7
    assert [x.get("id") for x in blocks]==[f"equation-{i}" for i in range(1,8)]
    assert len(soup.select(".eq math[display=block]"))==10
    assert len(soup.select("math.math-inline"))>=35
    assert len(soup.select("math mfrac"))>=6
    assert soup.select("#equation-1 mfrac")
    assert soup.select("#equation-4 munderover")
    assert soup.select("#equation-6 .eq-condition math")
    assert soup.select("#equation-7 munder")
    assert all(x.get("tabindex")=="0" and x.get("role")=="region"
               for x in soup.select(".eq-condition"))
    assert not soup.select("span.eq")
    assert not soup.select("svg math"), "MathML cannot be embedded into SVG text labels"

def test_display_math_accessibility_and_offline_rendering():
    soup=BeautifulSoup(FILE.read_text(encoding="utf-8"),"html.parser")
    math=soup.find_all("math")
    assert len(math)>=50
    assert all(x.get("aria-label") for x in math)
    assert all(x.find(["mi","mn","mfrac","mrow","munder","munderover"]) for x in math)
    assert all(x.get("tabindex")=="0" and x.get("role")=="region"
               for x in soup.select(".eq-scroll"))
    assert len(soup.select(".eq-scroll"))==7
    assert not soup.select('script[src^="http"],link[href^="http"]')
    css=soup.style.get_text()
    assert ".eq-scroll" in css and "overflow-x:auto" in css
    assert ".math-inline" in css and "@media print" in css
