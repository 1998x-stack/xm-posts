# xm-posts

**深度学习论文的图解实验室。** 从读者真正遇到的困惑出发，用原创机制图、可核验的公式、论文证据和可运行的最小代码，拆解经典架构与 LLM 系统技术。

[![Build & Pages](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml/badge.svg)](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml) · [网站](https://1998x-stack.github.io/xm-posts/) · [文章归档](https://1998x-stack.github.io/xm-posts/archive/) · [RSS](https://1998x-stack.github.io/xm-posts/feed.xml) · [源 Skill](https://github.com/1998x-stack/Olah-style-posts)

> 发布源：`main` → GitHub Actions 校验与构建 → `_site/` artifact → GitHub Pages。公开网址需要仓库 Pages 功能首次启用且工作流成功；见 [启用说明](#github-pages-与持续部署)。

## 已发布的长文

| Post | 解释的问题 | 文章源码 | 核心资料 |
|---|---|---|---|
| **Understanding SentencePiece** | 原始文字如何编码为子词 ID？BPE、Unigram、归一化与解码边界 | [`posts/foundations/sentencepiece/`](posts/foundations/sentencepiece/index.html) | [Kudo & Richardson (EMNLP 2018)](https://aclanthology.org/D18-2012/) |
| **Understanding GAE** | 一步 TD 与全轨迹回报之间，如何权衡偏差与方差？ | [`posts/reinforcement-learning/gae/`](posts/reinforcement-learning/gae/index.html) | [Schulman et al. (ICLR 2016)](https://arxiv.org/abs/1506.02438) |
| **Understanding AlphaGo** | 为什么策略网络与价值网络能引导树搜索，避免只靠遍历下围棋？ | [`posts/reinforcement-learning/alphago/`](posts/reinforcement-learning/alphago/index.html) | [Silver et al. (Nature 2016)](https://doi.org/10.1038/nature16961) |
| **Understanding The Pile** | 为什么 22 种语料混合能增强跨领域文本建模？ | [`posts/datasets/the-pile/`](posts/datasets/the-pile/index.html) | [Gao et al. (2020)](https://arxiv.org/abs/2101.00027) |
| **Understanding Chinchilla** | 在固定训练 FLOPs 下，参数量与训练 tokens 如何均衡？ | [`posts/training/chinchilla/`](posts/training/chinchilla/index.html) | [Hoffmann et al. (NeurIPS 2022)](https://arxiv.org/abs/2203.15556) |
| **Understanding FineWeb** | 跨快照去重越强，为什么训练效果反而可能更差？ | [`posts/datasets/fineweb/`](posts/datasets/fineweb/index.html) | [Penedo et al. (NeurIPS 2024)](https://arxiv.org/abs/2406.17557) |
| **Understanding Multi-Head Attention** | 为什么多个 Q/K/V 投影比单个注意力汇总更有表达空间？ | [`posts/architectures/multi-head-attention/`](posts/architectures/multi-head-attention/index.html) | [Vaswani et al. (NeurIPS 2017)](https://arxiv.org/abs/1706.03762) |
| **Understanding GQA** | 为什么共享 KV Head 能降低 Decode 带宽又保留 Query 多头？ | [`posts/architectures/gqa/`](posts/architectures/gqa/index.html) | [Ainslie et al. (EMNLP 2023)](https://aclanthology.org/2023.emnlp-main.298/) |
| **Understanding FlashAttention** | Attention 的 FLOPs 没变，为什么 GPU 仍能提速？ | [`posts/systems/flashattention/`](posts/systems/flashattention/index.html) | [Dao et al. (2022)](https://arxiv.org/abs/2205.14135) |
| **Understanding AlexNet** | 为什么深层 CNN 能在 2012 ImageNet 上突破？卷积、ReLU、双 GPU 与真实集成指标 | [`posts/architectures/alexnet/`](posts/architectures/alexnet/index.html) | [Krizhevsky et al. (NeurIPS 2012)](https://papers.nips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf) |
| **Understanding ResNet** | 网络越深，为什么训练反而可能更难？ | [`posts/architectures/resnet/`](posts/architectures/resnet/index.html) | [He et al.](https://arxiv.org/abs/1512.03385) |
| **Understanding RNN** | 为什么新输入还能携带历史状态，长期依赖又为何难学？ | [`posts/architectures/rnn/`](posts/architectures/rnn/index.html) | [Elman (1990)](https://doi.org/10.1207/S15516709COG1402_1) |
| **Understanding LSTM** | 为什么一千步前的线索仍可能影响当前输出？ | [`posts/architectures/lstm/`](posts/architectures/lstm/index.html) | [Hochreiter & Schmidhuber (1997)](https://doi.org/10.1162/neco.1997.9.8.1735) |
| **Understanding RoPE** | 为什么旋转 Q/K 就能编码相对位置？ | [`posts/architectures/rope/`](posts/architectures/rope/index.html) | [Su et al., RoFormer](https://arxiv.org/abs/2104.09864) |
| **Understanding Seq2Seq** | 从变长输入到变长输出：为什么需要 Encoder–Decoder？ | [`posts/architectures/seq2seq/`](posts/architectures/seq2seq/index.html) | [Sutskever et al. (2014)](https://arxiv.org/abs/1409.3215) |
| **Understanding Transformer** | 为什么用 Self-Attention 替代循环结构？ | [`posts/architectures/transformer/`](posts/architectures/transformer/index.html) | [Vaswani et al.](https://arxiv.org/abs/1706.03762) |
| **Understanding Pre-LN vs Post-LN** | LayerNorm 改动为何影响残差梯度与 warm-up？ | [`posts/architectures/pre-ln-vs-post-ln/`](posts/architectures/pre-ln-vs-post-ln/index.html) | [Xiong et al. (ICML 2020)](https://proceedings.mlr.press/v119/xiong20b.html) |
| **Understanding DPO** | 为什么偏好对可以直接训练策略而无需显式奖励模型？ | [`posts/training/dpo/`](posts/training/dpo/index.html) | [Rafailov et al. (NeurIPS 2023)](https://arxiv.org/abs/2305.18290) |
| **Understanding Linear Regression** | 为什么最小平方残差意味着正交投影？闭式解、梯度下降和统计推断需要哪些边界？ | [`posts/classical-ml/linear-regression/`](posts/classical-ml/linear-regression/index.html) | [NIST: Least Squares](https://www.itl.nist.gov/div898/handbook/pmd/section1/pmd141.htm) · [Berkeley: Gauss–Markov](https://eml.berkeley.edu/sst/regression.html) |
| **Understanding Naive Bayes** | 条件独立怎么帮助分类？多项式、伯努利、平滑与校准有什么本质区别？ | [`posts/classical-ml/naive-bayes/`](posts/classical-ml/naive-bayes/index.html) | [McCallum & Nigam (1998)](https://www.cse.iitb.ac.in/~soumen/readings/papers/McCallumN1998event.pdf) |
| **Understanding Decision Tree** | 为什么一连串简单判断能成为分类与回归模型？从 ID3、CART 与 C4.5 到剪枝 | [`posts/classical-ml/decision-tree/`](posts/classical-ml/decision-tree/index.html) | [Quinlan (1986)](https://doi.org/10.1007/BF00116251) · [Breiman et al. (1984)](https://www.routledge.com/Classification-and-Regression-Trees/Breiman-Friedman-Stone-Olshen/p/book/9780412048418) |
| **Understanding SVM** | 为什么分对了仍需最大间隔？ | [`posts/classical-ml/svm/`](posts/classical-ml/svm/index.html) | [Cortes & Vapnik (1995)](https://doi.org/10.1007/BF00994018) |
| **Understanding XGBoost** | 为什么提升树可以二阶优化并扩展到海量稀疏数据？ | [`posts/classical-ml/xgboost/`](posts/classical-ml/xgboost/index.html) | [Chen & Guestrin (KDD 2016)](https://arxiv.org/abs/1603.02754) |
| **Understanding PCA** | 最大方差为何等价于最小平方重建误差？ | [`posts/classical-ml/pca/`](posts/classical-ml/pca/index.html) | [Pearson (1901)](https://doi.org/10.1080/14786440109462720) · [Hotelling (1933)](https://www.scienceopen.com/document?vid=a0c9b352-1645-4706-9d7c-a76e6534a1b5) |
| **Understanding Chain-of-Thought Prompting** | Few-shot 的中间推理步骤如何改变复杂任务表现？ | [`posts/reasoning/chain-of-thought/`](posts/reasoning/chain-of-thought/index.html) | [Wei et al. (NeurIPS 2022)](https://arxiv.org/abs/2201.11903) |
| **Understanding Self-Consistency** | 多路径采样与最终答案投票为何有效？ | [`posts/reasoning/self-consistency/`](posts/reasoning/self-consistency/index.html) | [Wang et al. (2022; ICLR 2023)](https://arxiv.org/abs/2203.11171) |
| **Understanding MCTS** | 为什么不用搜完整棵树，也能优先探索有价值的决策？UCT、Monte Carlo Rollout 与 PUCT | [`posts/reinforcement-learning/mcts/`](posts/reinforcement-learning/mcts/index.html) | [Kocsis & Szepesvári (ECML 2006)](https://aima.cs.berkeley.edu/~russell/classes/cs294/s11/readings/Kocsis%2BSzepesvari%3A2006.pdf) |
| **Understanding A3C** | 异步并行 Actor–Critic 如何用 n-step Advantage 与熵正则替代 Replay？ | [`posts/reinforcement-learning/a3c/`](posts/reinforcement-learning/a3c/index.html) | [Mnih et al. (ICML 2016)](https://proceedings.mlr.press/v48/mniha16.html) |
| **Understanding DQN** | 为什么像素与奖励足以驱动动作价值学习？ | [`posts/reinforcement-learning/dqn/`](posts/reinforcement-learning/dqn/index.html) | [Mnih et al. (Nature 2015)](https://doi.org/10.1038/nature14236) |
| **Understanding NoisyNet** | 为什么可学习的参数噪声能带来更连贯的探索？ | [`posts/reinforcement-learning/noisynet/`](posts/reinforcement-learning/noisynet/index.html) | [Fortunato et al. (ICLR 2018)](https://arxiv.org/abs/1706.10295) |
| **Understanding REINFORCE** | 为什么无法对环境求导，也能从随机行动与奖励中估计策略梯度？ | [`posts/reinforcement-learning/reinforce/`](posts/reinforcement-learning/reinforce/index.html) | [Williams (Machine Learning 1992)](https://doi.org/10.1007/BF00992696) |
| **Understanding PPO** | 为什么能复用同一批轨迹又避免过大更新？ | [`posts/reinforcement-learning/ppo/`](posts/reinforcement-learning/ppo/index.html) | [Schulman et al. (2017)](https://arxiv.org/abs/1707.06347) |
| **Understanding SAC** | 为什么旧经验可复用，还要用最大熵保留探索？ | [`posts/reinforcement-learning/sac/`](posts/reinforcement-learning/sac/index.html) | [Haarnoja et al. (ICML 2018)](https://proceedings.mlr.press/v80/haarnoja18b.html) |
| **Understanding RLHF** | 为什么示范微调还需要人类偏好与策略优化？ | [`posts/training/rlhf/`](posts/training/rlhf/index.html) | [Ouyang et al. (2022)](https://arxiv.org/abs/2203.02155) |
| **Understanding GRPO** | 为什么不需要 Critic 也能构造策略优势？ | [`posts/training/grpo/`](posts/training/grpo/index.html) | [Shao et al. (2024)](https://arxiv.org/abs/2402.03300) |
| **Understanding WordPiece** | 为什么 BERT MaxMatch 与训练词表不是一个算法？ | [`posts/foundations/wordpiece/`](posts/foundations/wordpiece/index.html) | [Schuster & Nakajima (2012)](https://research.google/pubs/japanese-and-korean-voice-search/) · [BERT tokenizer](https://github.com/google-research/bert/blob/master/tokenization.py) |
| **Understanding Word2Vec** | 为什么上下文预测能产生词向量？ | [`posts/foundations/understanding-word2vec/`](posts/foundations/understanding-word2vec/index.html) | [Mikolov et al. (2013)](https://arxiv.org/abs/1301.3781) · [NeurIPS 2013](https://arxiv.org/abs/1310.4546) |
| **Understanding Embeddings** | 为什么词的编号能够变成可比较的语义向量？从 Word2Vec 到对比检索 | [`posts/foundations/embeddings/`](posts/foundations/embeddings/index.html) | [Word2Vec](https://arxiv.org/abs/1301.3781) · [SBERT](https://aclanthology.org/D19-1410/) · [SimCSE](https://aclanthology.org/2021.emnlp-main.552/) |
| **Understanding Importance Sampling** | 为什么故意改变抽样分布，仍可无偏估计目标概率？稀有事件、SNIS、ESS 与 Off-policy | [`posts/foundations/importance-sampling/`](posts/foundations/importance-sampling/index.html) | [Kahn & Marshall (1953)](https://doi.org/10.1287/opre.1.5.263) · [Owen (2013)](https://artowen.su.domains/mc/Ch-var-is.pdf) |
| **Understanding SGD** | 为什么带噪梯度也能驱动大规模学习？ | [`posts/foundations/sgd/`](posts/foundations/sgd/index.html) | [Bottou (2010)](https://bottou.org/papers/bottou-2010) |
| **Understanding Adam** | 梯度为什么需要方向和平方尺度的两份记忆？ | [`posts/foundations/adam/`](posts/foundations/adam/index.html) | [Kingma & Ba (2015)](https://arxiv.org/abs/1412.6980) |
| **Understanding AdamW** | 为什么 Adam 的 L₂ 与 Weight Decay 不等价？ | [`posts/foundations/adamw/`](posts/foundations/adamw/index.html) | [Loshchilov & Hutter (ICLR 2019)](https://arxiv.org/abs/1711.05101) |
| **Understanding PagedAttention** | 为什么 KV Cache 需要像操作系统一样分页？从 Block Table 到 vLLM Serving | [`posts/inference/pagedattention/`](posts/inference/pagedattention/index.html) | [研究出处](https://arxiv.org/abs/2309.06180) |
| **Understanding DDPG** | 连续动作如何学习？从确定性策略梯度到双目标网络与经验回放 | [`posts/reinforcement-learning/ddpg/`](posts/reinforcement-learning/ddpg/index.html) | [研究出处](https://arxiv.org/abs/1509.02971) |
| **Understanding CNN** | 为什么一个小核在整张图上滑动，就能学习视觉结构？ | [`posts/architectures/cnn/`](posts/architectures/cnn/index.html) | [研究出处](https://doi.org/10.1109/5.726791) |
| **Understanding SVD** | 矩阵如何把空间拉伸成椭圆？从奇异值到最优低秩近似、PCA 与伪逆 | [`posts/foundations/svd/`](posts/foundations/svd/index.html) | [研究出处](https://doi.org/10.1007/BF02288367) |
| **Understanding KV Cache** | 自回归 Decode 为什么要保存历史 K/V？ | [`posts/inference/kv-cache/`](posts/inference/kv-cache/index.html) | [Kwon et al. (SOSP 2023)](https://doi.org/10.1145/3600006.3613165) |
| **Understanding GPT-1** | 为什么预测下一个 token 能迁移到多种语言理解任务？ | [`posts/training/gpt-1/`](posts/training/gpt-1/index.html) | [Radford et al. (2018)](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) |
| **Understanding BERT** | 为什么 MLM 能学到双向上下文？80/10/10、NSP、历史消融与微调如何工作？ | [`posts/training/bert/`](posts/training/bert/index.html) | [Devlin et al. (NAACL 2019)](https://aclanthology.org/N19-1423/) |
| **Understanding QLoRA** | 为什么 65B 模型可以在一张 48GB GPU 上微调？NF4、双重量化与 Paged Optimizers | [`posts/training/qlora/`](posts/training/qlora/index.html) | [Dettmers et al. (NeurIPS 2023)](https://arxiv.org/abs/2305.14314) |
| **Understanding LoRA** | 为什么低秩矩阵足以适配部分下游任务？ | [`posts/training/lora/`](posts/training/lora/index.html) | [Hu et al. (ICLR 2022)](https://arxiv.org/abs/2106.09685) |

Pre-LN vs Post-LN 具有 12 节解读、5 幅独立 SVG、交互式平移实验和纯 Python 的 Jacobian 数值检查；SGD 具有 14 节渐进推导、7 幅独立 SVG、Mini-batch 抽样交互与纯 Python 随机梯度单元测试；ResNet 具有 11 节解读与 10 幅独立 SVG；Transformer 具有 16 节解读与 13 幅独立 SVG，另有最小 PyTorch Attention 示例；Naive Bayes 具有 13 节渐进解释、6 幅独立 SVG、原生 MathML、Multinomial/Bernoulli 对照交互与确定性 Python 断言；SVM 具有 12 节机制推导、6 幅独立 SVG、可调 RBF 相似度矩阵和纯 Python 一维解析示例，采用离线原生 MathML 排版分式、上下标和求和范围；Word2Vec 具有 12 节精读、5 幅内嵌原创图、7 份独立 SVG、SGNS 训练器和数值梯度校验。AdamW 具有 14 节渐进推导、6 幅独立 SVG、二维预条件器交互实验与纯 Python Adam/AdamW 代码断言。GRPO 具有 11 节深度解读、4 幅独立 SVG、可交互优势示例和 Python 断言测试。RLHF 从 SFT、奖励模型与 PPO 出发，包含 12 节推导、4 幅机制图、2 个交互实验和最小数学断言；Adam 具有 14 节机制讲解、7 幅独立 SVG、时间步交互及含 AdamW/AMSGrad 分支的纯 Python 最小实现与单元测试。LoRA 具有 12 节论文精读、6 幅独立 SVG、rank 参数预算交互与纯 Python 合并等价性算例。DPO 具有 12 节机制推导、6 幅独立 SVG、可调 β 交互与最小 Python 公式检验。KV Cache 具有 13 节解读、6 幅独立 SVG、KV 显存交互计算器与纯 Python 数值一致性测试。RoPE 具有 12 节机制推导、4 幅独立 SVG、平移交互演示、纯 Python 旋转验证与长上下文扩展比较。Self-Consistency 提供 12 节解读、5 幅独立 SVG、答案计票交互、数学推导及可执行 Python 示例。教学简化、原论文和后续变体需明确区分；每篇文章的发布状态以 CI 和浏览器验证结果为准。

DQN 包含 14 节机制讲解、6 幅独立 SVG、TD Target / Huber 交互计算器及纯 Python 不变量测试，以 2015 Nature 版本为主线并明确区分 2013 与后续 Double DQN。

FineWeb 包含 14 节数据管道精读、6 幅独立 SVG、1 幅正文交互示意、MinHash banding 与 Edu 阈值交互、3 个原生 MathML 数学块、19 条来源证据及教学数值测试；研究数据版本与更新后统计口径严格区分。

SAC 归入 `reinforcement-learning`，在现有分类内增加 **Off-policy & Experience Replay** 与 **Maximum Entropy RL** 两条主题，不新建顶层分类。文章明确区分 ICML 2018 原版独立 V 网络与后续 twin-target-Q / 自动温度设计，采用离线 MathML、6 幅可独立打开的 SVG、温度交互与标准库单测。

DDPG 包含 13 节连续控制精读、5 幅独立 SVG、可交互 Bellman target 实验、MathML 公式、最小数学断言与 ICLR 2016 原文证据；保留在 `Reinforcement Learning → Continuous Control / Off-policy Actor–Critic`，不新建顶层分类。

RNN 具有 12 节渐进式机制解读、4 幅独立 SVG、4 处原生 MathML、可调梯度实验、纯 Python BPTT 有限差分验证，并区分 Elman 1990 原论文和现代训练算例。

PPO 包含 14 节原论文推导、6 幅独立 SVG、交互式裁剪目标演算、纯标准库数学测试，并单独辨析了 RLHF 的参考模型 KL 与 PPO 的旧策略偏移指标。

Chinchilla 的解读包含 12 节渐进讲解、5 幅独立 SVG、6 组原生 MathML 公式、固定预算交互实验与纯 Python 数学断言；原论文数据和教学示意分别标注。

GPT-1 按 `Training → Pretraining` 既有分类归档，不新建顶级类别；解读包含 13 节原论文阅读、5 幅独立 SVG、4 个 MathML 公式、训练阶段交互、实验消融和确定性因果 Mask 代码检查。历史模型、后续改进与本文独立教学示意分别标注。

The Pile 的 22 个来源按原论文 Table 1 给出有效采样权重，配五幅独立 SVG、原生 MathML 的混合权重与 BPB 公式、可交互三来源采样算例、受控 1.3B 模型实验证据及 Python 数值测试；明确区分历史论文结果与教学模拟。

## 内容分类

| 分类 | 路径 | 范围 |
|---|---|---|
| 基础理论 | `posts/foundations/` | 优化器、正则化、Embedding、Tokenization / BPE、数学基础 |
| 经典机器学习 | `posts/classical-ml/` | SVM、概率模型、树与集成、降维和线性模型 |
| 模型架构 | `posts/architectures/` | CNN、RNN、Transformer、MoE、状态空间、高效注意力与长上下文架构 |
| 强化学习 | `posts/reinforcement-learning/` | Policy Gradient、Actor–Critic、Replay、MCTS、连续控制 |
| 数据与语料 | `posts/datasets/` | 预训练语料、清洗、混合采样、污染与数据治理 |
| 训练与对齐 | `posts/training/` | 预训练、微调、RLHF、分布式训练、Training Parallelism、Mixed Precision、Checkpointing |
| 推理策略与测试时计算 | `posts/reasoning/` | CoT、Self-Consistency、搜索、验证、Test-time Scaling |
| 推理与 Serving | `posts/inference/` | 请求调度、Continuous Batching、KV Cache、Speculative Decoding、Prefill/Decode |
| 系统与 Kernel | `posts/systems/` | GPU、内存层级、CUDA/Triton、编译、Collective Communication、性能建模 |
| **检索与 RAG（新增）** | `posts/retrieval-rag/` | Embedding Retrieval、ANN、Reranking、RAG、Grounding、Hybrid Search |
| **智能体与工具使用（新增）** | `posts/agents/` | ReAct、Planning、Tool Calling、Memory、Agent Evaluation |
| 多模态 | `posts/multimodal/` | Vision / Audio / Language 与跨模态融合 |
| 评测与复现 | `posts/evaluation/` | Benchmark、消融、复现实验协议 |

**分类与目录规则：** `content/categories.json` 是一级分类和二级 Topic 的唯一来源。新分类通过 `posts/<category>/README.md` 建立实体占位；研究专题通过 `posts/<category>/_topics/<topic>/README.md` 建立非发布占位。正式文章始终位于 `posts/<category>/<article-slug>/`，由 `content/posts.json` 注册和管理发布状态。

Linear Regression 使用现有 `classical-ml` → **Linear Models** 分类，不为单篇线性模型新增顶层分类；与后续 Logistic Regression、Ridge/Lasso 构成同一学习路径。其基础历史跨越 Legendre 与 Gauss，证据采用 NIST 和 Berkeley 等方法资料，而非误称一篇现代原论文。

AlexNet 归入 `architectures` 的 **Convolutional Neural Networks & Vision** 主题，而不新建视觉顶层目录；后续 VGG、Inception、ResNet 可形成连贯的 CNN 历史线。原论文的 15.3% Top-5 test error 来自七模型集成，绝非单模型结果。

RNN 沿用 `architectures` 下现有 **Recurrent Networks / LSTM** 主题，不重复新增顶层或近义二级分类；以 Elman 1990 为基本模型，串接 LSTM / GRU 与其他序列架构。

LSTM 归入 `architectures` 的 **Recurrent Networks / LSTM** 二级主题，区分 1997 原始两门版、2000 年遗忘门与现代标准实现。

Seq2Seq 归入 `architectures`，补充 **Sequence-to-Sequence / Encoder–Decoder** 二级主题；无需为一篇论文新建一级分类，后续 RNN、LSTM、Attention 与机器翻译架构可延伸此主题。

MHA 归入 `architectures` 下新增的 **Attention Mechanisms & Multi-Head Attention** 二级专题，不另设一级分类；与 Transformer 机制总览和 GQA 的 Head Sharing 文章相互链接。文章对应 Vaswani et al. 2017 §3.2、Table 3，含六幅 SVG、原生 MathML、交互与确定性数值自检。

GQA 归入 `architectures` 下新增的 **Attention Head Sharing** 专题，不新增一级分类；它对 KV Cache 的推理开销有直接影响，相关实现与 Serving 主题仍归入 `inference`。

RoPE 归入 `architectures`，补充 **Positional Encoding** 主题；不为单篇位置编码论文增设顶层分类，后续 ALiBi、PI、YaRN 可以继续沿此脉络整理。

AdamW 继续使用 `foundations` 中的 **Optimization & Regularization** 主题，不为单篇优化器论文新建顶层分类；未来 Adam、SGD 和学习率调度可共享该主题。各类别均有 `README.md` 占位；占位**不会作为文章上线**。`content/categories.json` 是分类单一数据源，`content/posts.json` 是文章元数据和发布状态的单一数据源。增加新文章不用手动编辑首页、Sitemap 或 RSS。

XGBoost 归入 `classical-ml` 既有 **Trees & Ensembles** 主题，不新建顶层分类；KDD 2016 原论文与当前 `hist` 方法分开描述。文章包含 14 节、6 幅独立 SVG、7 组原生 MathML 公式、交互式阈值/正则化实验和确定性 Python 单元测试。

BPE 放在 `foundations` → **Tokenization & Subword Units**（新增二级专题，沿用现有一级分类），而不是再新增一级目录；对应 `posts/foundations/bpe/` 包含原论文证据、六幅独立 SVG、交互训练/编码演示、MathML 与纯 Python 回归测试。明确区分 Gage 1994、Sennrich et al. ACL 2016 与 GPT-2 byte-level BPE。

SentencePiece 继续归入 `foundations` → **Tokenization & Subword Units**，与 BPE 共享已有二级专题；包含 Unigram 动态规划、子词采样、原生 MathML、五幅 SVG 与原论文实证核验。

WordPiece 继续归于 `foundations` → **Tokenization & Subword Units**，与 BPE 共享二级专题，不新增顶级分类。`posts/foundations/wordpiece/` 提供 14 节论文/源码精读、七幅独立 SVG、MathML、双交互实验、词表评分教学重建与 BERT MaxMatch 纯 Python 测试；明确标出 Google 原版词表训练源码未公开。

## 仓库结构

```text
xm-posts/
├── README.md                     # 项目入口、运行与部署说明
├── AGENTS.md                     # 各类编码 Agent 的协作契约
├── content/
│   ├── categories.json           # 分类元数据
│   └── posts.json                # 单一文章注册表；draft / published
├── posts/
│   ├── training/dpo/              # DPO: 原论文解读、SVG、证据与最小代码
│   ├── foundations/adamw/         # AdamW: HTML、SVG、Python 与证据
│   ├── training/grpo/              # GRPO: HTML、SVG、数值核与证据
│   ├── inference/kv-cache/          # KV Cache: HTML、SVG、证据与代码
│   ├── classical-ml/svm/          # SVM: HTML、SVG、代码与证据
│   ├── reasoning/self-consistency/ # CoT 多路径采样、投票图解与实验证据
│   ├── foundations/sgd/          # SGD: HTML、SVG、Python 与证据
│   ├── foundations/adam/         # Adam: HTML、SVG、Python 优化器与证据
│   ├── foundations/understanding-word2vec/  # Word2Vec: HTML、SVG、SGNS 与证据
│   ├── training/lora/                # LoRA: HTML、6 SVG、代码与证据
│   ├── architectures/
│   │   ├── pre-ln-vs-post-ln/    # LN 放置、残差路径、证据与数值示例
│   │   ├── resnet/
│   │   │   ├── index.html
│   │   │   ├── assets/*.svg
│   │   │   └── evidence.json
│   │   └── transformer/
│   │       ├── index.html
│   │       ├── assets/*.svg
│   │       ├── mini_attention.py
│   │       └── evidence.json
│   ├── retrieval-rag/
│   │   ├── README.md             # 检索与 RAG 一级分类占位
│   │   └── _topics/*/README.md   # 六个二级主题规划占位（不发布）
│   ├── agents/
│   │   ├── README.md             # Agent 一级分类占位
│   │   └── _topics/*/README.md   # 五个二级主题规划占位（不发布）
│   └── {foundations,reinforcement-learning,training,inference,systems,multimodal,evaluation}/
│       ├── README.md            # 分类占位与投稿约定
│       └── _topics/*/README.md  # 规划中的二级主题，不是文章
├── skills/olah-style-paper-posts/ # Skill 正本；SKILL / references / assets / scripts
├── .claude/skills/olah-style-paper-posts/  # 完整 Skill 镜像
├── .pi/skills/olah-style-paper-posts/      # 完整 Skill 镜像
├── .agent/skills/olah-style-paper-posts/   # 完整 Skill 镜像
├── .opencode/skills/olah-style-paper-posts/# 完整 Skill 镜像
├── site/assets/                  # 首页及分类页面的 CSS / JS / SVG
├── scripts/
│   ├── new_post.py               # 新建 draft、注册目录与元数据
│   ├── build_site.py             # 生成 _site/、分类/归档/索引/RSS/Sitemap
│   ├── validate_site.py          # 校验文章、链接、发布排除与 SVG
│   └── sync_skills.py            # 同步四份 Skill，支持 --check
├── tests/test_site.py
├── docs/
│   ├── architecture.md           # 站点与发布架构
│   └── editorial.md              # 论文解读、图示与证据标准
├── .github/workflows/publish.yml # PR 验证；main 自动部署 GitHub Pages
└── _site/                       # CI 构建产物，gitignored
```

## 开始开发

要求 Python 3.11+。静态站点构建仅依赖 Python 标准库；验证使用 pytest、BeautifulSoup 和 Playwright。

```bash
git clone https://github.com/1998x-stack/xm-posts.git
cd xm-posts
python -m pip install -r requirements-dev.txt
python -m playwright install chromium

# 1. 构建静态站点
python scripts/build_site.py

# 2. 检查文章、目录、链接和四份 Skill
python scripts/validate_site.py
python scripts/sync_skills.py --check
python -m pytest -q

# 3. 预览产物：在 _site/ 目录启动静态服务器
cd _site && python -m http.server 8000
# 打开 http://localhost:8000/
```

生产版本链接按 GitHub Pages 项目路径 `/xm-posts/` 构建；在 `http.server` 本地预览时，页面内的相对链接照常工作。页面不使用前端框架、CDN 或远程脚本，不做追踪。

## 新增一篇 Post（可持续扩展）

1. 从分类中选定一个稳定 slug，执行：

   ```bash
   python scripts/new_post.py inference kv-cache \
     --title 'Understanding KV Cache' \
     --subtitle '为什么缓存 Key 与 Value 能加速自回归解码？' \
     --paper 'https://arxiv.org/...'
   ```

2. 这会创建 `posts/inference/kv-cache/`，并在 `content/posts.json` 注册 `status: draft`。依据 [`SKILL.md`](skills/olah-style-paper-posts/SKILL.md) 完成论文取证、渐进式图解、SVG 单独提取、数学与代码核验，填充 `evidence.json`。
3. 在本地执行 `python scripts/build_site.py && python scripts/validate_site.py && python -m pytest -q`；在 Chromium 桌面 / 手机宽度下检查文章交互、图片与溢出。
4. 论文证据和浏览器检查通过后，手动将注册条目的 `status` 改为 `published`，更新实际发布日期、摘要、阅读时长等数据。提交 PR；PR 会自动验证但**不会部署**。
5. PR 合并到 `main` 后，Actions 重新构建并部署。首页、分类列表、归档、`posts.json`、RSS 和 Sitemap 自动更新。`draft` 从线上构建完全排除。

## 数学公式渲染规范

论文中的关键公式优先使用浏览器原生 **MathML Core**，不再以 Unicode 字符串拼凑分式、求和及上下标。新增 [Math Typesetting](skills/olah-style-paper-posts/references/math-typesetting.md) 规范覆盖离线数学排版、公式无障碍、手机端键盘横向滚动、SVG 命名空间隔离与 Playwright QA；静态校验器与浏览器检查自动验证这些约束。对应更新源于 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 并同步至四份 Agent Skill 镜像。

## 多 Agent Skill 兼容

本仓库从 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 引入 `olah-style-paper-posts`，并在四个 Agent 可发现的位置保留**完整文件副本**，包含 `SKILL.md`、`references/`、`assets/`、`scripts/`。实际 Agent 的发现规则视软件配置而定；这四个目录不只是指向正本的坏链接或简短转发文件。

**只编辑 `skills/olah-style-paper-posts/` 正本**，更新后运行：

```bash
python scripts/sync_skills.py
python scripts/sync_skills.py --check
```

镜像不同步会使 CI 失败。正本出处和引入版本详见 [`UPSTREAM.md`](skills/olah-style-paper-posts/UPSTREAM.md)。

## GitHub Pages 与持续部署

[`.github/workflows/publish.yml`](.github/workflows/publish.yml) 在 PR 上执行质量检查、测试、HTML 构建、浏览器 QA；在 `main` push 后，用 `actions/upload-pages-artifact` 和 `actions/deploy-pages` 发布已验证的 `_site/`。工作流申请最低所需的 `contents: read`、`pages: write` 和 `id-token: write` 权限，并将部署放在 `github-pages` 环境。

**首次启用说明（如果自动启用被仓库策略拒绝）：**

进入仓库 **Settings → Pages → Build and deployment → Source → GitHub Actions**，保存后在 **Actions → Validate & publish xm-posts → Run workflow** 重新运行。工作流会先尝试通过 GitHub Pages API 在仓库中自动初始化工作流发布源；若 token 权限不足，这一步会失败并提示人工启用（不会虚构已上线的站点）。详见 [GitHub 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

预期生产入口：`https://1998x-stack.github.io/xm-posts/`。以 GitHub Actions 中成功的 `Publish GitHub Pages` Job 和在线 URL 实际访问为准，而非仅以 YAML 文件存在判定上线。

## 内容标准与归属

主要研究方法来自 Christopher Olah 的 [Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) 与 Harvard NLP 的 [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) **教学组织思路**，而不是复制其文字、代码或图片。论文实验数字标注原论文出处；示意与推导区分教学简化与论文结果；生成的文章不应出现“单文件离线”“原创 SVG”“参考某某风格”等制作过程小字。

协作请先阅读 [`AGENTS.md`](AGENTS.md)、[`docs/editorial.md`](docs/editorial.md) 和 [`CONTRIBUTING.md`](CONTRIBUTING.md)。除非明确核验并添加仓库许可证，否则不要推断第三方论文、图像、代码享有与本站相同的再分发许可。

QLoRA 归入 Training → PEFT / LoRA → Quantized Fine-tuning / QLoRA，不新建顶层分类；提供 12 节机制解读、6 幅 SVG、MathML、权重显存交互与论文证据表。

GAE 归入 `reinforcement-learning` 下已有的 **Policy Gradient / Actor–Critic** 主题，不新增顶层分类；文章包含 14 节、五幅独立 SVG、原生 MathML、λ 交互、终止/截断算例和确定性 Python 验证，明确区分 2016 GAE + TRPO 与后续 GAE + PPO。

### Agents & Tool Use — ReAct

ReAct（Yao et al., ICLR 2023）收录于 `posts/agents/react/`：解释 Thought / Action / Observation 的闭环、论文实验口径、MathML 形式化、可交互轨迹与有限状态 Python 验证。该目录属于 `Agents & Tool Use`，不同于 `reasoning` 的 CoT 与 Self-Consistency；专题规划位于 `posts/agents/_topics/react/`，不单独发布。

MoE 复用 `Architectures → Mixture of Experts (MoE)` 已有二级研究主题，不新增重复分类。[Understanding MoE](posts/architectures/moe/index.html) 以 Shazeer et al. 2017 为主线，区分 GShard、Switch、Mixtral 与 DeepSeekMoE，提供七幅独立 SVG、八组 MathML、路由容量交互与 `tests/test_moe.py` 数值验证。

BERT 归入现有 `Training → Pretraining`，新增二级专题 **Bidirectional Encoder Pretraining / BERT**，不新增顶层类别。文章包含六幅机制 SVG、五组 MathML、MLM 交互、论文消融与标准库不变量测试。
