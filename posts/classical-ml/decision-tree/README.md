# Understanding Decision Tree — article source and QA

This explainer uses three **distinct** historical lines: Breiman et al. (1984) CART,
Quinlan (1986) ID3, and Quinlan (1993) C4.5, with a later 1996 refinement.
It does not pretend they are a single algorithm or that the examples reproduce
a historical benchmark. Its algebra and experiments are independent teaching
examples, not extracted accuracy numbers.

## Files

- `index.html`: 13-section Chinese explainer; 8 native offline MathML formulas;
  accessible threshold selection demo, no external CSS, JS, font or trackers.
- `assets/01-rule-path.svg` through `06-prune.svg`: six semantic standalone
  original diagrams, embedded inline in the HTML with stable unique IDs.
- `evidence.json`: 10 evidence claims, with historical vs modern vs derived scope.
- `mini_decision_tree.py`: deterministic one-dimensional classification stump,
  regression stump, and a simplified pruning-cost comparison, standard library only.
- `tests/test_decision_tree.py`: label entropy, Gini, threshold, SSE,
  ordering invariance, alpha equality and validation failure tests.

## Reproduce

```bash
python posts/classical-ml/decision-tree/mini_decision_tree.py
python -m pytest tests/test_decision_tree.py -q
python skills/olah-style-paper-posts/scripts/validate.py posts/classical-ml/decision-tree/index.html
python skills/olah-style-paper-posts/scripts/browser_check.py posts/classical-ml/decision-tree/index.html --output reports/decision-tree
python scripts/build_site.py
python scripts/validate_site.py
python -m pytest -q
```

Inspect real Chromium at 1440, 768, 390, 360 px, interaction, screenshot,
MathML numerator/denominator geometry, print and offline requests before releasing.
The page has no invented accuracy or benchmark claims.

## Taxonomy

The existing `classical-ml → Trees & Ensembles` track already covers this
paper. No new top-level category is needed. Later random forest and boosting
studies can join this track without restructuring the site.
