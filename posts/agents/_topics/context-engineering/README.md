# Context Engineering & Context Management

> 稳定 Topic ID：\`agents/context-engineering\`

## 收录范围

研究 Agent 每次推理时的完整信息环境，以及长时任务中的上下文生命周期：

- 上下文预算、信息选择、排序、去重与压缩；
- Prompt、工具 Schema、few-shot、消息历史与外部证据的组装；
- RAG、Just-in-Time Retrieval 与渐进式披露；
- Session trimming、summarization、compaction；
- Agent Memory、知识表示、记忆纠错与跨会话注入；
- Sub-agent context isolation、上下文交接和可观测性；
- 上下文安全、来源溯源、陈旧信息与注入攻击；
- Context quality evaluation 与长期任务可靠性。

## 与相邻专题的边界

| Topic | 边界 |
|---|---|
| \`memory\` | 聚焦跨会话知识如何写入、组织、维护与重用；本专题覆盖完整推理时上下文生命周期 |
| \`tool-calling\` | 聚焦工具接口、参数与调用协议；本专题研究工具定义和工具结果如何进入上下文 |
| \`retrieval-rag\` | 聚焦检索算法和证据召回；本专题研究召回结果如何筛选、压缩和组装 |
| \`react\` | 聚焦 Thought / Action / Observation 推理—行动循环；本专题聚焦每轮循环的上下文状态管理 |
| \`software-engineering-agents\` | 聚焦代码 Agent 与 ACI；本专题研究可迁移到各类 Agent 的上下文组织方法 |

## 典型学习路径

Prompt Engineering → ReAct / Tool Use → Agent Memory → Context Engineering → Harness Engineering & Long-horizon Agents

## 证据原则

优先引用原始论文、官方 Engineering 文章、官方 Cookbook 和 API 文档。区分研究综述、厂商工程案例、产品特定能力与本文的综合教学模型。不要把厂商产品实现写成跨模型的通用保证。
