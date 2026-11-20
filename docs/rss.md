# RSS publishing contract

The feed is a generated publication artifact, **not a hand-edited source file**.

- Canonical URL: `https://1998x-stack.github.io/xm-posts/feed.xml`
- Build source: `scripts/build_site.py::build_feed`
- Publication registry: `content/posts.json`
- Taxonomy source: `content/categories.json`
- Output: `_site/feed.xml` (never commit `_site/`)
- Format: RSS 2.0 + Atom self link + Dublin Core Terms modified date

## Contract

| Field | Value | Stability / meaning |
| --- | --- | --- |
| `rss@version` | `2.0` | Keep for existing subscribers |
| `channel/title` | `xm-posts` | Stable reader-facing title |
| `channel/link` | Site base URL | Absolute URL ending in `/` |
| `channel/description` | Concise Chinese project description | Describes the feed; not an individual article |
| `channel/language` | `zh-cn` | Primary language; individual entries can contain English |
| `atom:link` | Self link to the absolute `feed.xml`, `rel=self`, `type=application/rss+xml` | Reader discovery and feed identity |
| `item/title` | `title` from manifest | Article title |
| `item/link` | Canonical `/posts/<category>/<slug>/` URL | Absolute; derived from build base URL |
| `item/guid` | Same canonical URL, `isPermaLink=true` | Must remain stable when the article is revised |
| `item/description` | Plain-text `summary` | Excerpt, **not full article HTML** |
| `item/pubDate` | RFC 822-compatible GMT date, derived from `published` | See date precision caveat below |
| `item/dcterms:modified` | ISO `YYYY-MM-DD` from `updated` | Date of most recent editorial update |
| `item/category` | Primary category title and topic title | `domain` links to the corresponding category and topic anchor |

### Date precision and ordering

The source manifest records calendar dates (`YYYY-MM-DD`), not timestamps with a timezone. RSS 2.0 requires an RFC 822-style datetime for `pubDate`, so the generator **normalizes the publication day to 00:00:00 GMT**. This is a deterministic serialization convention, **not a claim that an author published at midnight**.

The day-precision `updated` value is emitted as `dcterms:modified` without inventing an exact time. Published posts must have an ISO `updated` date that is no earlier than `published`.

Entries sort by `(updated, published, slug)` descending, using the `slug` only as a deterministic same-day tie-breaker. **An updated article retains its original GUID and publication date.** Not every RSS client will resurface a changed existing entry; do not issue false new GUIDs to force notifications.

No wall-clock `lastBuildDate` is emitted: the same checked-out manifests should build the same feed bytes. Do not imply a publication or feed change occurred simply because CI rebuilt.

### Publication gate

- Only entries marked `status: published` appear; draft and `_topics` placeholders never appear.
- Feed generation uses the same manifest and URL helper as sitemap, archive and category pages.
- XML is serialized and escaped using Python's standard-library XML serializer, not hand-built string concatenation.
- A new public base URL affects `link` and `guid`; changing the base URL is therefore a **subscription migration** and requires a deliberate redirect/migration plan.
- The current feed includes all published entries. If a size limit is later introduced, document its retention period and test for deterministic order and unique GUIDs.
- Homepage and generated indexes link to the feed; each copied article gets an RSS autodiscovery link in the head. Existing valid RSS links are not duplicated.

## Verification

From the repository root:

```bash
python scripts/build_site.py
python -m pytest -q tests/test_rss.py
python scripts/validate_site.py
```

Inspect the generated XML with the standard library:

```bash
python - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
root = ET.fromstring(Path('_site/feed.xml').read_bytes())
items = root.findall('./channel/item')
print('RSS version:', root.attrib['version'])
print('Published items:', len(items))
print('First article:', items[0].findtext('link') if items else '(none)')
PY
```

After deployment, verify the **actual** public endpoint and its latest expected article URL:

```bash
curl -fIL https://1998x-stack.github.io/xm-posts/feed.xml
curl -fsS https://1998x-stack.github.io/xm-posts/feed.xml | head -30
```

A successful local test or merged commit is not proof that GitHub Pages has finished deploying. Confirm the `Publish GitHub Pages` job and the network response separately. If an RSS reader seems stale, check deployment first, then its refresh and cache policies.

## Authoring checklist

1. Update the article's `status`, `published`, `updated`, `summary`, `category`, `topic` and link-critical slug in `content/posts.json`.
2. Use real dates; when revising an existing post, change `updated` but preserve `published`.
3. Do not invent times, fake updates or new GUIDs for the same article.
4. Run RSS, site, math/content and browser tests before a release.
5. Keep README subscription instructions, `AGENTS.md`, and this contract aligned.

## References

- [RSS 2.0 specification](https://www.rssboard.org/rss-specification)
- [RSS best-practice profile — Atom self-link](https://www.rssboard.org/rss-profile)
- [RSS autodiscovery](https://www.rssboard.org/rss-autodiscovery)
- [Dublin Core Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
