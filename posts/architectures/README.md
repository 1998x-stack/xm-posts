# 模型架构 / Architectures

拆开网络的信息路径：从 AlexNet 的卷积视觉表征、ResNet 的残差学习，到 Transformer 的注意力结构。

该目录包含本分类文章。添加新 Post 时创建 `posts/architectures/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## Normalization & Residual Paths

- [Understanding Pre-LN vs Post-LN](pre-ln-vs-post-ln/index.html)：LayerNorm 位置、残差梯度、warm-up 论文证据、DeepNorm / Peri-LN。
- 本主题横跨模型结构与训练稳定性，先作为 `architectures` 的二级主题；若未来扩展为覆盖多个模型家族的独立系列，再评估增设一级分类。

RoPE 位于 `posts/architectures/rope/`，主题为 **Positional Encoding**；位置编码属于模型架构，推理缓存与部署属于推理分类的交叉议题。

## Convolutional Neural Networks & Vision

- [Understanding AlexNet](alexnet/index.html)：从 ImageNet 2012 的训练范式出发，拆解卷积、ReLU、LRN、双 GPU、数据增强与 Dropout；严格区分单模型指标和七模型竞赛集成。
- [Understanding ResNet](resnet/index.html)：从网络深度的优化退化与 shortcut 切入，承接 AlexNet 到残差学习的历史发展。
- 该主题作为模型架构的二级轨道，不增设新的顶层分类；后续 VGG、Inception、EfficientNet 可依此归档。

## Recurrent Networks / LSTM

- [Understanding LSTM](lstm/index.html)：从普通 RNN 的长期梯度问题到 1997 CEC / 输入与输出门；明确区分 2000 年遗忘门、2002 年 peephole 和现代四门实现。
- 本主题为 `Architectures` 内的二级研究方向，可继续容纳 Vanilla RNN、GRU、双向 LSTM 与序列状态模型；暂不新建顶层类别。

## Sequence-to-Sequence / Encoder–Decoder

- [Understanding Seq2Seq](seq2seq/index.html)：2014 年 LSTM Encoder–Decoder、Teacher Forcing、自回归解码、反转源序列与 Attention 解决固定向量瓶颈的后续发展。
- 属于模型架构的二级主题，后续 RNN、LSTM、Bahdanau Attention、Luong Attention 与 Transformer Encoder–Decoder 可沿此线索组织；无需新建一级分类。
