"""CI performance metrics and browser partitioning regression tests."""
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from browser_check_all import partition_articles
from ci_metrics import pdf_from_log, record_start, report, run_step


def test_browser_shards_deterministic_and_exhaustive():
    articles = [(f"post-{i}", "foundations") for i in range(72)]
    groups = partition_articles(articles[::-1], 3)
    assert [len(x) for x in groups] == [24, 24, 24]
    assert groups == partition_articles(articles, 3)
    assert sorted(item for group in groups for item in group) == sorted(articles)
    assert not any(set(groups[i]) & set(groups[j]) for i in range(3) for j in range(i + 1, 3))


def test_browser_shards_fail_closed_on_duplicates_or_invalid_count():
    with pytest.raises(ValueError):
        partition_articles([("same", "a"), ("same", "b")], 2)
    with pytest.raises(ValueError):
        partition_articles([("first", "a")], 0)


def test_ci_timing_and_pdf_summary(tmp_path):
    measurements = tmp_path / "reports" / "ci"
    record_start(measurements)
    log = measurements / "pdf-render.log"
    command = [
        sys.executable, "-c",
        "print('PDF CACHED example'); print('{\"pdf_count\":2,\"cached\":1,\"rendered\":1,\"total_bytes\":10000}')"
    ]
    assert run_step(measurements, "pdf", command, log=log) == 0
    assert pdf_from_log(log)["cached"] == 1

    browser = tmp_path / "reports" / "browser-all-summary.json"
    browser.write_text(json.dumps({
        "pass": True, "expected_articles": 2, "verified_articles": 2,
        "workers": 2, "browser_launches": 2, "elapsed_seconds": 8.0
    }), encoding="utf-8")
    site = tmp_path / "_site"
    site.mkdir()
    (site / "index.html").write_text("hello", encoding="utf-8")
    markdown, data = report(measurements, log, browser, site)
    assert "50.0% cache hits" in markdown
    assert "2/2 posts" in markdown
    assert data["site_bytes"] == 5
    assert data["phases"][0]["exit_code"] == 0
    assert data["measured_wall_seconds"] >= 0


def test_pdf_log_missing_is_not_reported_as_zero(tmp_path):
    assert pdf_from_log(tmp_path / "missing.log") is None
    file = tmp_path / "bad.log"
    file.write_text('not json\n{"pdf_count":2,"cached":2,"rendered":1,"total_bytes":100}\n', encoding="utf-8")
    assert pdf_from_log(file) is None


def test_failed_command_still_emits_timing(tmp_path):
    directory = tmp_path / "ci"
    assert run_step(directory, "failure", [sys.executable, "-c", "raise SystemExit(7)"]) == 7
    data = json.loads((directory / "failure.json").read_text(encoding="utf-8"))
    assert data["exit_code"] == 7
    assert data["seconds"] >= 0
