# LLM-as-a-Judge & Judge Reliability

本专题研究如何将大语言模型用作评价器，以及如何证明这个评价器值得信任。

## 收录范围

- **任务形态**：Pointwise scoring、Pairwise comparison、Listwise ranking、Critique / rubric scoring、Verifier。
- **评价设计**：任务定义、评价维度、评分锚点、证据要求、结构化输出与聚合。
- **可靠性**：Human–judge agreement、inter-rater reliability、重复运行稳定性、位置交换与风格扰动。
- **偏差与校准**：Position / verbosity / self-preference bias、score calibration、human-anchored correction。
- **Meta-evaluation**：JudgeBench、RewardBench 等评审器基准；事实与逻辑验证、鲁棒性、成本和可复现性。

## 与邻近专题的边界

- Agent 的工具使用成功率、轨迹质量和端到端任务完成率，主归 `agents/agent-evaluation`。
- 人类偏好标签用于 Reward Model、RLHF、DPO 或 GRPO 训练时，训练目标主归 `training`；评审器如何生成/验证标签仍归本专题。
- ROC-AUC、PR、相关系数和一致性统计是评估工具，不替代对评审目标与标注协议的定义。

## 阅读顺序

1. 先明确任务、rubric 与评价单位。
2. 比较 pointwise、pairwise 和 listwise 评审方式。
3. 审计位置偏差、稳定性与人工一致性。
4. 用独立 benchmark 和人工校准集做 meta-evaluation。

正式文章通过 `content/posts.json` 发布；本 README 只定义专题边界，不是文章。
