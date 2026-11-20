"""Regression checks for the paper-explainer Skill's MathML validation gate."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/olah-style-paper-posts"
spec = importlib.util.spec_from_file_location("math_skill_validator", SKILL / "scripts/validate.py")
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)

SOURCE = (ROOT / "examples/resnet/index.html"
          if (ROOT / "examples/resnet/index.html").exists()
          else ROOT / "posts/architectures/resnet/index.html")
VALID_MATH = (
    '<div class="math-equation"><div class="math-scroll" data-math-scroll '
    'tabindex="0" role="region" aria-label="数学公式，可横向滚动">'
    '<math display="block" aria-label="a 除以 b"><mfrac><mi>a</mi><mi>b</mi></mfrac></math>'
    '</div></div>'
)

def check_html(tmp_path, fragment):
    html = SOURCE.read_text(encoding="utf-8")
    assert "</body>" in html
    html = html.replace("</body>", fragment + "</body>", 1)
    path = tmp_path / "test-article.html"
    path.write_text(html, encoding="utf-8")
    return validator.validate(path)

def test_valid_structured_math(tmp_path):
    result = check_html(tmp_path, VALID_MATH)
    assert result["pass"], result["failures"]
    assert result["counts"]["mathml"] == 1

def test_math_in_svg_rejected(tmp_path):
    html = SOURCE.read_text(encoding="utf-8")
    assert "</svg>" in html
    bad = '<text><math aria-label="bad"><mi>x</mi></math></text>'
    html = html.replace("</svg>", bad + "</svg>", 1)
    p = tmp_path / "broken-svg.html"
    p.write_text(html, encoding="utf-8")
    res = validator.validate(p)
    assert not res["pass"]
    assert any("nested inside SVG" in failure for failure in res["failures"])

def test_fraction_arity_rejected(tmp_path):
    bad = VALID_MATH.replace("<mi>a</mi><mi>b</mi>", "<mi>a</mi>")
    res = check_html(tmp_path, bad)
    assert not res["pass"]
    assert any("malformed mfrac" in failure for failure in res["failures"])

def test_missing_math_label_rejected(tmp_path):
    res = check_html(tmp_path, VALID_MATH.replace('aria-label="a 除以 b"', ""))
    assert not res["pass"]
    assert any("missing accessible description" in failure for failure in res["failures"])

def test_display_requires_keyboard_scroll_region(tmp_path):
    bad = VALID_MATH.replace('tabindex="0"', 'tabindex="-1"')
    res = check_html(tmp_path, bad)
    assert not res["pass"]
    assert any("keyboard-focusable" in failure for failure in res["failures"])

def test_skill_reference_explains_offline_and_svg_boundary():
    doc=(SKILL/"references/math-typesetting.md").read_text(encoding="utf-8")
    for phrase in ("MathML Core", "mfrac", "SVG", "keyboard", "offline"):
        assert phrase in doc
