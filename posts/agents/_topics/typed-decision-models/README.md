# Typed Decision Models & Probabilistic Routing

本 Topic 研究把窄范围判断作为类型化、概率化接口交给软件消费的模型与工程模式，当前以 TypeSafe AI Jev / System One 为案例。

## 核心问题

- 如何设计封闭的答案空间：Choice、Score、Noul，以及版本化的 Box 扩展。
- 如何区分 top-option probability、confidence 与统计意义上的 calibration。
- 如何将概率与业务损失结合，计算 Bayes risk，并支持自动执行、拒绝和人工复核。
- 如何把决策模型接入 Agent / Router / Guardrail，同时让代码保留权限、审计和副作用控制。

## 分类边界

- 经典概率分类器本身归 classical-ml。
- ECE、Brier Score、风险—覆盖率与基准评测归 evaluation。
- 多步推理、搜索与验证归 reasoning。
- 本 Topic 关注类型化决策接口及其在 Agent 工作流中的位置，使用 Tags 和阅读路径关联相邻领域。

## 已登记文章

- [Understanding Jev：类型化概率决策模型](../../typed-decision-models/) — 从原语、概率校准和 Bayes risk 到 Agent 工程策略。

> 此 README 是 Topic 导航，不是独立文章；正式文章以 content/posts.json 为准。
