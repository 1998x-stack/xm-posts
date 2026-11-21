"""Whole-repository evidence-ledger contract for every published article."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import data

SKILL_VALIDATOR = ROOT / "skills" / "olah-style-paper-posts" / "scripts"
sys.path.insert(0, str(SKILL_VALIDATOR))
from validate import validate_evidence_ledger


def test_every_published_article_has_a_traceable_evidence_ledger():
    _, posts = data(ROOT)
    published = [post for post in posts if post["status"] == "published"]
    assert published
    for post in published:
        evidence = ROOT / "posts" / post["category"] / post["slug"] / "evidence.json"
        result = validate_evidence_ledger(evidence)
        assert result["pass"], f"{post['slug']}: {result['failures']}"
        assert result["claim_count"] >= 1, post["slug"]
        missing_notes = [warning for warning in result["warnings"] if "notes should explain" in warning]
        assert not missing_notes, f"{post['slug']}: {missing_notes}"


def test_evidence_ledger_rejects_untraceable_claims(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps([
        {"id": "A1", "claim": "claim", "kind": "paper",
         "source_url": "http://example.org/paper", "locator": "Table 1",
         "status": "verified", "notes": "scope"},
    ]), encoding="utf-8")
    result = validate_evidence_ledger(path)
    assert not result["pass"]
    assert any("HTTPS" in failure for failure in result["failures"])


def test_unverified_evidence_is_visible_as_a_warning_not_silently_passed(tmp_path):
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps([
        {"id": "A1", "claim": "claim", "kind": "paper",
         "source_url": "https://example.org/paper", "locator": "Section 1",
         "status": "unverified", "notes": "source not independently checked"},
    ]), encoding="utf-8")
    result = validate_evidence_ledger(path)
    assert result["pass"]
    assert any("unverified" in warning for warning in result["warnings"])
