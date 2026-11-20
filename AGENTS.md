# AGENTS.md — xm-posts repository instructions

Applies to **all agent-authored changes in this repository** (including Claude, Pi, Codex / generic agents, and OpenCode). In case of conflict, **scientific truth, user intent, and repository tests** outrank visual preference. This file is the repo-level contract; detailed paper-explainer workflows live in [`skills/olah-style-paper-posts/SKILL.md`](skills/olah-style-paper-posts/SKILL.md).

## 1. Mission and deliverable

Create evidence-grounded, pedagogically progressive, illustrated technical articles on neural networks, LLMs and systems. An accepted Post has semantic offline-capable HTML, editable standalone SVGs, a claims/evidence ledger, relevant runnable examples, and browser QA proof. Never trade correctness for novelty, beauty or word count.

## 2. Know your boundaries

- **Source of truth** for categories: `content/categories.json`; for post publication, cards, RSS and sitemap: `content/posts.json`.
- **Source of truth** for article HTML and assets: `posts/<category>/<slug>/index.html`, `assets/*.svg`, `evidence.json`; optional minimal code lives beside the article.
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
6. **QA.** Run source validator, site builder, link checker, tests and actual Playwright at 1440/768/390/360px. Test a real interaction, inspect errors/overflow and ensure keyboard use. Do not call skipped checks 'passed'.
7. **Release.** Publish a branch/PR, review diff & CI; only then merge and verify `main`, Pages run and reachable URLs. Do not assert production deployment merely because a workflow exists.

Read the full process in `skills/olah-style-paper-posts/references/{paper-extraction,narrative-architecture,evidence-and-citation,html-design-system,svg-production,implementation-and-interactivity,browser-qa,publishing}.md`.

## 4. Make a new Post

```bash
python scripts/new_post.py inference understanding-kv-cache \
  --title 'Understanding KV Cache' \
  --subtitle '为什么缓存可以改善自回归推理？' \
  --paper 'https://arxiv.org/...'
```

This creates **draft** metadata. Replace the template with an actual, referenced explanation; create independent SVGs and evidence; run required QA; update `reading_minutes`, `summary`, `tags`, `published` and finally `status` from `draft` to `published`. Never change state solely because a file exists. Never create fake placeholder posts in `content/posts.json` with `status: published`.

For new categories, add an entry to `content/categories.json` and a `posts/<category>/README.md` placeholder. Do not hand-edit the generated site indexes or hardcode new post cards.

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
- No bypassing CI, weakening `status: published` gate, replacing an existing scientific explanation with a glossy placeholder, or duplicating an agent skill fork with divergent instructions.

## 7. PR hand-off checklist

- [ ] Primary sources and numerical evidence checked, original vs modern variants separated.
- [ ] `index.html` accurate with 1 H1, correct semantic structure and navigable sections.
- [ ] SVGs tested alone and embedded; no cross-document duplicate IDs.
- [ ] Relevant code examples have deterministic asserts; limits documented.
- [ ] `content/posts.json` accurate; drafts excluded.
- [ ] Build and link validation pass, genuine browser interaction verified.
- [ ] Four skill mirrors match canonical; README and docs match paths and deployment.
- [ ] CI passes; production claims only after actual deployed site verified.

## 8. Copyright and provenance

The teaching *method* is inspired by Christopher Olah and Harvard NLP. All article text and diagrams must be independently constructed. Cite primary papers for substantive facts; do not assume the absence of a license implies permission to redistribute images or code. Canonical Skill upstream provenance is recorded in `skills/olah-style-paper-posts/UPSTREAM.md`.
