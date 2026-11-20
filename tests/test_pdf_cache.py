"""Incremental PDF cache tests: dependencies, corruption fallback and pruning."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pdf_fingerprint import fingerprint
from render_pdfs import PdfCache


def sample_site(tmp_path: Path):
    root = tmp_path / "repo"
    out = root / "_site"
    article = out / "posts" / "architectures" / "test-post"
    article.mkdir(parents=True)
    (root / "scripts").mkdir()
    (root / "scripts" / "render_pdfs.py").write_text("renderer-v1", encoding="utf-8")
    (root / "scripts" / "pdf_fingerprint.py").write_text("fingerprint-v1", encoding="utf-8")
    (root / "requirements-dev.txt").write_text("playwright>=1.53", encoding="utf-8")
    (out / "assets").mkdir()
    (out / "assets" / "related-posts.css").write_text(
        ".xm-related-grid { color: black; }", encoding="utf-8"
    )
    (out / "posts" / "agents" / "another-post" / "assets").mkdir(parents=True)
    cover = out / "posts" / "agents" / "another-post" / "assets" / "cover.svg"
    cover.write_text('<svg viewBox="0 0 1 1"></svg>', encoding="utf-8")
    (article / "assets").mkdir()
    (article / "assets" / "figure.svg").write_text('<svg/>', encoding="utf-8")
    (article / "index.html").write_text(
        '<html><head><link rel="stylesheet" href="../../../assets/related-posts.css">'
        '</head><body><main><img src="assets/figure.svg">'
        '<img src="../../../posts/agents/another-post/assets/cover.svg">'
        '</main></body></html>', encoding="utf-8"
    )
    (out / "archive").mkdir()
    (out / "archive" / "index.html").write_text("archive-v1", encoding="utf-8")
    return root, out, article, cover


def fp(root, out, article):
    return fingerprint(root, out, article, "https://example.org/xm-posts/posts/architectures/test-post/")


def test_fingerprint_only_changes_for_pdf_inputs(tmp_path, monkeypatch):
    monkeypatch.setenv("PDF_FONT_SIGNATURE", "noto=1;stix=1")
    root, out, article, cover = sample_site(tmp_path)
    first = fp(root, out, article)
    assert first == fp(root, out, article)
    (out / "archive" / "index.html").write_text("archive-v2", encoding="utf-8")
    assert fp(root, out, article) == first
    (article / "assets" / "figure.svg").write_text("<svg>changed</svg>", encoding="utf-8")
    second = fp(root, out, article)
    assert second != first
    cover.write_text("<svg>related image changed</svg>", encoding="utf-8")
    third = fp(root, out, article)
    assert third != second
    (out / "assets" / "related-posts.css").write_text(".xm-related-grid{display:none}", encoding="utf-8")
    fourth = fp(root, out, article)
    assert fourth != third
    (root / "scripts" / "render_pdfs.py").write_text("renderer-v2", encoding="utf-8")
    assert fp(root, out, article) != fourth


def test_fingerprint_includes_public_url_and_font_versions(tmp_path, monkeypatch):
    root, out, article, _ = sample_site(tmp_path)
    monkeypatch.setenv("PDF_FONT_SIGNATURE", "fonts-a")
    first = fp(root, out, article)
    monkeypatch.setenv("PDF_FONT_SIGNATURE", "fonts-b")
    assert fp(root, out, article) != first
    assert fingerprint(root, out, article, "https://example.org/different/") != fp(root, out, article)


def test_cache_restore_integrity_and_stale_fallback(tmp_path, monkeypatch):
    # Inspection is covered by render_pdfs.inspect_pdf; isolate cache integrity
    # checks here without invoking Chromium or writing fake 'real' PDFs.
    monkeypatch.setattr("render_pdfs.inspect_pdf", lambda payload, slug: 2)
    cache = PdfCache(tmp_path / "cache")
    payload = b"%PDF-" + b"z" * 5000
    cache.store("example-post", "abc", payload, 2)
    cache.save({"example-post"})
    restored = PdfCache(tmp_path / "cache")
    assert restored.restore("example-post", "abc") == (payload, 2)
    assert restored.restore("example-post", "different") is None
    restored.pdf_path("example-post").write_bytes(payload + b"corrupt")
    assert restored.restore("example-post", "abc") is None


def test_full_build_prunes_unpublished_entries_but_one_post_does_not(tmp_path, monkeypatch):
    monkeypatch.setattr("render_pdfs.inspect_pdf", lambda payload, slug: 2)
    cache = PdfCache(tmp_path / "cache")
    pdf = b"%PDF-" + b"z" * 5000
    cache.store("still-published", "f1", pdf, 2)
    cache.store("now-unpublished", "f2", pdf, 2)
    cache.save(None)  # --only never prunes the rest
    assert cache.pdf_path("now-unpublished").is_file()
    cache.save({"still-published"})  # complete build removes stale entries
    assert not cache.pdf_path("now-unpublished").exists()
    assert "now-unpublished" not in PdfCache(tmp_path / "cache").entries
