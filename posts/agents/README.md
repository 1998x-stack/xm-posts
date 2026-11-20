# 智能体与工具使用 / Agents & Tool Use

本分类专注模型与外界交互的行动闭环：ReAct、Planning、Tool Calling、Memory、Software Engineering Agents & ACI、Agent Evaluation。

## 正式文章

- [ReAct](react/) — Thought / Action / Observation 交错；理解模型如何在推理与外部观察之间更新计划。
- [Function Calling](function-calling/) — 从工具声明、JSON Schema、调用 ID 到应用侧执行、权限验证、结果回传与端到端评测。
- [Software Engineering Agents & ACI](swe-agent/) — SWE-agent：代码搜索、编辑、错误护栏、上下文管理与软件修复评测。

## 专题占位

- [Planning](_topics/planning/README.md) — 研究规划占位；尚非正式 Post。
- [Tool Calling](_topics/tool-calling/README.md) — 主题范围与后续研究规划；已有 Function Calling 正式文章。
- [Memory](_topics/memory/README.md) — 研究规划占位；尚非正式 Post。
- [Agent Evaluation](_topics/agent-evaluation/README.md) — 研究规划占位；尚非正式 Post。

## 分类边界与发布约定

- `reasoning` 解释内在推理、搜索与测试时计算；`agents` 关注环境观察、工具执行、状态和实际任务结果。
- `retrieval-rag` 研究检索质量和依据溯源；当检索被 Agent 作为工具使用时可做跨分类链接。
- 正式文章放在 `posts/agents/<slug>/index.html`，提供独立 SVG、证据账本及真实 QA，并在 `content/posts.json` 注册。
- `_topics/` 中的 README 仅作规划或知识地图，不创建文章记录，也不会作为独立文章部署。
