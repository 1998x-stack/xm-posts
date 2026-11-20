# 分类体系与跨领域归属规则

> 维护对象：`content/categories.json`（一级分类与稳定二级 topic slug）、`content/posts.json`（每篇文章的唯一主分类/主专题）。
> `posts/<category>/_topics/<topic>/README.md` 是规划占位，不是文章，也不是发布目录；`posts/<category>/<slug>/index.html` 才是文章源文件。

## 14 个一级分类及领域边界

| 分类 slug | 收录范围 | 与邻近类别的边界 |
| --- | --- | --- |
| `foundations` | 线性代数、数值稳定、优化与正则化、表示与分词基础 | 具体的学习算法归 `classical-ml`；训练过程与分布式实现归 `training` |
| `classical-ml` | 线性/概率模型、树与集成、核方法、聚类、降维等经典算法 | 深度网络信息路径归 `architectures` |
| `architectures` | CNN、RNN、Transformer、门控、MoE、状态空间、高效注意力，以及神经场/三维场景表示与新视角合成 | GPU 算子实现归 `systems`，线上请求管理归 `inference`；跨模态联合建模归 `multimodal` |
| `reinforcement-learning` | MDP、Bellman、Policy Gradient、Actor–Critic、探索与搜索 | RLHF/GRPO 等模型后训练方案的训练目标与流程归 `training` |
| `datasets` | 语料来源、清洗去重、混合、污染与数据治理 | 任务指标、Benchmark 设计与可重复性归 `evaluation` |
| `training` | 预训练、Scaling Laws、PEFT、偏好对齐、分布式与混合精度 | 权重衰减的基础推导可以在 `foundations`，但工程训练管线在此 |
| `reasoning` | CoT、自一致性、推理采样、验证与测试时计算 | 涉及工具和环境反馈闭环时归 `agents` |
| `inference` | KV Cache、解码、Batching、服务调度和 Prefill/Decode | 硬件 kernel/编译与通讯归 `systems` |
| `systems` | GPU 内存、算子、编译、通信、性能分析及底层优化 | 服务请求、token 调度、端到端 serving 归 `inference` |
| `storage-indexing` | B+ Tree、LSM Tree、页与缓冲区管理、事务恢复、MVCC | 数据库磁盘/索引结构归此类；向量语义召回归 `retrieval-rag`，GPU 算子实现归 `systems` |
| `retrieval-rag` | 向量/ANN、稀疏混合检索、重排序、RAG、证据落地 | Agent 任务计划与工具执行归 `agents`，embedding 基础表征归 `foundations` |
| `agents` | ReAct、规划、工具调用、Agent Memory、Context Engineering、软件工程 Agent、Agent-Computer Interface、Harness Engineering、Agentic RL 与端到端评测 | 纯推理策略归 `reasoning`；检索算法归 `retrieval-rag`；跨会话知识管理归 `memory`；推理时上下文的选择、组装与生命周期归 `context-engineering`；PPO / GRPO 等优化算法仍按其训练方法归 `training` 或 `reinforcement-learning` |
| `multimodal` | 视觉/语言/音频的跨模态建模与对齐 | 通用单模态 CNN 架构仍可归 `architectures` |
| `evaluation` | 模型/任务 Benchmark、ROC/PR、消融与复现 | 训练数据质量、污染事实与许可证归 `datasets` |


### Neural Rendering & 3D Scene Representations

- 稳定专题 slug：`architectures/neural-rendering-3d-vision`。
- 收录 NeRF、Mip-NeRF、Instant-NGP 等神经场/隐式场景表示，以及用于同一新视角合成任务的显式或混合表示对照（例如 3D Gaussian Splatting）。
- 不新增一级 `computer-vision` 分类：当前单篇 NeRF 不足以支撑新的顶层领域；`architectures` 可承载其模型信息流与场景表示机制。若未来视觉任务、几何重建、视频理解等形成多个稳定专题，再依据实际内容规模重新评估顶层分类。
- 术语边界：NeRF 是连续神经场 + 体渲染；3D Gaussian Splatting 是以显式各向异性高斯为基元的竞争性场景表示，不应被写成 NeRF 的一个网络变体。

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


## Harness Engineering 专题边界

- **主分类：** `agents`；**二级专题：** `harness-engineering`。
- 研究模型外部的运行时系统：Agent Loop、模型接入、工具与动作、上下文/记忆、安全权限、编排、扩展、可观测性、失败归因、验证与维护熵。
- 不新建一级分类。Harness 横跨 ACI、Memory、Evaluation 和 Software Engineering Agents，但其核心研究对象是把这些能力组织成可恢复、可验证的运行时。
- ReAct 主要解释推理—行动—观察循环；SWE-agent / ACI 主要研究操作接口；Agent Memory 主要研究跨会话知识；Harness Engineering 将这些能力置于完整任务生命周期中进行系统设计。
- Harness 与 Evaluation Harness 必须区分：前者使模型能够行动，后者运行任务并测量结果。
- 当前专题文献仍在快速演进；对预印本提出的子系统分类，应标注来源和研究状态，不把它们描述为已统一的行业标准。


## Agentic RL 专题归属（2026-11）

- **主分类：** `agents`；**二级专题：** `agentic-rl`。
- 研究多轮、部分可观测环境中的策略学习、工具交互、轨迹奖励、信用分配、长程课程与异步 Rollout。
- 不新增一级分类：Agentic RL 的任务形态属于 Agent 环境交互闭环；PPO、GAE、GRPO 等算法仍保留在原有强化学习 / 训练专题。
- 与 ReAct / Tool Calling / Planning 通过阅读路径关联，避免把“行动协议”“优化算法”和“训练系统”混成一个概念。


## Context Engineering 专题边界（2026-11）

- **主分类：** `agents`；**二级专题：** `context-engineering`。不新增一级分类。
- 收录推理时上下文的选择、预算、检索、处理、组装、裁剪、压缩、持久化、隔离、安全与评测。
- `memory` 继续聚焦跨会话经验的写入、组织、验证、纠错与重用；`context-engineering` 研究每一轮推理时如何组合全部必要信息。
- `retrieval-rag` 继续聚焦召回、向量索引、重排序与证据检索；`context-engineering` 负责把检索结果纳入完整推理上下文。
- `tool-calling` 聚焦工具接口与调用协议；`context-engineering` 负责工具 Schema、工具输出与执行状态在上下文中的管理。
- `harness-engineering` 研究 Agent Runtime 的工具、权限、执行环境、可观测性与治理；Context Engineering 是其中关键的信息管理子系统，两者应互相链接而非合并成同一个 Topic。
