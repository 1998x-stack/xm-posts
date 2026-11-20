# 强化学习 / Reinforcement Learning

从环境反馈、信用分配与值函数到策略优化，系统解释 Policy Gradient、Actor–Critic、GAE、TRPO、PPO 及其与 LLM 偏好对齐的联系。

## 已发布
- [Understanding NoisyNet](noisynet/index.html)：可学习的参数空间噪声、Factorised Gaussian Noise、DQN/Dueling/A3C 采样时序与 Atari-57 证据。
- [Understanding MCTS](mcts/index.html)：UCT 树搜索、四阶段模拟、探索系数与 PUCT 对比。
- [Understanding AlphaGo](alphago/index.html)：2016 Nature 原论文、监督/强化策略、价值网络、APV-MCTS、rollout 与异步搜索；另辨析 AlphaGo Lee / Zero。
- [Understanding DDPG](ddpg/index.html)：连续动作、确定性策略梯度、Off-policy Replay 与双目标网络。
- [Understanding SAC](sac/index.html)：最大熵离策略 Actor–Critic、经验回放、双 Q、tanh 高斯策略、自动温度与版本分辨。
- [Understanding DQN](dqn/index.html)：贝尔曼自举、经验回放、目标网络、Atari 架构与论文证据。
- [Understanding PPO](ppo/index.html)：为什么用 clipped surrogate、如何估计优势以及两种 KL 的区别。

后续可拓展 REINFORCE、Double DQN、Dueling DQN、DDPG、TD3、TRPO、RLHF 的具体算法。所有文章须具有 `index.html`、`assets/*.svg`、`evidence.json`，并在 `content/posts.json` 登记；草稿不会发布到 GitHub Pages。
