## Goal and reader question

What misconception / paper section / infra issue does this PR address?

## Scientific sources and changes

- Primary paper(s), DOI / arXiv, relevant sections/tables:
- Equations and tensor shapes checked:
- Original / later variants kept separate:

## Article and SVG checklist

- [ ] Claims evidence ledger updated
- [ ] SVGs have accessible labels and unique IDs across inline HTML
- [ ] Article contains no production/tooling footer chatter
- [ ] Relevant executable code and deterministic shape/mask tests

## Tests

- [ ] `python scripts/sync_skills.py --check`
- [ ] `python scripts/build_site.py`
- [ ] `python scripts/validate_site.py`
- [ ] `python -m pytest -q`
- [ ] Playwright browser QA for affected articles at 1440 / 768 / 390 / 360

## Publication

- [ ] Article status is `draft` until editorial QA is complete
- [ ] If published, date, summary, tags, reading minutes and paper URL are accurate
- [ ] CI passes and no draft/tooling content leaks to the Pages build
