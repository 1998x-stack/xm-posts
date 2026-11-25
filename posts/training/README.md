# 训练与对齐 / Training & Alignment

预训练、微调、对齐目标与优化策略的可验证拆解。

该目录包含本分类文章。添加新 Post 时创建 `posts/training/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 已发布论文解读

- [Understanding Score Centering](score-centering/index.html) — 从 training–inference mismatch 的 score drift 推导开始，覆盖 drift / signal 分解、Top-k tail reconstruction、bias 边界、GRPO group baseline 与 RSC 后续工作。二级主题：RL Post-training & Policy Optimization。

- [Understanding Knowledge Distillation](knowledge-distillation/index.html) — Hinton et al. (2015) 的 soft targets、温度缩放与 KL；延伸到 DistilBERT、TinyBERT、GKD、DeepSeek-R1 与扩散模型蒸馏。二级主题：Knowledge Distillation & Teacher–Student Transfer。

- [Understanding DPO](dpo/index.html) — Rafailov et al. (NeurIPS 2023)，隐式奖励、成对偏好、KL 正则化与离线对齐。

相关子主题：Preference Optimization / RLHF。DPO 属于训练与对齐，不另建同义的顶层类别。

- [Understanding Chinchilla](chinchilla/index.html) — Hoffmann et al. (NeurIPS 2022)：固定训练算力、参数/token 比、IsoFLOP 和三种 scaling-law 估计；属于 Pretraining → Scaling Laws / Compute-Optimal Training。

- [Understanding Checkpoint Optimization](checkpoint-optimization/index.html) — Young–Daly 最优检查点间隔、CheckFreq 两阶段异步快照、PyTorch DCP、FSDP / ZeRO / Megatron 分片恢复与持久化正确性。当前为草稿，需通过 CI 与浏览器 QA 后再发布。

- [Understanding GPT-1](gpt-1/index.html) — Radford et al. (2018)：自回归预训练、任务输入转换、联合微调与消融分析。

- [Understanding QLoRA](qlora/index.html) — Dettmers et al. (NeurIPS 2023)；NF4、Double Quantization、Paged Optimizers 与 MMLU 原论文证据。二级主题：PEFT / LoRA → Quantized Fine-tuning。

## 专题规划占位（非文章）

训练与对齐负责模型参数更新、教师—学生知识迁移与跨设备训练机制。知识蒸馏归本类；剪枝/量化等效率方法通过交叉标签关联；NCCL、GPU kernel 与底层网络通信性能归 `systems`。

- [Distributed Training](_topics/distributed-training/README.md)
- [Training Parallelism](_topics/training-parallelism/README.md)
- [Mixed Precision](_topics/mixed-precision/README.md)
- [Checkpointing](_topics/checkpointing/README.md)
- [Knowledge Distillation](_topics/knowledge-distillation/README.md)

上述 `_topics/` 是研究路线占位目录，正式文章仍遵循 `posts/training/<slug>/index.html`；只有 `content/posts.json` 中的 `published` 文章才会被发布。
## 2026-11-21 新增专题
- [Reward Hacking & Specification Gaming](./_topics/reward-hacking/README.md)
- [Supervised Fine-Tuning & Instruction Tuning](./sft/index.html)
- [Distributed Training](./_topics/distributed-training/README.md)：新增 DeepSpeed / ZeRO 深度解析。
- 关联文章：Checkpoint Optimization、SFT、Reward Hacking、DeepSpeed。
