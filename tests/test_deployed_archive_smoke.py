from __future__ import annotations

from urllib.parse import urljoin
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_deployed_related import archive_contains_c51, feed_contains_c51  # noqa: E402


BASE = "https://example.github.io/xm-posts/"
C51_URL = urljoin(BASE, "posts/reinforcement-learning/c51/")


def page_url(path: str) -> str:
    return urljoin(BASE, path)


def test_archive_follows_rel_next_until_c51_is_found():
    pages = {
        page_url("archive/"): b'<nav><a rel="next" href="page/2/">Next</a></nav>',
        page_url("archive/page/2/"): b'<nav><a rel="next" href="page/3/">Next</a></nav>',
        page_url("archive/page/3/"): b'<a href="../../../posts/reinforcement-learning/c51/">C51</a>',
    }

    assert archive_contains_c51(BASE, fetcher=pages.__getitem__) == 3


def test_archive_returns_zero_when_chain_ends_without_c51():
    pages = {
        page_url("archive/"): b'<a rel="next" href="page/2/">next</a>',
        page_url("archive/page/2/"): b'<p>No target on this page.</p>',
    }

    assert archive_contains_c51(BASE, fetcher=pages.__getitem__) == 0


def test_archive_rejects_pagination_outside_site():
    def fetcher(url: str) -> bytes:
        return b'<a rel="next" href="https://evil.example/archive/">next</a>'

    try:
        archive_contains_c51(BASE, fetcher=fetcher)
    except AssertionError as exc:
        assert "escaped the site" in str(exc)
    else:
        raise AssertionError("external pagination target should be rejected")


def test_archive_detects_pagination_loop():
    archive = page_url("archive/")
    page_two = page_url("archive/page/2/")
    pages = {
        archive: b'<a rel="next" href="page/2/">next</a>',
        page_two: f'<a rel="next" href="{archive}">back</a>'.encode(),
    }

    try:
        archive_contains_c51(BASE, fetcher=pages.__getitem__)
    except AssertionError as exc:
        assert "loop detected" in str(exc)
    else:
        raise AssertionError("pagination loop should be rejected")


def test_archive_has_a_hard_page_limit():
    def endless(url: str) -> bytes:
        return b'<a rel="next" href="next/">next</a>'

    try:
        archive_contains_c51(BASE, fetcher=endless, max_pages=2)
    except AssertionError as exc:
        assert "safety limit" in str(exc)
    else:
        raise AssertionError("unbounded pagination should be rejected")


def test_rss_matches_the_exact_canonical_c51_guid():
    rss = f"""<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item><guid isPermaLink="true">{C51_URL}</guid></item>
    </channel></rss>""".encode()

    assert feed_contains_c51(rss, BASE)


def test_rss_does_not_accept_a_partial_slug_match():
    rss = b"""<?xml version="1.0"?>
    <rss version="2.0"><channel>
      <item><guid>https://example.github.io/xm-posts/posts/reinforcement-learning/c51-copy/</guid></item>
    </channel></rss>"""

    assert not feed_contains_c51(rss, BASE)
