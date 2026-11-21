# 概率决策模型 / Probabilistic Decision Models

本分类研究如何把模型判断变成可审计、可校准、可执行的概率决策。关注的不只是某一个模型产品，而是一套横跨统计决策理论、模型接口、风险控制和软件系统的知识体系。

## 研究主线

1. **Typed Decision Models**：在调用时声明 State、问题类型和有限答案空间，返回 Choice、Score、Noul 等结构化概率结果。
2. **Decision Theory**：用 Bayes Risk、Expected Loss 和成本矩阵，把概率转化为动作。
3. **Calibration**：检验概率与真实频率是否匹配，理解 ECE、Brier Score 和子群体校准。
4. **Risk Control**：通过 Risk Budgeting、Learn Then Test 等方法，对部署策略的错误率进行约束。
5. **Selective Prediction**：在自动执行、拒绝、人工复核和按需推理之间分配计算与风险。
6. **Routing & Robustness**：研究模型路由、级联、输入变体、选项顺序、数据布局和偏差。

## 二级专题

- [Typed Decision Models & System One](_topics/typed-decision-models/README.md)
- [Cost-sensitive Decision Theory](_topics/cost-sensitive-decision-theory/README.md)
- [Probability Calibration](_topics/probability-calibration/README.md)
- [Risk Budgeting & Statistical Guarantees](_topics/risk-budgeting/README.md)
- [Selective Prediction & Abstention](_topics/selective-prediction/README.md)
- [Decision Routing & Delegation](_topics/decision-routing/README.md)
- [Robustness, Bias & Invariance](_topics/robustness-and-bias/README.md)

## 与相邻分类的边界

- 经典分类器的参数学习、训练目标与算法机制归 classical-ml。
- 通用 benchmark、指标设计、消融和可重复性归 evaluation。
- Agent 的环境观察、工具调用、规划和执行闭环归 agents。
- 本分类聚焦“如何做出可被软件消费的概率决策，以及如何约束决策风险”。

## 当前正式文章

- [Understanding Jev：类型化概率决策模型](typed-decision-models/) — 从 Choice、Score、Noul 到校准、Bayes Risk、LTT 与 Agent 集成。

> 本文件是分类导航；正式文章和发布状态以 content/posts.json 为唯一依据。
