# 模型架构 / Architectures

拆开网络的信息路径：从 AlexNet 的卷积视觉表征、ResNet 的残差学习，到 Transformer 的注意力结构。

该目录包含本分类文章。添加新 Post 时创建 `posts/architectures/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## Normalization & Residual Paths

- [Understanding Pre-LN vs Post-LN](pre-ln-vs-post-ln/index.html)：LayerNorm 位置、残差梯度、warm-up 论文证据、DeepNorm / Peri-LN。
- 本主题横跨模型结构与训练稳定性，先作为 `architectures` 的二级主题；若未来扩展为覆盖多个模型家族的独立系列，再评估增设一级分类。

RoPE 位于 `posts/architectures/rope/`，主题为 **Positional Encoding**；位置编码属于模型架构，推理缓存与部署属于推理分类的交叉议题。

## Convolutional Neural Networks & Vision

- [Understanding CNN](cnn/index.html)：以 LeNet-5 为核心，图解局部感受野、共享核、跨通道卷积、空间尺寸和梯度，并追溯原版 C3/S/RBF 机制。

- [Understanding AlexNet](alexnet/index.html)：从 ImageNet 2012 的训练范式出发，拆解卷积、ReLU、LRN、双 GPU、数据增强与 Dropout；严格区分单模型指标和七模型竞赛集成。
- [Understanding ResNet](resnet/index.html)：从网络深度的优化退化与 shortcut 切入，承接 AlexNet 到残差学习的历史发展。
- 该主题作为模型架构的二级轨道，不增设新的顶层分类；后续 VGG、Inception、EfficientNet 可依此归档。

## Gating & Multiplicative Interactions

- [Understanding Neural Gating](neural-gating/index.html)：从 LSTM/GRU 到 Highway、GLU、SwiGLU 的跨论文门控机制，区分可学习的 sigmoid 保留门与非概率的乘性 FFN 门。
- [专题规划与术语边界](_topics/gating-mechanisms/README.md)：控制信息流而非独立建一级分类；与 Attention、MoE Routing 进行方法学区分。

## Recurrent Networks / LSTM

- [Understanding LSTM](lstm/index.html)：从普通 RNN 的长期梯度问题到 1997 CEC / 输入与输出门；明确区分 2000 年遗忘门、2002 年 peephole 和现代四门实现。
- 本主题为 `Architectures` 内的二级研究方向，可继续容纳 Vanilla RNN、GRU、双向 LSTM 与序列状态模型；暂不新建顶层类别。

## Sequence-to-Sequence / Encoder–Decoder

- [Understanding Seq2Seq](seq2seq/index.html)：2014 年 LSTM Encoder–Decoder、Teacher Forcing、自回归解码、反转源序列与 Attention 解决固定向量瓶颈的后续发展。
- 属于模型架构的二级主题，后续 RNN、LSTM、Bahdanau Attention、Luong Attention 与 Transformer Encoder–Decoder 可沿此线索组织；无需新建一级分类。

## Attention Head Sharing

- [Understanding GQA](gqa/index.html)：以 EMNLP 2023 原论文为主线，解释 MHA / GQA / MQA 头共享、Checkpoint mean-pooling + uptraining、KV Cache 成本与 T5-XXL 结果；提供交互演算、原生 MathML、独立 SVG、数值测试与证据账本。
- 研究主题属于注意力架构；KV Cache 的内存分配、页表和在线调度延伸至 `inference`，无需新建顶层分类。

## Graph Neural Networks & Message Passing

- [Understanding GNN](gnn/index.html)：从节点/边/邻接矩阵进入消息传递；通过四节点手算、GCN 对称归一化、两跳交互和原始论文证据，理解 GCN、GraphSAGE 与 GAT 的区别。
- [专题归属](_topics/graph-neural-networks/README.md)：作为 `architectures` 下的独立二级主题，图数据上的节点/边/图任务均可延伸到这里，不与规则网格 CNN 或全序列 Transformer Attention 混同。

## 专题规划占位（非文章）

`architectures` 研究模型信息流与结构算法：MoE、State Space Models、Efficient Attention、Long-context。FlashAttention 等特定 GPU kernel 优化应与 `systems` 双向链接而不重复归档。

- [Mixture of Experts (MoE)](_topics/moe/README.md)
- [State Space Models](_topics/state-space-models/README.md)
- [Efficient Attention](_topics/efficient-attention/README.md)
- [Long-context Architectures](_topics/long-context-architectures/README.md)

上述 `_topics/` 是研究路线占位目录，正式文章仍遵循 `posts/architectures/<slug>/index.html`；只有 `content/posts.json` 中的 `published` 文章才会被发布。

## Mixture of Experts (MoE)

- [Understanding Mixture of Experts (MoE)](moe/index.html)：精读 ICLR 2017 的 LSTM+稀疏专家结构，拆解 Noisy Top-K、Importance/Load、容量约束与 Expert Parallelism；区分 GShard、Switch、Mixtral 与 DeepSeekMoE。
- 复用现有 `Mixture of Experts (MoE)` 二级专题和 [`_topics/moe` 研究规划](_topics/moe/README.md)，不增设重复分类。

## Efficient Attention — DeltaNet

- [Understanding DeltaNet](deltanet/index.html)：精读 Yang et al. NeurIPS 2024，解释 Delta Rule 纠错式关联记忆、单位 Key 下的覆写、WY/Chunkwise 并行与论文对照实验；提供四幅独立 SVG、可交互 β 演示和标准库测试。
- DeltaNet 是高效注意力与线性 RNN 的交叉模型，复用已有 `Efficient Attention` / `State Space Models` 二级轨道，不新增一级分类；[Gated DeltaNet (2025)](https://arxiv.org/abs/2412.06464) 作为独立后续工作，不能混用实验结果。


## Efficient & Mobile CNNs

- [Understanding MobileNet](mobilenet/index.html)：从深度可分离卷积、α/ρ 与 V1 原论文实验到 V2/V3/V4 演进；后续接纳 ShuffleNet、MnasNet、EfficientNet，不设重复一级分类。


## Gating & Multiplicative Interactions — SwiGLU

- [Understanding SwiGLU](swiglu/index.html)：Shazeer 2020 的三投影 FFN、SiLU 门控、GEGLU/ReGLU 对照、T5 证据与现代 PaLM/LLaMA。
- 与 [Understanding Neural Gating](neural-gating/index.html) 共享现有 `gating-mechanisms` 二级主题，不重复增设一级分类。

分类占位统一沿用 `content/categories.json` 中的稳定 slug：MobileNet 使用 `_topics/efficient-mobile-cnn/`，Neural Gating 与 SwiGLU 统一使用 `_topics/gating-mechanisms/`。

## Generative Adversarial Networks (GAN)

- [Understanding GAN](gan/index.html)：精读 Goodfellow et al. NeurIPS 2014，拆解生成器与判别器、minimax、最优 D*、Jensen–Shannon 散度与 non-saturating loss；四幅原创 SVG、三类别互动分布实验、数值测试和原论文证据。
- 将 GAN 放在模型架构一级分类下新增 `generative-adversarial-networks` 稳定二级主题；它是一个生成建模训练框架，不等于 DCGAN、WGAN 等后续变体。其二分类判别训练和概率建模分别关联 Logistic Regression 与 GMM。
