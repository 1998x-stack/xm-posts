# 模型架构 / Architectures

拆开网络的信息路径：从 ResNet 的残差学习到 Transformer 的注意力结构。

该目录包含本分类文章。添加新 Post 时创建 `posts/architectures/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## Normalization & Residual Paths

- [Understanding Pre-LN vs Post-LN](pre-ln-vs-post-ln/index.html)：LayerNorm 位置、残差梯度、warm-up 论文证据、DeepNorm / Peri-LN。
- 本主题横跨模型结构与训练稳定性，先作为 `architectures` 的二级主题；若未来扩展为覆盖多个模型家族的独立系列，再评估增设一级分类。

RoPE 位于 `posts/architectures/rope/`，主题为 **Positional Encoding**；位置编码属于模型架构，推理缓存与部署属于推理分类的交叉议题。

## Sequence-to-Sequence / Encoder–Decoder

- [Understanding Seq2Seq](seq2seq/index.html)：2014 年 LSTM Encoder–Decoder、Teacher Forcing、自回归解码、反转源序列与 Attention 解决固定向量瓶颈的后续发展。
- 属于模型架构的二级主题，后续 RNN、LSTM、Bahdanau Attention、Luong Attention 与 Transformer Encoder–Decoder 可沿此线索组织；无需新建一级分类。
