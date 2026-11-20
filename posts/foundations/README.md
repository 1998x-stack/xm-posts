# 基础理论 / Foundations

从优化器、正则化、表示学习和数学直觉出发，建立理解现代模型的共同语言。

该目录包含本分类文章。添加新 Post 时创建 `posts/foundations/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 优化器与正则化

- [Understanding AdamW](adamw/index.html) — 解耦权重衰减：从 SGD 中的等价性到 Adam 的逐坐标更新。对应 [ICLR 2019 原论文](https://arxiv.org/abs/1711.05101)。

后续 Adam、SGD/SGDW、RMSProp、学习率调度与正则化比较保持在此类别，使用文章标签与主题索引形成可扩展专题；不为单篇文章增加顶级目录。
