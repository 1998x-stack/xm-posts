# Contributing to xm-posts

Thank you for improving scientific explanations. Prioritize an issue demonstrating a concrete reader misunderstanding, scientific correction, broken interaction, or missing reproduction step.

1. Read [AGENTS.md](AGENTS.md) and the [Skill](skills/olah-style-paper-posts/SKILL.md).
2. Fork/branch from `main`; keep each PR focused on one article, one scientific correction, or one infrastructure change.
3. For a new article, scaffold it with `scripts/new_post.py`; keep status `draft` until paper evidence, stand-alone SVGs and browser QA pass.
4. Make sources explicit, attribute third-party material, and do not use third-party illustration assets without verified licensing rights.
5. Run `scripts/build_site.py`, `scripts/validate_site.py`, `scripts/sync_skills.py --check`, `pytest`, and the relevant Chromium interaction check.
6. In the PR explain motivation, evidence, source sections, diagram changes, commands executed, screenshots (if layout changed), and deployment consequences.
7. After merge, verify the deploy workflow and actual rendered site. CI PR builds never deploy.

Do not add a misleading `published` entry for placeholder articles. The absence of a repository-wide license is not a blanket permission to reuse upstream text or art.
