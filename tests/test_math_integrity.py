"""Guard MathML's mathematical meaning, not only its visual appearance.

In particular, an arithmetic expression such as t-1 must not be encoded as a
single <mi> identifier, and DeltaNet's rank-one key must retain its time index.
"""
from pathlib import Path
import re

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
MATH_OPERATOR_IN_IDENTIFIER = re.compile(r"[+−=<>(),;/]")


def test_mathml_identifiers_do_not_hide_expressions():
    problems = []
    articles = sorted((ROOT / "posts").glob("*/*/index.html"))
    assert articles, "No source HTML posts found"
    for path in articles:
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for math in soup.find_all("math"):
            for ident in math.find_all("mi"):
                value = ident.get_text(strip=True)
                if MATH_OPERATOR_IN_IDENTIFIER.search(value):
                    problems.append(f"{path.relative_to(ROOT)}: <mi>{value}</mi>")
    assert not problems, (
        "Separate variables (<mi>), arithmetic/comma operators (<mo>), and "
        "numbers (<mn>), grouping expression scripts with <mrow>:\n"
        + "\n".join(problems)
    )


def test_deltanet_rank_one_update_uses_time_indexed_key():
    article = ROOT / "posts/architectures/deltanet/index.html"
    soup = BeautifulSoup(article.read_text(encoding="utf-8"), "html.parser")
    keyed_transposes = []
    for node in soup.select("math msubsup"):
        children = [child for child in node.children if getattr(child, "name", None)]
        if [child.name for child in children] != ["mi", "mi", "mo"]:
            continue
        if [child.get_text(strip=True) for child in children] == ["k", "t", "⊤"]:
            keyed_transposes.append(node)
    assert len(keyed_transposes) == 4, (
        "DeltaNet should use k_t^T in the ordinary, delta-corrected, and "
        "matrix-factored state updates (4 appearances)"
    )



def test_ppo_squares_are_powers_and_clip_term_is_samplewise():
    article = ROOT / "posts/reinforcement-learning/ppo/index.html"
    soup = BeautifulSoup(article.read_text(encoding="utf-8"), "html.parser")
    maths = soup.find_all("math")
    gae, objective = maths[4], maths[5]
    assert any(
        sup.find("mi", string="γ") and sup.find("mi", string="λ")
        and sup.find("mn", string="2")
        for sup in gae.find_all("msup")
    ), "The GAE expansion must show (γλ)^2, not (γλ)2"
    assert any(
        sup.find("mi", string="V") and sup.find("mn", string="2")
        for sup in objective.find_all("msup")
    ), "The value regression residual must be squared"
    assert objective.find("msubsup") is not None, (
        "The joint objective must average per-timestep ℓ_t^CLIP, "
        "not re-average the global L^CLIP"
    )
