"""Guard stable category/topic IDs and published article metadata."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_taxonomy_schema_and_placeholders():
    categories = json.loads((ROOT / "content/categories.json").read_text(encoding="utf-8"))
    assert len({c["slug"] for c in categories}) == len(categories)
    mapping = {}
    for category in categories:
        topics = category["topics"]
        slugs = [t["slug"] for t in topics]
        titles = [t["title"].strip().casefold() for t in topics]
        assert len(slugs) == len(set(slugs)), category["slug"]
        assert len(titles) == len(set(titles)), category["slug"]
        assert (ROOT / "posts" / category["slug"] / "README.md").is_file()
        mapping[category["slug"]] = set(slugs)
    for placeholder in (ROOT / "posts").glob("*/_topics/*/README.md"):
        _, category, _, topic, _ = placeholder.relative_to(ROOT).parts
        assert topic in mapping[category], str(placeholder)


def test_post_taxonomy_and_uniqueness():
    categories = json.loads((ROOT / "content/categories.json").read_text(encoding="utf-8"))
    posts = json.loads((ROOT / "content/posts.json").read_text(encoding="utf-8"))
    mapping = {c["slug"]: {t["slug"] for t in c["topics"]} for c in categories}
    keys = set()
    for post in posts:
        key = (post["category"], post["slug"])
        assert key not in keys, key
        keys.add(key)
        assert post["topic"] in mapping[post["category"]], key
        if post["status"] == "published":
            assert (ROOT / "posts" / post["category"] / post["slug"] / "index.html").is_file(), key
