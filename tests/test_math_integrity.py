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


MATHML_ONLY_TAGS = {
    "mi", "mn", "mo", "mtext", "mrow", "mfrac", "msqrt", "mroot",
    "msub", "msup", "msubsup", "munder", "mover", "munderover",
    "mtable", "mtr", "mtd", "mspace", "menclose", "mstyle",
}


def test_mathml_tokens_stay_inside_math_and_delimiters_are_balanced():
    """Catches fragments visually tolerated by HTML but semantically incomplete.

    Piecewise definitions may legitimately use an unclosed left brace; check
    only round/square delimiters, not curly braces.
    """
    problems = []
    for path in sorted((ROOT / "posts").glob("*/*/index.html")):
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for element in soup.find_all(list(MATHML_ONLY_TAGS)):
            if element.find_parent("math") is None:
                problems.append(
                    f"{path.relative_to(ROOT)}: orphan <{element.name}> outside <math>"
                )
        for i, math in enumerate(soup.find_all("math"), 1):
            stack = []
            for ch in math.get_text("", strip=True):
                if ch in "([":
                    stack.append(ch)
                elif ch in ")]":
                    if not stack or (stack.pop(), ch) not in {("(", ")"), ("[", "]")}:
                        problems.append(
                            f"{path.relative_to(ROOT)}: equation {i} unbalanced delimiters"
                        )
                        break
            if stack:
                problems.append(
                    f"{path.relative_to(ROOT)}: equation {i} has unclosed {stack}"
                )
    assert not problems, "\n".join(problems)


def test_importance_sampling_rare_event_variance_is_complete():
    article = ROOT / "posts/foundations/importance-sampling/index.html"
    soup = BeautifulSoup(article.read_text(encoding="utf-8"), "html.parser")
    formulas = [
        m for m in soup.find_all("math")
        if "稀有事件单样本 IS 方差" in m.get("aria-label", "")
        or "事件概率由 p(A) 改为 r" in m.get("aria-label", "")
    ]
    assert len(formulas) == 1
    eq = formulas[0]
    assert eq.find("msup") and eq.find("mfrac")
    assert "Var" in eq.get_text() and "−1" in eq.get_text()
    explanation = eq.find_parent(class_="math-equation").get_text()
    assert "条件分布" in explanation and "q(A)=r" in explanation
    # Under the explicitly stated conditional-mixture proposal.
    p, proposal_probability = 0.01, 0.20
    assert abs(p**2 * (1/proposal_probability - 1) - 0.0004) < 1e-12


def test_pca_frobenius_norms_are_marked_on_both_sides():
    article = ROOT / "posts/classical-ml/pca/index.html"
    soup = BeautifulSoup(article.read_text(encoding="utf-8"), "html.parser")
    energy = next(
        m for m in soup.find_all("math")
        if "Frobenius" in m.get("aria-label", "")
    )
    square_norms = energy.find_all("msubsup")
    assert len(square_norms) == 3
    assert all(
        len([child for child in node.children if getattr(child, "name", None)]) == 3
        and node.find("mi", string="F") is not None
        and node.find("mn", string="2") is not None
        for node in square_norms
    )


def test_bellman_inverse_exponent_uses_operator_and_number():
    article = ROOT / "posts/reinforcement-learning/bellman-equations/index.html"
    soup = BeautifulSoup(article.read_text(encoding="utf-8"), "html.parser")
    matrix = next(
        m for m in soup.find_all("math")
        if "固定策略的矩阵形式" in m.get("aria-label", "")
    )
    exponents = [
        sup for sup in matrix.find_all("msup")
        if sup.find("mo", string="−") and sup.find("mn", string="1")
    ]
    assert len(exponents) == 1
