from pathlib import Path
import subprocess
import sys
from bs4 import BeautifulSoup

ARTICLE=Path(__file__).resolve().parents[1]/"posts/inference/dspark"

def test_dspark_demo():
    subprocess.run([sys.executable,str(ARTICLE/"demo.py")],check=True)

def test_dspark_source():
    soup=BeautifulSoup((ARTICLE/"index.html").read_text(encoding="utf-8"),"html.parser")
    assert len(soup.find_all("h1"))==1
    assert len(soup.find_all("figure"))==7
    assert len(soup.find_all("math"))>=10
    ids=[x["id"] for x in soup.find_all(id=True)]
    assert len(ids)==len(set(ids))
    for svg in soup.find_all("svg"):
        assert (ARTICLE/"assets"/svg["data-export"]).is_file()
        assert svg.find("title") and svg.find("desc")
    for link in soup.select('nav a[href^="#"]'):
        assert soup.find(id=link["href"][1:])
