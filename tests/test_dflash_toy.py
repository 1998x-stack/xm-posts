from pathlib import Path
import runpy
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1] / "posts/inference/dflash"

def test_dflash_toy():
    runpy.run_path(str(ROOT / "toy_dflash.py"))["self_test"]()

def test_dflash_svg_sources():
    files = sorted((ROOT / "assets").glob("*.svg"))
    assert len(files) == 5
    html = (ROOT / "index.html").read_text()
    for path in files:
        content = path.read_text()
        assert content.strip() in html
        root = ET.fromstring(content)
        assert "viewBox" in root.attrib
        assert root.find("{http://www.w3.org/2000/svg}title") is not None
