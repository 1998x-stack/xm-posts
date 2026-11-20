# AGENTS.md — xm-posts repository instructions

Applies to **all agent-authored changes in this repository** (including Claude, Pi, Codex / generic agents, and OpenCode). In case of conflict, **scientific truth, user intent, and repository tests** outrank visual preference. This file is the repo-level contract; detailed paper-explainer workflows live in [`skills/olah-style-paper-posts/SKILL.md`](skills/olah-style-paper-posts/SKILL.md).

## 1. Mission and deliverable

Create evidence-grounded, pedagogically progressive, illustrated technical articles on neural networks, LLMs and systems. An accepted Post has semantic offline-capable HTML, editable standalone SVGs, a claims/evidence ledger, relevant runnable examples, and browser QA proof. Never trade correctness for novelty, beauty or word count.

## 2. Know your boundaries

- **Source of truth** for categories and stable second-level topic IDs: `content/categories.json` (`topics: [{slug,title}]`); for post publication, explicit `category` + `topic`, cards, RSS and sitemap: `content/posts.json`.
- **Source of truth** for article HTML and assets: `posts/<category>/<slug>/index.html`, `assets/*.svg`, `evidence.json`; optional minimal code lives beside the article.
- **Source of truth for article card covers:** published entries in `content/posts.json` must contain `cover.src` (a real, local `assets/*.svg` from that same article) and `cover.caption` (one distinctive, concept-specific explanatory sentence). The builder uses these for homepage and category cards. Do not add a fallback cover in `scripts/build_site.py`.
- **Source of truth** for skill: `skills/olah-style-paper-posts/`; four mirrored copies in `.claude/skills/`, `.pi/skills/`, `.agent/skills/`, `.opencode/skills/` must be byte-identical.
- **Source of truth** for static site logic: `scripts/build_site.py`, `site/assets/`; generated `_site/` is disposable and must never be committed.
- **Source of truth** for deployment: `.github/workflows/publish.yml`. PRs test only. A merge/push to `main` triggers Pages build and deployment; do not publish drafts.

Never edit the four agent mirrors directly. Change canonical skill, then `python scripts/sync_skills.py` and `--check`.

## 3. Non-negotiable article quality gates

1. **Evidence.** Read primary paper and figure captions; identify model version and dataset/split/metric. Put important claims in `evidence.json` with source link and locator. Do not invent ablation values or training behaviors. Treat code samples as code, not as a historical reproduction.
2. **Narrative.** Start with the concrete problem and intuition before equations. One diagram must answer one question; go from simple to complex through visibly distinct states. Avoid a long disconnected list of features.
3. **Mathematics.** State variable definitions and shape changes, masks, and normalization placement. Label toy examples, inference-time choices, and later model variants separately.
4. **SVG.** `viewBox`, accessible `<title>`/label, unique IDs **across the whole HTML document** (do not reuse `id="arrow"` in 13 SVGs), readable font sizes, unambiguous color roles; extract and inspect standalone SVGs in the browser.
5. **HTML/CSS/JS.** One `h1`, semantic `<main>`, `nav`, figure captions, accessible controls, keyboard focus, small-screen/print/reduced-motion support, no CDN or unnecessary network dependency. Default state must explain without running JS.
6. **Card cover.** Before marking a Post published, select an original SVG from that article which *illustrates its central mechanism*, and write an accurate, unique caption to `content/posts.json`. It must visually differ from other article covers and remain intelligible on a small card. Never use generic slogans, a placeholder formula, or one shared image for many articles.
7. **QA.** Run source validator, site builder, cross-page fragment/link checker, tests and actual Playwright at 1440/768/390/360px. Test a real interaction, inspect errors/overflow and ensure keyboard use. For covers, verify local image loads, unique SVG image content, meaningful caption, no clipping or horizontal overflow. Do not call skipped checks 'passed'.
8. **Release.** Publish a branch/PR, review diff & CI; only then merge and verify `main`, Pages run and reachable URLs. Do not assert production deployment merely because a workflow exists.

Read the full process in `skills/olah-style-paper-posts/references/{paper-extraction,narrative-architecture,evidence-and-citation,html-design-system,svg-production,implementation-and-interactivity,browser-qa,publishing}.md`.

## 4. Make a new Post

```bash
python scripts/new_post.py inference understanding-kv-cache \
  --topic kv-cache \
  --title 'Understanding KV Cache' \
  --subtitle '为什么缓存可以改善自回归推理？' \
  --paper 'https://arxiv.org/...'
```

This creates **draft** metadata. Replace the template with an actual, referenced explanation; create independent SVGs and evidence; run required QA; update `reading_minutes`, `summary`, `tags`, `published`, **`cover.src` and `cover.caption`**, and finally `status` from `draft` to `published`. Never change state solely because a file exists. Never create fake placeholder posts in `content/posts.json` with `status: published`.

For new categories, add an entry to `content/categories.json` and a `posts/<category>/README.md` placeholder. Every post must use exactly one registered second-level `topic` slug; use tags for cross-domain concepts. Generated `/topics/` and category `#topic-<slug>` anchors are public links, so preserve slug stability. Do not hand-edit the generated site indexes or hardcode new post cards.

## 5. How to validate

Run from repository root:

```bash
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python scripts/sync_skills.py --check
python scripts/build_site.py
python scripts/validate_site.py
python -m pytest -q
python skills/olah-style-paper-posts/scripts/browser_check.py posts/architectures/resnet/index.html --output reports/resnet
python skills/olah-style-paper-posts/scripts/browser_check.py posts/architectures/transformer/index.html --output reports/transformer
```

For a new Post, replace the browser-check path with that Post's `index.html` (the CI should be extended to cover it). Before any claim that the deployed site works, separately visit the generated Pages URL or inspect a successful deployed workflow and GET status.

## 6. Content prohibitions

- No fabricated references, claims, code results or benchmarking numbers. No unsupported claim of 'tested', 'live', or 'published'.
- No wholesale copy of Colah, Harvard NLP, original paper figure assets, or third-party licensed material.
- No article-header/footer production chatter, e.g. `原创图解 · 单文件离线 HTML`, `用直觉 → 图示 → 数学 → 工程实现，理解残差网络 · 参考 Colah 风格，非原文翻译`, or `原创教程 · 单 HTML 文件`.
- No remote scripts/fonts/trackers, no secrets, no unreviewed HTML injection, no accidental publication of `_site/`, tool folders or drafts.
- No repeated card illustrations, no hard-coded `Observe → Derive → Verify` fallback, no stock-image substitutes, no thumbnail copies of third-party paper figures, and no random visuals unrelated to an article's mechanism.
- No bypassing CI, weakening `status: published` gate, replacing an existing scientific explanation with a glossy placeholder, or duplicating an agent skill fork with divergent instructions.

## 7. PR hand-off checklist

- [ ] Primary sources and numerical evidence checked, original vs modern variants separated.
- [ ] `index.html` accurate with 1 H1, correct semantic structure and navigable sections.
- [ ] SVGs tested alone and embedded; no cross-document duplicate IDs.
- [ ] Relevant code examples have deterministic asserts; limits documented.
- [ ] `content/posts.json` accurate; drafts excluded.
- [ ] Every published entry includes its own validated `cover.src` and distinct explanatory `cover.caption`; card covers load and remain readable on phone and desktop.
- [ ] Build and link validation pass, genuine browser interaction verified.
- [ ] Four skill mirrors match canonical; README and docs match paths and deployment.
- [ ] CI passes; production claims only after actual deployed site verified.

## Card cover design contract (required for every published article)

The cover should let a student recognize **what happens inside the model** at a glance, not just fill a rectangle. For each new article, follow this workflow:

1. Read the mechanism explanation and choose a **specific visual question** (e.g. “which tokens share K/V heads?”, “how does a B+ tree split?”, “what does clipping change?”). Choose one of the article's independently authored, self-contained SVG figures that answers that question; prefer a legible mechanism/geometry/process diagram over a dense results table.
2. In that article's entry in `content/posts.json`, add the corresponding `cover` object; e.g. `"cover": {"src": "assets/02-head-sharing.svg", "caption": "多个 Query 头共享一组 Key 与 Value"}`. The example is **specific to GQA**; replace the file and caption for every other article. `src` is relative to `posts/<category>/<slug>/`; it must be a local SVG under `assets/` with no `..`, URL or remote dependency. The caption is one unique concise Chinese explanation (8–80 characters), not a generic tagline.
3. **One post, one carefully chosen cover.** Never silently reuse a common default or the same generic formula across cards; do not rely on random gradients, title-only placeholders, or repeated “Observe / Derive / Verify”. Cards may share a typographic frame, but their illustrations must be article-specific.
4. The illustration must survive a roughly 300–500 px-wide card: show the complete graphic (`object-fit: contain`), avoid clipped equations, minuscule labels and color-only meanings. If necessary, improve the source SVG or choose a more legible one; never copy third-party paper figures without permission.
5. The static builder renders the same cover on category cards, homepage spotlight and compact index, **and the chronological `/archive/` list**. `data()` must **fail closed** for a missing or invalid cover on a published post; drafts can wait until publication. Do not reintroduce a generic fallback.
6. Before merging, run the site builder, validator, pytest and actual Playwright checks at 1440, 768, 390 and 360 px. Confirm all cover images load, each published post has a distinct SVG, captions match diagrams and none introduces overflow. Cover QA belongs in PR review.

*Reminder:* `Agents.md` is a discoverability alias to canonical `AGENTS.md`. Maintain these rules here, not in two divergent copies.

## Related reading contract (required for new and existing Posts)

Every published Post should offer **a small, relevant next-reading route**, not a random list or all articles in the same category. The site builder adds cards to the **bottom of the published article HTML**, without rewriting the source article. The implementation is shared:

1. **Data ownership.** `content/posts.json` supplies the authoritative title, subtitle, reading time, published status and article-specific `cover`. `content/reading_paths.json` supplies the **curated, ordered** cross-post relationships. `scripts/related_posts.py` handles selection and safe HTML generation; `site/assets/related-posts.css` scopes its styling. Do not paste 70 hand-maintained card blocks into individual `index.html` files.
2. **Update the learning graph when publishing.** For every new published article, inspect neighboring Posts and add it to **one or more meaningful reading paths** in `content/reading_paths.json`. Order a path pedagogically (prerequisite → mechanism → application) rather than chronologically; keep each path tightly scoped and do not confuse similarly named but technically different concepts (e.g. ML decision trees versus B+ tree indexes). Cross-category links are welcome when the connection is substantive.
3. **Recommendation priority.** Curated adjacent steps win; two-step neighbors can follow. A strict fallback may use the same registered `category + topic` or specific overlapping technical tags. **Category alone is insufficient**. The selector is deterministic, deduplicated, excludes self-links and returns **at most four cards**. It should return **no cards** if there is no defensible connection, rather than invent a bridge. Explain the connection with a relation label and a named learning route.
4. **Publication safety.** Recommend **only `status: published`** entries with actual article paths and valid local cover SVGs. `load_reading_paths` must reject missing, duplicate, or unpublished references. Never link drafts, placeholders, `_topics/` stubs, or external papers as if they were local Posts. For a draft, do not add it to a published path until the draft itself becomes published.
5. **Presentation.** Cards use each target Post's own `cover.src` (no shared generic artwork), `title`, `subtitle`, and `reading_minutes`. Include a visible reason (e.g. `补充基础`, `继续深入`, `同主题延伸`) and an actual, navigable destination; use a semantic `section` with a distinct heading, accessible links, and decorative thumbnail alt text. Cards must work without JavaScript, with keyboard focus, at 1440/768/390/360px, in print and under reduced-motion preference. Keep all CSS namespaced to avoid breaking the many independent article styles.
6. **Build and QA.** `python scripts/build_site.py` injects the component once per published article, inside the closing article/main. Run `python scripts/validate_site.py`, `python -m pytest -q tests/test_related_posts.py tests/test_site.py`, and browser QA; check that all card destinations and cover images resolve, that no heading/ID duplication or horizontal overflow appears, and that the build remains reproducible. The published HTML (not `posts/.../index.html`) is the correct place to inspect generated cards. Review route quality manually, not only the numeric similarity score.
7. **Release semantics.** PR CI may validate the cards but does **not** deploy them. Only a successful merge/push to `main` followed by a successful GitHub Pages deployment and reachable article URL counts as published.

## PDF export contract (every published article)

- **One PDF per published post.** On a clean build, `python scripts/build_site.py` creates the original HTML site and `python scripts/render_pdfs.py` renders each published article to `_site/posts/<category>/<slug>/article.pdf` using Chromium/Playwright. Do not commit generated PDFs or `_site/`. Draft posts never receive generated PDFs or site buttons.
- **Website layout is authoritative.** PDF output comes from the actual article HTML/CSS (including inline SVG, native MathML and original print rules), not from a second Markdown, LaTeX or Word source. Only add conservative print overrides for page sizing, navigation and pagination; never rebuild the explanation as a different template.
- **No per-article manual button edits.** The exporter injects the accessible `下载 PDF` link and `site/assets/pdf-download.css` into the *built* HTML after a valid PDF exists. The article's source `index.html` remains standalone, and the on-screen control must not change normal document flow. Hide the control in PDF/print output.
- **PDF QA matters.** Fail the build for broken images, missing PDFs, invalid output or unsearchable/empty documents. Keep CJK + mathematical fonts available in CI; inspect SVG, MathML, code wrapping, page breaks and text clipping on representative long and short posts. Interactive exercises become static snapshots in PDF; retain the interactive HTML version for experimentation.
- **Deployment.** `.github/workflows/publish.yml` must generate PDFs before link validation and Pages upload. Verify links and PDF integrity on PRs; only claim production success after a successful Pages deployment and reachable downloadable URLs.

## 8. Copyright and provenance

The teaching *method* is inspired by Christopher Olah and Harvard NLP. All article text and diagrams must be independently constructed. Cite primary papers for substantive facts; do not assume the absence of a license implies permission to redistribute images or code. Canonical Skill upstream provenance is recorded in `skills/olah-style-paper-posts/UPSTREAM.md`.

## 9. RSS and README publication contract

- `content/posts.json` is the only article publication registry. The RSS feed at `/feed.xml` is **generated**, never edited manually, and includes only `status: published` entries. Maintain `docs/rss.md` as the detailed feed specification.
- Every published entry must have truthful ISO `published` and `updated` calendar dates (`updated >= published`). Do not fabricate publication times: RSS `pubDate` serializes date-only metadata as **00:00 GMT by convention**, not as an observed moment; `dcterms:modified` preserves date precision.
- Article permalink is the **stable RSS GUID**. Preserve it when updating the article. Do not change `feed.xml`, public article slugs, or base paths casually. Include absolute item links, summaries, category/topic labels, `atom:link rel="self"`, and HTML `application/rss+xml` autodiscovery.
- Update `README.md` as a reader-first project guide, **not** an ever-growing manual mirror of the article manifest. Give representative reading routes; point complete inventories to generated pages and the manifests. Keep deployment instructions explicit about PR-only validation vs successful Pages deployment.
- Required RSS QA: `python -m pytest -q tests/test_rss.py` plus full site build/validator and, after merge, actual live feed verification. Check XML parseability, unique stable GUIDs, no drafts, date semantics, link correctness and non-duplicated article-head discovery. Never claim live feed availability from local tests alone.

## HTML layout regression contract

- Published article source must start with **one** HTML5 doctype; never append another when updating a post.
- Preserve the semantic heading ladder: one H1, H2 sections, H3 widgets/subsections, and H4 only inside an H3 subsection. Styling is controlled by classes, not heading rank.
- Every published standalone article must provide valid `@media print { ... }` and `@media (prefers-reduced-motion: reduce) { ... }`. `@media(print)` is invalid and silently drops print rules.
- Keep long equations, code and wide diagrams inside explicit keyboard-focusable scroll regions where applicable; never suppress page-level overflow with `overflow-x:hidden`. Use `min-width:0` on grid and flex children, allow long headings and references to wrap, and keep mobile illustrations readable by local scrolling when required.
- Run `python scripts/validate_site.py` and Chromium checks at 360px, 390px, tablet, desktop and print. The static layout contract in `check_article_layout` prevents duplicate doctypes, skipped heading ranks and absent print/reduced-motion coverage; actual viewport overflow requires browser QA.

## Incremental downloadable PDF contract

The published HTML downloads are **pre-rendered** during the GitHub Pages workflow, never generated on a reader's click. Keep the existing fixed, unobtrusive PDF download button and article-specific print CSS.

1. After `scripts/build_site.py`, run `scripts/render_pdfs.py`. A full build must populate `_site/posts/<category>/<slug>/article.pdf` for **every published** post, including unchanged posts restored from cache. Drafts never receive PDFs.
2. PDF cache identity must cover built article HTML (including related-reading cards), local assets referenced directly or from CSS, related-post cover assets, print styles, renderer behavior/dependencies, font environment, and public URL. Do **not** invalidate on homepage/archive-only changes, and never rely solely on `updated` metadata or Git diff paths.
3. Cache files are expendable and **untrusted**: verify matching fingerprints, PDF hashes, byte size, page counts and extractable text; if missing, corrupt, or from an incompatible renderer, regenerate rather than publishing stale/broken files. Cache manifests cannot be considered evidence of a CI pass.
4. Rendering and injecting the download control are **separate operations**. Cache hits must inject exactly one accessible download link into the *built* HTML only, preserving the source article and print layout.
5. Restore `.pdf-cache/` from GitHub Actions cache, save it **after** final site validation, and ignore it in Git. Use unique immutable run keys with a versioned restore prefix. No cache must be necessary for a correct build. On full builds prune unpublished entries; `--only` must not erase unrelated entries.
6. When modifying the PDF pipeline, run `pytest tests/test_pdf_cache.py tests/test_pdf_export.py` plus the entire repository quality gate and at least one real PDF browser export in CI. Review logs for `PDF CACHED` versus `PDF RENDERED` and verify the published PDF download URL after Pages deployment. To force a full regeneration: `python scripts/render_pdfs.py --force`.


## Paginated discovery / thumbnail performance contract

- **Build-time pagination for `/archive/`.** The canonical archive and each `/archive/page/N/` URL are distinct static pages with canonical URLs, sitemap entries, bounded article rows, and real previous/next/numbered links. `scripts/build_site.py` uses `ARCHIVE_PAGE_SIZE = 16`. Never reintroduce a single giant archive DOM or hide excess rows with CSS/JS.
- **Home index only renders 8 articles at once.** Initial HTML contains only the first `HOME_PAGE_SIZE = 8` index cards. `site/assets/site.js` obtains lightweight metadata from built `posts.json`, searches and filters the full published corpus, and replaces the 8-card DOM window when the user changes pages. Do not include every thumbnail in the HTML or pre-create hidden `<img>` elements.
- **Images only for active page.** Keep `loading="lazy"` and `decoding="async"` on compact covers. Avoid preload tags for archive/search thumbnails and avoid requesting unselected pages. Hero/spotlight images are intentionally separate editorial selections.
- **Graceful fallback.** With JavaScript disabled or a failed search-index request, the homepage still shows its first 8 article links and a normal link to the full archive. Archive pagination works with no JavaScript.
- **Verification.** Tests must assert page-size bounds, no duplicate/omitted published posts across archive pages, valid relative SVG URLs at deeper nesting, canonical/sitemap coverage, and working full-library search/filter/pager at desktop and mobile widths. Tests should not require all published article thumbnails to be present on one DOM page.
