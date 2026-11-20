# 分类体系与跨领域归属规则

> 维护对象：`content/categories.json`（一级分类与稳定二级 topic slug）、`content/posts.json`（每篇文章的唯一主分类/主专题）。
> `posts/<category>/_topics/<topic>/README.md` 是规划占位，不是文章，也不是发布目录；`posts/<category>/<slug>/index.html` 才是文章源文件。

## 14 个一级分类及领域边界

| 分类 slug | 收录范围 | 与邻近类别的边界 |
| --- | --- | --- |
| `foundations` | 线性代数、数值稳定、优化与正则化、表示与分词基础 | 具体的学习算法归 `classical-ml`；训练过程与分布式实现归 `training` |
| `classical-ml` | 线性/概率模型、树与集成、核方法、聚类、降维等经典算法 | 深度网络信息路径归 `architectures` |
| `architectures` | CNN、RNN、Transformer、门控、MoE、状态空间与高效注意力结构 | GPU 算子实现归 `systems`，线上请求管理归 `inference` |
| `reinforcement-learning` | MDP、Bellman、Policy Gradient、Actor–Critic、探索与搜索 | RLHF/GRPO 等模型后训练方案的训练目标与流程归 `training` |
| `datasets` | 语料来源、清洗去重、混合、污染与数据治理 | 任务指标、Benchmark 设计与可重复性归 `evaluation` |
| `training` | 预训练、Scaling Laws、PEFT、偏好对齐、分布式与混合精度 | 权重衰减的基础推导可以在 `foundations`，但工程训练管线在此 |
| `reasoning` | CoT、自一致性、推理采样、验证与测试时计算 | 涉及工具和环境反馈闭环时归 `agents` |
| `inference` | KV Cache、解码、Batching、服务调度和 Prefill/Decode | 硬件 kernel/编译与通讯归 `systems` |
| `systems` | GPU 内存、算子、编译、通信、性能分析及底层优化 | 服务请求、token 调度、端到端 serving 归 `inference` |
| `storage-indexing` | B+ Tree、LSM Tree、页与缓冲区管理、事务恢复、MVCC | 数据库磁盘/索引结构归此类；向量语义召回归 `retrieval-rag`，GPU 算子实现归 `systems` |
| `retrieval-rag` | 向量/ANN、稀疏混合检索、重排序、RAG、证据落地 | Agent 任务计划与工具执行归 `agents`，embedding 基础表征归 `foundations` |
| `agents` | ReAct、规划、工具调用、记忆、Agent 端到端评估 | 纯推理策略归 `reasoning`；检索方法归 `retrieval-rag` |
| `multimodal` | 视觉/语言/音频的跨模态建模与对齐 | 通用单模态 CNN 架构仍可归 `architectures` |
| `evaluation` | 模型/任务 Benchmark、ROC/PR、LLM-as-a-Judge、评审器可靠性、偏差校准、消融与复现 | 训练数据质量、污染事实与许可证归 `datasets`；Agent 端到端任务执行评估归 `agents` |

## 二级分类治理

1. 每篇文章恰好登记一个 `category` 与一个 **已注册** `topic`。跨学科关联使用 `tags` 与文章链接，不为同一术语复制多个一级分类。
2. `topic.slug` 是公开锚点的一部分（`#topic-<slug>`），**先保留现有稳定 slug，再改善标题、解释和页面导航**。不要仅因措辞好看而改 slug。
3. 对确有不同边界的二级主题，要求标题与描述不同；不得让两个 topic 共享同一展示标题。当前 Systems 已区分 Kernel 编程、GPU 内存、编译/内核优化、Collectives、分布式通信和 Roofline/Benchmark。
4. 占位目录必须使用精确的注册 slug。新增 Topic 优先写分类元数据，再添加 `_topics/` 的 README；单篇新文章通常不值得新增一级分类。
5. Draft 必须继续以 `status: draft` 保持离线，不要将规划中的 README 当作 `published` 条目。

## 2026-11 分类占位整合

| 原占位目录（未注册 ID） | 归并到已注册的主 topic |
| --- | --- |
| `architectures/_topics/efficient-mobile-cnns` | `architectures/_topics/efficient-mobile-cnn` |
| `architectures/_topics/gated-ffn-activations` | `architectures/_topics/gating-mechanisms` |
| `architectures/_topics/gating-multiplicative-interactions` | `architectures/_topics/gating-mechanisms` |
| `foundations/_topics/softmax-logsumexp` | `foundations/_topics/numerical-stability` |

这些旧路径是未发布的研究占位，并非文章 URL。整理中没有迁移或删除已发布的文章路径，也没有改变现有 Systems 二级 slug。

## 新 Post 审查与合并顺序

1. 在 `content/categories.json` 中寻找现有一级与二级归属，使用最窄且语义准确的主专题；确有缺口再补新的 topic。
2. 修改 `content/posts.json`，核对 `category / slug` 唯一、`topic` 已注册，检查出版状态和来源证据。
3. 校验目录、SVG/MathML、数学数值测试、跨文章链接和文档；`_topics` 必须与 schema 一致。
4. 运行 `python scripts/sync_skills.py --check`、`python -m pytest -q`、`python scripts/build_site.py`、`python scripts/validate_site.py`，并做完整浏览器验证。
5. PR 先审查完整 diff 和 Actions 结果；只在主分支可无冲突合并且 CI 成功后合并。合并后单独检查 Pages 工作流与在线网址。旧 PR 只有在新 PR 已承接其全部有效变更后才标记 superseded。

自动回归：`tests/test_taxonomy_contract.py` 对重复的 ID/标题、孤儿占位目录、文章主专题和已发布文件路径进行检测。详见根目录 `AGENTS.md` 及 `docs/editorial.md`。


## LLM-as-a-Judge 专题边界

`evaluation/llm-as-a-judge` 收录将 LLM 用作评审器的评价方法与可靠性研究：评价 rubric、pointwise / pairwise / listwise 判断、critique / verifier、人工一致性、位置与长度偏差、校准、对抗鲁棒性，以及评审器自身的 meta-evaluation。若重点是 Agent 在工具、环境和多步骤任务中的端到端成功率，主专题仍归 `agents/agent-evaluation`；若重点是偏好标签如何进入 Reward Model / RLHF / DPO 训练，则主专题归 `training/rlhf` 或 `training/preference-optimization`，并用 tags 关联本专题。
