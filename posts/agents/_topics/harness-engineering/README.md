# Harness Engineering

本专题研究让基础模型在真实软件与工具环境中持续执行任务的运行时系统：如何组织 Agent Loop、上下文、工具、项目记忆、任务状态、安全权限、可观测性、失败归因、验证和维护治理。

## 专题边界

- **归入本专题：** Agent Runtime / Harness、长任务执行、跨上下文交接、工具与执行环境集成、独立评估器、权限与沙箱、Agent 可观测性、验证协议、维护熵治理。
- **与 ReAct 的边界：** ReAct 主要解释推理—行动—观察循环；Harness Engineering 研究如何把循环放进完整、可恢复、可验证的运行时。
- **与 SWE-agent / ACI 的边界：** ACI 关注模型如何查看和操作计算机；Harness 还包括上下文、状态、权限、编排、验证和治理。
- **与 Agent Memory 的边界：** Memory 关注知识如何保存、纠错与检索；Harness 将记忆作为运行时的一项能力进行调度。
- **与 Agent Evaluation 的边界：** Evaluation harness 负责测量；Agent harness 负责让模型执行。两者可以协同，但不是同一个对象。

## 建议学习顺序

1. ReAct：理解最小行动闭环。
2. SWE-agent：理解面向模型的 ACI。
3. Agent Memory：理解跨会话知识管理。
4. Harness Engineering：将工具、上下文、状态、安全和验证组合为完整运行时。

## 核心参考

- OpenAI, *Harness engineering: leveraging Codex in an agent-first world* (2026-02-11).
- Anthropic, *Effective harnesses for long-running agents* (2025-11-26).
- Anthropic, *Harness design for long-running application development* (2026-03-24).
- Zhong & Zhu, *AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents* (arXiv:2605.13357).
- Barbaste et al., *Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents* (arXiv:2609.00006).

专题文章是研究性工程综述；新增文章不改变已有 topic slug 或历史文章路径。
