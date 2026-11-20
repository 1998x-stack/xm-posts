# Imitation Learning & Learning from Demonstrations

本专题研究智能体如何从人类、专家控制器或高质量策略的示范中学习行为。它位于强化学习分类下，是为了与现有策略学习文章共享阅读路径；**这不表示模仿学习在概念上是强化学习的子集**。

## 核心问题

- 专家状态—动作数据如何转化为策略？
- 为什么行为克隆会受到协变量偏移影响？
- DAgger 如何利用学习者 rollout 和专家纠错扩展数据集？
- IRL / MaxEnt IRL 如何从行为推断奖励？
- GAIL 如何匹配专家与学习者的占用分布？
- Diffusion Policy 如何表达多模态、连续的动作序列？

## 正式文章

- [Understanding Imitation Learning](../imitation-learning/index.html)

## 分类边界

- 与强化学习分类中的 reward-driven policy optimization 互补，但监督信号不同。
- 与训练分类中的 RLHF / DPO 相邻，但逐时刻动作示范、偏好比较和奖励反馈不是同一种监督。
- Diffusion Policy 属于生成式策略表示；它可用专家示范训练，不应被误解为与 BC、DAgger 同层级的独立监督信号。
