# Autonomous Execution & Iterative Control

## 研究范围

研究 Agent 的外层执行控制：长周期任务拆解、跨轮次状态恢复、迭代预算、验证反馈、完成条件、停滞诊断与安全停止。

## 核心问题

1. 如何把长任务分解为单轮可完成、可验证的工作单元？
2. 如何区分短暂模型上下文与仓库、任务计划、测试和 Git 等持久状态？
3. 如何使用测试、类型检查和构建结果形成可靠的反馈信号？
4. 如何区分真正完成、模型自我声明完成、预算耗尽和需要人工接管？
5. 如何在多轮自动执行中限制权限、成本和不可逆操作？

## 代表性入口

- Ralph Loop：经典 Shell 进程循环与 Claude Code Stop Hook 的差异。
- Long-horizon coding agents：跨多轮任务规划与执行。
- Harness engineering：将模型、工具、状态、验证器和权限边界组织为可控系统。

## 分类边界

- ReAct：单次运行内部的思考、行动与观察。
- Software Engineering Agents & ACI：代码环境中的搜索、编辑与工具接口。
- Harness Engineering：完整的 Agent Runtime、权限、可观测性和维护治理。
- Context Engineering：每轮上下文如何选择、压缩和组织。
- Agent Memory：跨任务经验如何存储和复用。
- 本专题：执行器如何跨轮次调度、验证、持久化和终止。

本目录是研究占位，不是正式文章；正式文章应放在 `posts/agents/<slug>/index.html` 并在 `content/posts.json` 中登记。
