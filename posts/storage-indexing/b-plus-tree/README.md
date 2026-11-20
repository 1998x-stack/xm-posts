# Understanding B+ Tree

- 正文：[index.html](index.html)
- 六幅独立 SVG：`assets/01-page-layout.svg` 至 `assets/06-page-cost.svg`
- 证据台账：[evidence.json](evidence.json)
- 教学代码：[mini_b_plus_tree.py](mini_b_plus_tree.py)

教学设定：内部节点最多 4 孩子，叶子最多 3 项；唯一整数键；父级 separator 是右子树最小键。代码覆盖 insert/find/range；删除重平衡仅在正文讲解，非代码功能。

验证命令：`python posts/storage-indexing/b-plus-tree/mini_b_plus_tree.py`、`python -m pytest -q tests/test_b_plus_tree.py`、`python scripts/build_site.py`、`python scripts/validate_site.py`，以及完整 Playwright 浏览器检查。
