# Understanding LogSumExp & Softmax Taylor Expansion

依据 [科学空间 2026-07-13 原文](https://spaces.ac.cn/archives/11814) 和 [Kuzina et al., arXiv:2607.07706](https://arxiv.org/abs/2607.07706) 的问题背景，重新组织的独立技术解读。

- `index.html`：13 节渐进文章，原生 MathML、5 幅内联 SVG、交互数值实验。
- `assets/*.svg`：5 幅可独立使用的语义 SVG，与内联图内容一致。
- `evidence.json`：每条研究背景、数学推导与教学示例的证据、状态和边界。
- `mini_softmax_taylor.py`：纯 Python 标准库实现，执行 `python posts/foundations/logsumexp-softmax-taylor/mini_softmax_taylor.py`。
- `tests/test_logsumexp_softmax_taylor.py`：稳定性、概率归一化、阶数误差与状态重排的确定性检查。

注意：科学空间正文对自动抓取返回 403；原文标题和引言通过站点公开索引核对，进一步数学式通过独立推导与代码核验，不能称为逐行原文复刻。图与示例都是教学构造。
