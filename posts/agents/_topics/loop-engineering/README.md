# Loop Engineering

> **专题说明 / Topic scope** — 研究如何把 Agent 的单次运行组织成可持续触发、可验证、可恢复且受治理的外层工作循环。

- **一级分类**：`agents`
- **稳定 Topic ID**：`loop-engineering`
- **研究范围**：事件 / 日程触发、任务发现与去重、循环编排、独立验证、状态持久化、预算与权限边界、停止条件、人工升级和跨会话恢复。
- **与相邻主题的边界**：
  - `react` 关注单次执行中的 Thought–Action–Observation；
  - `planning` 关注任务分解与计划更新；
  - `memory` 关注跨步骤 / 跨会话的信息保存与检索；
  - `software-engineering-agents` 关注代码仓库任务中的 ACI 与执行能力；
  - `loop-engineering` 关注外层系统何时触发、如何分派、如何验收、写回什么以及何时终止。
- **候选机制**：schedule / repository event、durable task state、verifier、retry budget、human escalation、version-bound approval。
- **证据边界**：Loop Engineering 是 2026 年出现的新兴实践术语；研究性预印本和工程博客提供了机制与案例，但不等于已有充分受控实验证明所有自动循环都提升质量。
- **发布规则**：正式文章位于 `posts/agents/<article-slug>/index.html`；此目录只说明 Topic 范围，不作为文章或 RSS 条目。
