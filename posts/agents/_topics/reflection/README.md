# Reflection, Self-Critique & Verbal Feedback

> 稳定 Topic ID：`agents/reflection`

## 收录范围

研究 Agent 如何将已经发生的输出或行动，与反馈信号进行比较，并把评价结果转成可执行修正或后续经验：

- Self-Critique / Self-Refine：模型内部反馈、定位问题与迭代修订；
- Externally Grounded Critique：搜索、编译器、单元测试、API 和环境反馈；
- Reflexion：Actor / Evaluator / Reflector / Episodic Memory 的跨轮次经验闭环；
- 反思停止条件、最佳候选保留、回归检测与预算管理；
- 反馈质量、评价器独立性、错误归因与记忆污染；
- Reflection 与 CoT、Self-Consistency、ReAct、Agent Memory、SFT / DPO / RL 的边界。

## 与相邻专题的边界

| Topic | 边界 |
|---|---|
| `reasoning/chain-of-thought` | CoT 描述单次生成中的中间推理；Reflection 进一步评价已有输出或轨迹并转成修正 |
| `reasoning/self-consistency` | Self-Consistency 聚合多条候选路径；Reflection 消费反馈改变候选或下一轮策略 |
| `agents/react` | ReAct 组织 Thought / Action / Observation；Reflection 读取轨迹与评价，提炼修正 |
| `agents/memory` | Memory 研究经验如何保存、组织和检索；Reflection 研究哪些反馈应写入，以及如何影响下一轮 |
| `training` | SFT / DPO / RL 通过训练信号改变参数；典型测试时 Reflection 改变输出、上下文或记忆而不更新权重 |

## 典型学习路径

Chain-of-Thought → Self-Consistency → ReAct → Reflection → Agent Memory

## 证据原则

优先引用原始论文与正式会议 / 期刊版本。将论文实验、综述观点、独立推导和教学模拟分开标注。报告指标时必须保留模型、数据集、评价协议和表格定位；内部自评不应被描述成独立真值。

Reflection 不构成新的一级分类；它是 Agents & Tool Use 中关于反馈、反思与经验更新的稳定二级主题。
