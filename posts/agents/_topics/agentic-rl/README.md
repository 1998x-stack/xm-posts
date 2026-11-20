# Agentic Reinforcement Learning

## 研究定位

Agentic RL 研究如何通过环境交互与强化学习，让语言模型智能体学习多轮、长程、带工具使用的决策策略。重点不是“如何写一个 Agent Prompt”，而是如何把任务、动作、观察、奖励、轨迹和策略更新组成可训练、可评测的闭环。

## 主要问题

- 从单轮 completion reward 转向多轮 trajectory reward。
- 在部分可观测环境中使用历史、记忆或 belief 形成决策。
- 区分模型生成的 reasoning/action token 与环境返回的 observation。
- 解决长程任务中的稀疏奖励、信用分配和探索问题。
- 设计任务课程、奖励塑形、环境稳定性与离线/在线数据混合。
- 处理异步 rollout、工具延迟、策略版本滞后和训练吞吐。

## 与相邻专题的边界

- **ReAct**：解释 Thought / Action / Observation 的交互组织方式；原始 ReAct 不要求通过 RL 更新策略。
- **Tool Calling**：解释模型如何生成结构化工具调用；不等同于环境级策略学习。
- **Agent Planning**：关注任务分解与行动计划；Agentic RL 关注如何从结果中学习改进决策策略。
- **Agent Memory**：关注跨步骤或跨会话信息保存；在 Agentic RL 中可作为策略状态的一部分。
- **Reinforcement Learning**：提供 MDP、Policy Gradient、GAE、PPO、探索等算法基础。
- **Training / GRPO**：提供 LLM 后训练的优化目标；Agentic RL 将其扩展到多轮环境轨迹和工具反馈。

## 推荐先修路线

1. Bellman Equations → REINFORCE → GAE → PPO
2. GRPO → ReAct → Agentic RL
3. Agentic RL → SWE-agent / Agent Evaluation / Agent Memory

## 研究阅读

- Agentic RL Survey, TMLR 2026
- AgentGym-RL, ICLR 2026
- WebRL, ICLR 2025
- Agent Lightning, 2025
- SOAR, ACL 2026
- Demystifying RL for Long-Horizon Tool-Using Agents, Findings of EMNLP 2026

本目录是正式 topic 的研究说明；具体文章以同级正式 Post 与 `content/posts.json` 为准。
