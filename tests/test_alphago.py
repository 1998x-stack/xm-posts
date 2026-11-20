"""Deterministic equation checks for the 2016 AlphaGo explainer."""
from pathlib import Path
import runpy
M = runpy.run_path(str(Path(__file__).resolve().parents[1] / "posts/reinforcement-learning/alphago/mini_alphago.py"))
def test_mixing_and_bounds():
    mix=M["mixed_value"]
    assert abs(mix(.6,-1,.5) + .2) < 1e-12
    assert mix(.6,-1,0)==.6 and mix(.6,-1,1)==-1
def test_puct_visit_bonus():
    f=M["puct_score"]
    assert abs(f(.2,.5,3,16,2)-1.2)<1e-12
    assert f(.2,.5,0,16,2)>f(.2,.5,3,16,2)
def test_root_choice_and_perspective():
    assert M["select_most_visited"]({"A":3,"B":10})=="B"
    b=M["backup_alternating_players"](["a","b"],.75)
    assert b["a"]==.75 and b["b"]==-.75


def test_two_asynchronous_streams_and_empty_denominators():
    from math import isclose
    import pytest
    f = M["two_stream_q"]
    assert isclose(f(2, 4, 9, 10, .5), .7)
    assert isclose(f(1, 2, 0, 0, 0), .5)
    assert isclose(f(0, 0, 3, 4, 1), .75)
    with pytest.raises(ValueError):
        f(0, 0, 3, 4, .5)


def test_virtual_loss_restore_and_real_result():
    add, done = M["apply_virtual_loss"], M["resolve_virtual_loss"]
    assert add(10, 4., 3) == (13, 1.)
    assert done(13, 1., 3, 1.) == (11, 5.)
    assert done(13, 1., 3, -1.) == (11, 3.)
    import pytest
    with pytest.raises(ValueError):
        done(1, 0., 3, 1.)


def test_distinct_value_state_sampling_contract():
    sample=M["sampled_value_state"]
    assert sample(1,200)==2 and sample(100,200)==101
    import pytest
    with pytest.raises(ValueError):
        sample(451,500)


def test_deep_visual_post_and_math_semantics():
    from bs4 import BeautifulSoup
    root=Path(__file__).resolve().parents[1]
    article=root/"posts/reinforcement-learning/alphago"
    doc=BeautifulSoup((article/"index.html").read_text(encoding="utf-8"),"html.parser")
    assert len(doc.find_all("svg")) == 15
    assert len(doc.find_all("math")) == 12
    assert len(list((article/"assets").glob("*.svg"))) == 15
    assert len(doc.select("[data-mcts-phase]")) == 4
    assert len(doc.select("[data-vloss]")) == 3
    assert doc.select_one("#mcts-step-picture") is not None
    for m in doc.find_all("math"):
        assert m.get("aria-label") and m.find_parent(attrs={"data-math-scroll":True})
    assert "Extended Data Table 7" in doc.get_text(" ",strip=True)
    assert "2890" in doc.get_text(" ",strip=True)
