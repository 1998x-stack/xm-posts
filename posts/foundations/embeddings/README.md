# Understanding Embeddings — source and verification notes

This is a multi-paper mechanism study, not a benchmark reproduction.

## Primary sources

- Mikolov et al., 2013, [CBOW and Skip-gram](https://arxiv.org/abs/1301.3781).
- Mikolov et al., 2013, [Negative Sampling](https://arxiv.org/abs/1310.4546).
- Pennington et al., 2014, [GloVe](https://aclanthology.org/D14-1162/).
- Devlin et al., 2019, [BERT](https://aclanthology.org/N19-1423/).
- Reimers and Gurevych, 2019, [SBERT](https://aclanthology.org/D19-1410/).
- Gao et al., 2021, [SimCSE](https://aclanthology.org/2021.emnlp-main.552/).
- Wang et al., 2022, [E5](https://arxiv.org/abs/2212.03533).

## Reproduce mathematical assertions

`python posts/foundations/embeddings/mini_embedding.py` and `python -m pytest -q tests/test_embeddings.py`.

## Required publication gates

- Build, source and link checks in `scripts/build_site.py` and `scripts/validate_site.py`.
- `scripts/browser_check_all.py` at 1440, 768, 390 and 360 CSS px, with offline requests blocked, SVG and MathML checks, keyboard interaction and print.
- PR CI success, merge to main and successful Pages deployment.
- Do not count unexecuted checks as passes.

All SVG coordinates are instructional, not measured model embeddings. The deterministic Python example does not train a model or reproduce published benchmark metrics.
