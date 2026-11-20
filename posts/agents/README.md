# 智能体与工具使用 / Agents & Tool Use

本分类专注模型与外界交互的行动闭环：ReAct、Reflection / Self-Critique、Planning、Tool Calling、Memory、Software Engineering Agents & ACI、Harness Engineering、Agentic RL、Agent Evaluation。

## 已发布专题

- [Agentic Reinforcement Learning](agentic-rl/index.html) — 从单轮 LLM-RL 到多轮环境交互，讲解 POMDP、轨迹回报、信用分配、长程课程与异步训练。
- [Harness Engineering](harness-engineering/index.html) — Agent Runtime、上下文交接、工具、安全、独立评估与维护治理。

## 专题占位

- [ReAct](react/) — 已有正式论文解读；[专题研究规划](_topics/react/README.md) 仍作为未发布的历史规划记录。
- [Reflection & Self-Critique](reflection/) — 从 Self-Refine、CRITIC 到 Reflexion，区分内部反馈、外部验证和跨轮次经验记忆。
- [Software Engineering Agents & ACI](swe-agent/) — SWE-agent：代码搜索、编辑、错误护栏、上下文管理与软件修复评测。
- [Planning](_topics/planning/README.md) — 研究规划占位；尚非正式 Post。
- [Tool Calling](_topics/tool-calling/README.md) — 研究规划占位；尚非正式 Post。
- [Memory](_topics/memory/README.md) — 研究规划占位；尚非正式 Post。
- [Agent Evaluation](_topics/agent-evaluation/README.md) — 研究规划占位；尚非正式 Post。

## 分类边界与发布约定

- `reasoning` 解释内在推理、搜索与测试时计算；`agents` 关注环境观察、工具执行、状态和实际任务结果。
- `retrieval-rag` 研究检索质量和依据溯源；当检索被 Agent 作为工具使用时可做跨分类链接。
- 正式文章放在 `posts/agents/<slug>/index.html`，提供独立 SVG、证据账本及真实 QA，并在 `content/posts.json` 注册。
- `_topics/` 中的 README 仅作规划，占位不创建文章记录，也不会部署为文章。
