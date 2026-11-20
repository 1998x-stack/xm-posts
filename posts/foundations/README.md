# 基础理论 / Foundations

从优化算法与优化器、词嵌入、表示学习和数学直觉出发，建立理解现代模型的共同语言。

该目录包含本分类文章。添加新 Post 时创建 `posts/foundations/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 已发布文章

- [Understanding Word2Vec](understanding-word2vec/index.html)：从自监督词窗到 CBOW / Skip-gram、Negative Sampling 和词向量几何。配套 `assets/`、`evidence.json`、`code/train_sgns.py` 与测试。

- [Understanding Adam](adam/index.html)：一阶/二阶矩、偏差修正、AdamW 与 AMSGrad；含交互演示与纯 Python 更新核。
