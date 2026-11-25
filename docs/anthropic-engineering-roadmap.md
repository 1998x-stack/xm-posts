# Anthropic Engineering → xm-posts：29 篇文章盘点与分批建设路线

> 盘点日期：2026-11-23。官方 Engineering 栏目显示 29 篇文章。本文将“直接覆盖”“主题覆盖”和“尚无独立文章”分开记录；主题覆盖不等于已经复现对应官方工程案例。

## 建设原则

1. 先以 Anthropic 官方 Engineering 栏目为全集，再扫描 xm-posts 的 `content/posts.json`、文章目录、证据账本和相关 PR 去重。
2. 不把普通博客文章伪装成同行评审论文；官方工程文章使用 `source_label: 官方工程文章`，所有公司报告数字都标记为自述数据。
3. 每批 3 个主题；每篇先读原文、抽取主张与边界，再写技术叙事、独立 SVG、MathML（有数学必要时）、最小可运行示例和测试。
4. 草稿先使用 `status: draft`，不进入首页、RSS、sitemap、PDF 或 Pages 文章集合；只有结构、证据、浏览器 QA 和 CI 完成后才能转为 published。
5. 新文章应与现有 ReAct、SWE-agent、Agent Evaluation、Function Calling、MCP、Context Engineering、Harness Engineering、Loop Engineering 和 Agent Memory 建立阅读关系；发布前再写入 `content/reading_paths.json`。

## 官方文章全集与去重结果

| # | 日期 | 官方文章 | xm-posts 对应情况 | 处理策略 |
|---:|---|---|---|---|
| 1 | 2026-11-13 | Building strong safety evaluations | 尚无独立安全评测文章；Agent Evaluation / LLM-as-a-Judge 提供基础 | 新建 safety-evaluations |
| 2 | 2026-11-06 | The components of agent memory | `agents/agent-memory-components` 直接覆盖 | 保留，后续交叉审计 |
| 3 | 2026-10-13 | Redesigning source control at Anthropic | 尚无 Scion / Agent-scale VCS 专题 | 新建 developer-infrastructure |
| 4 | 2026-05-25 | How we contain Claude across products | 尚无 Agent containment 专题 | 新建 agent-security |
| 5 | 2026-04-23 | An update on recent Claude Code quality reports | 尚无 Claude Code 质量事故复盘专题 | 新建事故分析文章 |
| 6 | 2026-04-08 | Scaling Managed Agents: Decoupling the brain from the hands | Harness / Agentic RL 有背景，但没有 Managed Agents 架构专题 | 新建 managed-agents |
| 7 | 2026-03-25 | How we built Claude Code auto mode: a safer way to skip permissions | Agent security / tool calling 部分相关 | 新建权限决策专题 |
| 8 | 2026-03-24 | Harness design for long-running application development | `agents/harness-engineering` 已覆盖总体框架 | 对现有文章增补长任务设计 |
| 9 | 2026-03-06 | Eval awareness in Claude Opus 4.6’s BrowseComp performance | Agent Evaluation 部分覆盖；无 eval awareness 专题 | 新建 benchmark awareness 专题 |
| 10 | 2026-02-05 | Building a C compiler with a team of parallel Claudes | SWE-agent / Harness 有关联，无并行 Claude 编译器案例 | 新建 multi-agent coding case study |
| 11 | 2026-02-05 | Quantifying infrastructure noise in agentic coding evals | Agent Evaluation 有基础，无 infra noise 量化专题 | 新建评测基础设施专题 |
| 12 | 2026-01-21 | Designing AI-resistant technical evaluations | Agent Evaluation 部分覆盖 | 增补 adversarial / AI-resistant eval 设计 |
| 13 | 2026-01-09 | Demystifying evals for AI agents | `agents/agent-evaluation` 已有总体框架 | 对照原文补充 eval taxonomy 与工程协议 |
| 14 | 2025-11-26 | Effective harnesses for long-running agents | Harness / Loop Engineering 部分覆盖 | 对照原文补充 long-running harness |
| 15 | 2025-11-24 | Introducing advanced tool use on the Claude Developer Platform | Function Calling / MCP 部分覆盖 | 新建 advanced tool use 专题 |
| 16 | 2025-11-04 | Code execution with MCP: Building more efficient agents | MCP 已有；无 code execution 具体专题 | 新建 MCP code execution |
| 17 | 2025-10-20 | Beyond permission prompts: making Claude Code more secure and autonomous | Agent Security 尚未建立 | 与 containment / auto mode 串联 |
| 18 | 2025-10-16 | Equipping agents for the real world with Agent Skills | 尚无 Agent Skills 独立文章 | 新建 Agent Skills |
| 19 | 2025-09-29 | Effective context engineering for AI agents | `agents/context-engineering` 已有广义专题 | 对照原文增补 Anthropic 实践 |
| 20 | 2025-09-17 | A postmortem of three recent issues | 尚无对应事故复盘 | 新建 reliability postmortem |
| 21 | 2025-09-11 | Writing effective tools for agents — with agents | Function Calling 已有通用覆盖 | 增补工具设计、工具迭代与失败模式 |
| 22 | 2025-06-26 | Desktop Extensions: One-click MCP server installation for Claude Desktop | MCP 已有协议解释；无 Desktop Extension 专题 | 新建 Desktop Extensions |
| 23 | 2025-06-18 | Confidential Inference via Trusted Virtual Machines | 尚无 confidential inference 专题 | 新建可信执行环境专题 |
| 24 | 2025-06-13 | How we built our multi-agent research system | ReAct / Agentic RL 有基础，无研究系统架构专题 | 新建 multi-agent research system |
| 25 | 2025-04-18 | Claude Code: Best practices for agentic coding | SWE-agent / Harness 部分相关 | 整理实践与反模式，避免重复泛讲 |
| 26 | 2025-03-20 | The "think" tool: Enabling Claude to stop and think in complex tool use situations | ReAct / Function Calling 有基础，无 think tool 专题 | 新建 tool-use control 专题 |
| 27 | 2025-01-06 | Raising the bar on SWE-bench Verified with Claude 3.5 Sonnet | SWE-agent 已有，但不是该 benchmark 提升案例 | 对照原文补充 benchmark 方法与结果 |
| 28 | 2024-12-19 | Building effective agents | ReAct / AutoGPT / Harness 已有 | 用官方文章审查现有 Agent 基础路线 |
| 29 | 2024-09-19 | Introducing Contextual Retrieval | RAG / Query Understanding 有基础，无 Contextual Retrieval 专题 | 新建或增补检索增强专题 |

## 执行批次

### Batch 01 — 安全、基础设施与隔离（本 PR）

1. Building strong safety evaluations → `posts/evaluation/anthropic-safety-evaluations/`
2. Redesigning source control at Anthropic → `posts/systems/agent-scale-source-control/`
3. How we contain Claude across products → `posts/agents/agent-containment/`

### Batch 02 — Claude Code 与 Managed Agents

1. An update on recent Claude Code quality reports
2. Scaling Managed Agents: Decoupling the brain from the hands
3. How we built Claude Code auto mode

### Batch 03 — 并行编程与 Agentic Coding Eval

1. Harness design for long-running application development（现有 Harness 深度增补）
2. Eval awareness in Claude Opus 4.6’s BrowseComp performance
3. Building a C compiler with a team of parallel Claudes

### Batch 04 — Evaluation 方法学

1. Quantifying infrastructure noise in agentic coding evals
2. Designing AI-resistant technical evaluations
3. Demystifying evals for AI agents（现有 Agent Evaluation 深度增补）

### Batch 05 — Harness 与 Tool Use

1. Effective harnesses for long-running agents
2. Introducing advanced tool use on the Claude Developer Platform
3. Code execution with MCP

### Batch 06 — 安全权限、Skills 与 Context

1. Beyond permission prompts: making Claude Code more secure and autonomous
2. Equipping agents for the real world with Agent Skills
3. Effective context engineering for AI agents（现有文章深度增补）

### Batch 07 — 工具生态与可靠性

1. A postmortem of three recent issues
2. Writing effective tools for agents — with agents（现有 Function Calling 深度增补）
3. Desktop Extensions

### Batch 08 — 基础设施与研究系统

1. Confidential Inference via Trusted Virtual Machines
2. How we built our multi-agent research system
3. Claude Code: Best practices for agentic coding

### Batch 09 — Agent 推理与基准

1. The "think" tool
2. Raising the bar on SWE-bench Verified（现有 SWE-agent 深度增补）
3. Building effective agents（现有 ReAct / AutoGPT / Harness 路线审查）

### Batch 10 — Retrieval 与现有知识库复核

1. Introducing Contextual Retrieval
2. The components of agent memory（已有文章交叉审计，不重复建文）
3. xm-posts RAG / Query Understanding（与 Contextual Retrieval 的边界复核）

## Batch 01 技术范围与验收标准

### 01 Safety Evaluations

- Construct validity：拒绝率不是安全性的代理变量。
- Observational vs causal evaluation。
- Harmful / benign paired prompts 与 over-refusal。
- Multi-turn simulated user：固定首轮、动态后续轮、trajectory-level grading。
- Internal validity：contamination、reward hacking、difficulty calibration。
- LLM grader：atomic rubric、human agreement、bias tests、fail-loudly。
- Preregistration、paired comparison、confidence intervals、sample-size caveats。
- 沙箱和实时监控的运行安全。

### 02 Agent-scale Source Control

- Git distributed/offline assumptions 与 online agent workload。
- Changeset / WAL、content-addressed blob、derived data。
- Server-authoritative API、refs coordination、sparse / virtualized checkout。
- scion-daemon → regional cache → scion-server → Spanner / object storage。
- 公司自述指标与适用边界；Scion 不是 Git 的普适替代品。
- 通过可运行 toy object selector 解释按需获取，不伪装成 Scion 实现。

### 03 Agent Containment

- User misuse / model misbehavior / external attacker。
- Environment / model / external-content 三类防御。
- Ephemeral container、OS sandbox + HITL、sealed VM。
- Trust dialog 前配置解析、user-mediated injection、egress capability grant。
- EDR visibility、tool output prompt injection、persistent memory poisoning、multi-agent trust escalation。
- 只呈现防御性抽象，不复现可直接用于数据外传的 payload。

## 质量与发布门禁

- 每篇至少 4 幅独立 SVG（每幅有 title/desc、唯一 ID、独立文件）；图必须解释具体机制，不做重复装饰。
- 每篇有 evidence.json，区分 verified / derived / illustrative / unverified；所有公司指标标注“公司自述”。
- 相关代码示例有确定性测试；教学抽象不得冒充生产实现。
- MathML 仅用于确有数学价值的定义或推导；不为公式数量而堆砌公式。
- 单文件 HTML 离线可读；无 CDN、远程字体或外部 JS；支持键盘、移动端、打印和 reduced-motion。
- 静态测试、全量 pytest、build_site、validate_site，以及 1440 / 768 / 390 / 360px Chromium QA；交互必须真实点击验证。
- 草稿不进入线上。通过 PR CI、人工技术审查和浏览器 QA 后才改为 published；合并后核验 Pages 部署和 HTML / PDF 可访问性。
