from __future__ import annotations
import json
from pathlib import Path
import sys
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "posts/evaluation/anthropic-safety-evaluations"))
sys.path.insert(0, str(ROOT / "posts/systems/agent-scale-source-control"))
sys.path.insert(0, str(ROOT / "posts/agents/agent-containment"))

from safety_eval_demo import appropriate_response_rate
from source_control_demo import sparse_object_set
from agent_containment_demo import inside_workspace


def test_trajectory_rate_requires_every_turn_to_pass():
    data = [
        [{"appropriate": True}, {"appropriate": True}],
        [{"appropriate": True}, {"appropriate": False}],
        [{"appropriate": True}],
    ]
    assert appropriate_response_rate(data) == 2 / 3


def test_trajectory_rate_rejects_empty_input():
    try:
        appropriate_response_rate([])
    except ValueError:
        pass
    else:
        raise AssertionError("empty evaluation set must fail loudly")


def test_sparse_object_selector_only_returns_requested_subtree():
    objects = {
        "src/api/routes.py": b"a",
        "src/api/schema.py": b"b",
        "src/core/loop.py": b"c",
        "docs/guide.md": b"d",
    }
    assert sparse_object_set(objects, ["src/api"]) == [
        "src/api/routes.py", "src/api/schema.py"
    ]


def test_workspace_boundary_resolves_symlinks(tmp_path):
    workspace = tmp_path / "workspace"
    outside = tmp_path / "outside"
    workspace.mkdir()
    outside.mkdir()
    (outside / "secret.txt").write_text("not readable", encoding="utf-8")
    link = workspace / "shortcut"
    link.symlink_to(outside, target_is_directory=True)
    assert inside_workspace(workspace, workspace / "notes.txt")
    assert not inside_workspace(workspace, link / "secret.txt")


def test_draft_articles_have_independent_svg_and_evidence():
    entries = [
        ("evaluation", "anthropic-safety-evaluations"),
        ("systems", "agent-scale-source-control"),
        ("agents", "agent-containment"),
    ]
    for category, slug in entries:
        directory = ROOT / "posts" / category / slug
        html = BeautifulSoup((directory / "index.html").read_text(encoding="utf-8"), "html.parser")
        assert len(html.select("h1")) == 1
        svgs = html.select("svg")
        assert len(svgs) >= 4
        ids = [node.get("id") for node in html.select("[id]")]
        assert len(ids) == len(set(ids))
        for svg in svgs:
            assert svg.find("title") is not None
            assert svg.find("desc") is not None
        assets = list((directory / "assets").glob("*.svg"))
        assert len(assets) >= 4
        evidence = json.loads((directory / "evidence.json").read_text(encoding="utf-8"))
        assert len(evidence) >= 6
        assert all(item.get("source_url", "").startswith("https://www.anthropic.com/") for item in evidence)
