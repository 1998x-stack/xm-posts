# 分类体系与跨领域归属规则

> 维护对象：`content/categories.json`（一级分类与稳定二级 topic slug）、`content/posts.json`（每篇文章的唯一主分类/主专题）。
> `posts/<category>/_topics/<topic>/README.md` 是规划占位，不是文章，也不是发布目录；`posts/<category>/<slug>/index.html` 才是文章源文件。

## 一级分类及领域边界

| 分类 slug | 收录范围 | 与邻近类别的边界 |
| --- | --- | --- |
| `foundations` | 线性代数、数值稳定、优化与正则化、表示与分词基础 | 具体的学习算法归 `classical-ml`；训练过程与分布式实现归 `training` |
| `classical-ml` | 线性/概率模型、树与集成、核方法、聚类、降维等经典算法 | 深度网络信息路径归 `architectures` |
| `architectures` | CNN、RNN、Transformer、门控、MoE、状态空间、高效注意力，以及神经场/三维场景表示与新视角合成 | GPU 算子实现归 `systems`，线上请求管理归 `inference`；跨模态联合建模归 `multimodal` |
| `reinforcement-learning` | MDP、Bellman、Policy Gradient、Actor–Critic、探索与搜索 | RLHF/GRPO 等模型后训练方案的训练目标与流程归 `training` |
| `datasets` | 语料来源、清洗去重、混合、污染与数据治理 | 任务指标、Benchmark 设计与可重复性归 `evaluation` |
| `training` | 预训练、Scaling Laws、PEFT、知识蒸馏与教师—学生迁移、偏好对齐、分布式与混合精度 | 权重衰减的基础推导可以在 `foundations`，模型知识迁移训练归此；推理部署优化归 `inference` / `systems` |
| `reasoning` | CoT、自一致性、推理采样、验证与测试时计算 | 涉及工具和环境反馈闭环时归 `agents` |
| `inference` | KV Cache、解码、Batching、服务调度和 Prefill/Decode | 硬件 kernel/编译与通讯归 `systems` |
| `systems` | GPU 内存、算子、编译、通信、性能分析及底层优化 | 服务请求、token 调度、端到端 serving 归 `inference` |
| `storage-indexing` | B+ Tree、LSM Tree、页与缓冲区管理、事务恢复、MVCC | 数据库磁盘/索引结构归此类；向量语义召回归 `retrieval-rag`，GPU 算子实现归 `systems` |
| `retrieval-rag` | 向量/ANN、稀疏混合检索、重排序、RAG、证据落地 | Agent 任务计划与工具执行归 `agents`，embedding 基础表征归 `foundations` |
| `agents` | ReAct、规划、工具调用、Agent Memory、Context Engineering、软件工程 Agent、显式状态机与事件驱动工作流、Agent-Computer Interface、Harness Engineering、Agentic RL、Loop Engineering 与端到端评测 | 纯推理策略归 `reasoning`；检索算法归 `retrieval-rag`；跨会话知识管理归 `memory`；推理时上下文的选择、组装与生命周期归 `context-engineering`；PPO / GRPO 等优化算法仍按其训练方法归 `training` 或 `reinforcement-learning`；Loop 关注跨运行的触发、验证、持久化与终止 |
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

### Knowledge Distillation 的分类边界

`knowledge-distillation` 注册为 `training` 下的二级专题，不新增 `model-compression` 一级分类。原因是 KD 的核心对象是训练监督与教师—学生知识迁移；它可以服务模型压缩，也可以用于同规模能力迁移、LLM 推理轨迹学习、多模态知识迁移和扩散生成加速。剪枝、量化与低秩分解仍保留各自技术边界，通过 tags、文章链接与阅读路径建立交叉关系。

专题采用多维标签而非互斥树：知识信号（response / feature / relation / sequence）、教师访问方式（white-box / black-box）、教师拓扑（single / multi-teacher / self-distillation）、数据机制（offline / online / on-policy / data-free / synthetic）和能力目标（通用任务 / reasoning / multimodal / diffusion / agent）。一篇论文可以同时落在多个轴上；每篇文章仍只有一个主 category/topic。

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


## Loop Engineering 专题边界

- **主分类：** `agents`；**二级专题：** `loop-engineering`。
- 研究 Agent 运行之间的外层工作循环：事件 / 日程触发、任务发现与去重、上下文投影、隔离执行、独立验证、持久状态、预算、停止条件与人工升级。
- 不新增一级分类。Loop Engineering 依赖 Harness 提供的工具、权限、沙箱和观测能力，但重点是跨运行的任务生命周期；Harness 主要描述单次运行时及其执行环境。
- 与 ReAct（单次 Thought–Action–Observation）、Planning（计划生成与更新）、Memory（状态与经验保存）、Context Engineering（本轮信息选择与组装）、Agentic RL（训练与优化 Agent 策略）和 Agent Evaluation（任务结果测量）有关联但不等价。
- 2026 年 Loop Engineering 文献仍处于探索阶段。引用仓库挖掘比例时必须说明启发式筛选分母；不能把观察性采用数据写成因果效率提升，也不能把预印本提出的构件称为统一行业标准。

## 2026-11-21 知识体系扩展

本批次以“先明确知识对象，再连接可验证的学习路径”为原则扩展专题。新增两个一级知识域，并为 Agent、训练、检索与评测补充边界清晰的二级专题。

### 新增一级知识域

- **`knowledge-representation` — Knowledge Representation & Semantic Technologies**
  - `ontology-engineering`：本体工程与建模。
  - `semantic-web-standards`：RDF、RDFS、OWL、SKOS 与 SPARQL。
  - `knowledge-graphs`：知识图谱构建与查询。
  - `knowledge-reasoning`：逻辑推理与一致性。
  - `ontology-learning-alignment`：本体学习、匹配与 LLM 辅助工程。
  - 边界：研究符号知识的显式语义建模、关系约束、查询与推理；不等同于向量检索或普通 RAG。

- **`decision-models` — Probabilistic Decision Models**
  - `typed-decision-models`：类型化决策模型。
  - `cost-sensitive-decision-theory`：代价敏感决策理论。
  - `probability-calibration`：概率校准。
  - `risk-budgeting`：风险预算与统计保证。
  - `selective-prediction`：选择性预测与拒绝决策。
  - `decision-routing`：决策路由与委派。
  - `robustness-and-bias`：鲁棒性、偏差与不变性。
  - 边界：研究如何把模型输出的概率转化为可审计的行动决策；不把“最大概率类别”直接等同于“最优动作”。

### 既有一级知识域的二级专题扩展

- **`agents`**
  - `reflection`：反思、自我批评与语言反馈。
  - `autonomous-agents`：自主 Agent 系统与框架。
  - `autonomous-execution`：自主执行与迭代控制。
  - `tool-integration-protocols`：工具集成与互操作协议（含 MCP）。
  - 与 `tool-calling` 的边界：Function Calling 关注单次结构化工具调用；MCP 关注 Host / Client / Server 间的协议互操作。
  - 与 `harness-engineering` 的边界：Reflection 关注如何利用反馈修正行为；Harness 关注运行时、权限、工具、环境和验证基础设施。

- **`training`**
  - `supervised-finetuning`：监督微调与指令微调。
  - `reward-hacking`：奖励黑客与规格博弈。
  - 与 `distributed-training`、`checkpointing` 共同构成从训练目标、数据、优化到系统可靠性的学习路径。

- **`retrieval-rag`**
  - `query-understanding`：查询理解与对话式搜索。
  - 先解析用户意图、实体、约束与上下文，再进入 Query Rewriting、Retrieval、Reranking 与 RAG；避免把查询理解和检索执行混为一谈。

- **`evaluation`**
  - `llm-as-a-judge`：LLM 评审器与 Judge 可靠性。
  - 与 `agent-evaluation` 配合：前者研究评审器如何测量质量，后者研究 Agent 系统的任务成功、轨迹、可靠性、安全与成本。

### 跨专题关系原则

- **Function Calling → MCP → Harness Engineering**：从调用接口到协议互操作，再到受控运行时。
- **Query Understanding → Retrieval / RAG → Context Engineering**：从理解需求到检索证据，再到组织推理上下文。
- **SFT → Preference Optimization → Reward Hacking / Evaluation**：从监督目标到偏好优化，再到目标错配与测量审计。
- **Ontology → Knowledge Graph → Retrieval / RAG**：显式语义知识与统计检索互补，不互相替代。
- **Probability Calibration → Cost-sensitive Decision → Selective Prediction → Agent Routing**：从可信概率到风险敏感的执行、复核或拒绝。

### 模仿学习（Imitation Learning）

- **主归属**：`reinforcement-learning / imitation-learning`（稳定二级 Topic，现有一级分类不变），以「从专家示范学习策略」为核心。
- **教学范围**：Behavior Cloning、协变量偏移、DAgger、Inverse Reinforcement Learning、MaxEnt IRL、GAIL 与 Diffusion Policy。
- **概念边界**：模仿学习并不要求显式环境奖励；置于强化学习导航区是为了连接策略学习和决策问题，而不是宣称模仿学习是奖励驱动 RL 的严格子集。数据聚合程序、逆奖励推断、占用测度匹配与生成式动作模型应区分学习信号和模型结构。


## State Machines & Workflow Control 专题边界

- **主分类：** `agents`；**二级专题：** `state-machines`。不新增一级分类。
- 研究离散状态、事件、转移、守卫、动作和终态约束，覆盖 DFA / NFA、Mealy / Moore、EFSM、层次状态机与 Statecharts。
- 工程重点是协议、工具调用、Agent Runtime 与长任务工作流中的合法路径、非法事件、重试、超时、取消、持久化和并发控制。
- 与 `loop-engineering` 的边界：State Machines 研究单个系统/任务实例的显式状态与合法转移；Loop Engineering 研究跨运行的触发、发现、隔离执行、验证、持久化与终止。
- 与 `harness-engineering` 的边界：State Machines 提供行为控制模型；Harness Engineering 组织工具、权限、环境、可观测性和验证基础设施。
- 与 `architectures/state-space-models` 的边界：有限状态机使用有限个离散控制状态；SSM 使用数值状态变量和状态方程传播历史信息。不要因共享术语 state 而混同。
- 与 `reinforcement-learning` 的边界：MDP 增加动作、概率转移和奖励，用于策略决策；FSM 主要刻画控制行为的合法路径。二者可组合，但不等价。
- Event Sourcing 是事件持久化与状态重建模式；Workflow Engine 是带持久化、计时器、重试和 Worker 调度的执行系统；它们可使用 FSM，但不属于同一抽象层。


## Robotic Process Automation 专题边界（2026-11）

- 主分类：agents；二级专题：robotic-process-automation。
- 收录传统 RPA、软件机器人、UI 自动化、机器人编排、流程挖掘辅助候选发现、IPA 与 Agentic Process Automation 的交叉研究。
- Traditional RPA 的核心是预定义规则、确定性步骤和受控的业务状态转换；它可以通过 UI 操作遗留应用，但不要求模型进行开放式规划。
- BPM / Workflow 负责端到端流程设计、责任、事件和治理；RPA 通常执行其中的任务级动作。二者互补，不应把 RPA 描述为完整 BPM 的替代品。
- API Automation 优先使用稳定接口和数据契约；只有接口不可用或改造成本不合理时，才将 UI RPA 作为兼容层。
- IPA 在执行流程中加入 OCR、文档理解、ML 或 NLP；Agentic Process Automation 则在不确定环节加入 LLM Agent 的理解、规划与异常处理能力。
- 与 ReAct 的边界：ReAct 研究 Thought–Action–Observation 的动态推理循环；RPA 研究如何把已明确的业务步骤转化为可重复、可审计的确定性执行。
- 与 Tool Calling 的边界：Function Calling 定义模型如何调用结构化工具；RPA 定义工具/机器人如何跨应用完成具体业务操作。
- 与 Harness Engineering 的边界：Harness 研究 Agent Runtime、权限、环境、状态和验证基础设施；RPA 是可被 Harness 编排的一类确定性执行器。
- 与 Process Mining 的关系：Process Mining 从事件日志发现真实流程并检查偏差；Task Mining 更关注 UI 交互轨迹。两者可辅助候选发现，但不自动替代业务、风险与经济评估。
- 评估必须区分 UI 动作成功、业务状态正确、端到端流程完成和组织层面的投资回报；不得把界面 Toast 或按钮点击当作持久化业务正确性的证据。
- 新增 RPA 文章应将原始 RPA 研究、近年系统综述、Agentic Automation 论文和企业软件状态验证研究分层引用；预印本、概念模型和教学模拟器必须标明证据等级。
