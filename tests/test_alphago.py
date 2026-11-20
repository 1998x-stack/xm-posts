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
    assert abs(f(.2,.5,3,16,2)-.7)<1e-12
    assert f(.2,.5,0,16,2)>f(.2,.5,3,16,2)
def test_root_choice_and_perspective():
    assert M["select_most_visited"]({"A":3,"B":10})=="B"
    b=M["backup_alternating_players"](["a","b"],.75)
    assert b["a"]==.75 and b["b"]==-.75
