# Understanding Word2Vec — Olah-style paper post

一篇开箱即读的中文双论文交互式精读文章：从自监督窗口、CBOW / Skip-gram、embedding lookup 到 Negative Sampling、梯度和 NumPy 代码。

## 预览

直接双击 `index.html`。网页 **100% 离线**、无需服务器/CDN/构建系统；所有布局、SVG 和演示脚本均内联在 HTML 中。

也可运行：

```bash
python -m http.server 8000
# 访问 http://localhost:8000/
```

## 代码实验

```bash
python -m pip install numpy
python code/train_sgns.py --epochs 30 --negative 3 --window 2 --seed 7
python -m unittest discover -s tests -v
```

默认 tiny corpus 仅用于验证算法与损失下降方向，不是原论文规模复现，不能据此衡量真实语义质量。`train_sgns.py` 实现的是最小 SGNS；不含原 C 实现的高频词子采样、Huffman 层次 Softmax、多线程/Hogwild、以及短语发现。示例使用稳定的 NumPy logaddexp 与固定随机种子。

## 文件结构

- `index.html`：单文件离线文章，含自绘 inline SVG 与 3 组交互演示。
- `assets/architecture.svg`：架构 SVG 的独立版，便于后期维护和重新排版。
- `assets/negative-sampling.svg`：SGNS 正负路径的独立版。
- `code/train_sgns.py`：可运行的教学 SGNS 训练器。
- `tests/test_sgns.py`：损失与梯度检查、smoke test。
- `references/reading-notes.md`：论文对应章节、限定说明与研究证据链。

## 原创性与引用

HTML、所有图解与 JavaScript 是为本示例重新编写；Christopher Olah / The Annotated Transformer 只作为叙事形式参考，不复制受版权保护的原图与正文。文章中的数值演示与几何图均明确标为人工构造。引用来源和来源区分见 `references/reading-notes.md`。

## GitHub Pages

作为静态站点，可直接把 `index.html` 与同级目录放在任意 Pages 发布目录。站点若已有导航与 CSS 系统，可把文章作为独立 post 入口，不需要 JS bundler。

## 在 xm-posts 中的路径

- 分类：`foundations`，具体主题标签为 `Word Embeddings`。
- 页面地址：`https://1998x-stack.github.io/xm-posts/posts/foundations/understanding-word2vec/`。
- 发布索引单一数据源：`content/posts.json`；不要以本目录 `post.json` 替代站点索引。
- `assets/` 中的 SVG 同时提供本文 5 张 inline 图的可独立编辑版本。
