"""Deterministic tests for pedagogical AlexNet shape arithmetic."""
import importlib.util
from pathlib import Path
import pytest

SOURCE=Path(__file__).resolve().parents[1]/"posts/architectures/alexnet/mini_alexnet.py"
spec=importlib.util.spec_from_file_location("mini_alexnet",SOURCE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_conv1_boundary_conventions():
    assert m.conv_out(227,11,4,0)==55
    assert m.conv_out(224,11,4,2)==55
    assert m.conv_out(224,11,4,0)==54
    assert m.shape_trace(227,0)==(55,27,13,6)
    assert m.shape_trace(224,2)==(55,27,13,6)

def test_grouping_changes_connectivity_and_parameter_count():
    assert m.grouped_conv_params(96,256,5,2)==307456
    assert m.grouped_conv_params(96,256,5,1)==614656
    assert m.fc_params(9216,4096)==37752832

def test_invalid_spatial_and_group_shapes():
    with pytest.raises(ValueError):m.conv_out(3,11)
    with pytest.raises(ValueError):m.conv_out(10,3,0)
    with pytest.raises(ValueError):m.grouped_conv_params(95,256,5,2)

def test_published_manifest_and_article_evidence():
    import json
    root=Path(__file__).resolve().parents[1]
    posts=json.loads((root/"content/posts.json").read_text(encoding="utf-8"))
    alex=[p for p in posts if p["slug"]=="alexnet"]
    assert len(alex)==1 and alex[0]["category"]=="architectures" and alex[0]["status"]=="published"
    evidence=json.loads((SOURCE.parent/"evidence.json").read_text(encoding="utf-8"))
    assert len(evidence)>=10
    assert all(row["source_url"].startswith("https://") and row["locator"] for row in evidence)
