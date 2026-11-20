# 基础理论 / Foundations

从优化器、正则化、词嵌入、表示学习和数学直觉出发，建立理解现代模型的共同语言。

该目录包含本分类文章。添加新 Post 时创建 `posts/foundations/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 已发布文章

- [Understanding Word2Vec](understanding-word2vec/index.html)：从自监督词窗到 CBOW / Skip-gram、Negative Sampling 和词向量几何。配套 `assets/`、`evidence.json`、`code/train_sgns.py` 与测试。

- [Understanding AdamW](adamw/index.html)：解耦权重衰减，从 SGD 中的等价性到 Adam 的逐坐标更新。配套六幅 SVG、`mini_adamw.py` 与原论文证据。

本类别中优化器、正则化与表示学习以文章标签和专题结构细分，不为单篇论文新增顶级分类。

- [Understanding Adam](adam/index.html)：一阶/二阶矩、偏差修正、AdamW 与 AMSGrad；含交互演示与纯 Python 更新核。

- [Understanding SGD](sgd/index.html)：从全量 GD 到 Mini-batch、无偏梯度、学习率衰减与计算统计权衡；包含 SVG 与测试。

- [Understanding SVD](svd/index.html)：矩阵分解、Eckart–Young 低秩定理、PCA 与伪逆；含交互秩选择、MathML 与 NumPy 断言。

- [Understanding Embeddings](embeddings/index.html)：覆盖 lookup、Word2Vec/GloVe、BERT、SBERT、SimCSE/E5、cosine 与 ANN/RAG 召回；附七幅图示、MathML、交互实验、证据与 Python 断言。所属二级主题：`Representation Learning & Embeddings`。

- [Understanding BPE](bpe/index.html)：带词频的贪心子词合并、原论文实验与 byte-level 变体；含六幅机制图、交互分词实验、MathML 与纯 Python 验证。

- [Understanding Importance Sampling](importance-sampling/index.html)：稀有事件、换测度、方差缩减、SNIS、ESS 与离策略评价。
