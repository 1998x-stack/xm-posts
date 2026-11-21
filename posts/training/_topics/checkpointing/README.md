# Checkpointing

> **专题规划 / Research topic** — 正式文章由 `content/posts.json` 管理；本 README 仅记录主题边界与后续研究路线。

- **一级分类**：`training`
- **二级主题**：`checkpointing`
- **研究范围**：训练状态快照、容错策略、保存间隔、异步 staging、分布式分片、resharding、持久化提交与恢复验证。
- **边界说明**：Training Checkpoint 解决故障后的训练续跑；Activation Checkpoint 通过反向传播重计算节省激活显存。两者有关联，但不是同一问题。
- **已构建草稿文章（待 CI 与浏览器验收）**：[Understanding Checkpoint Optimization](../../checkpoint-optimization/index.html) — Young–Daly、CheckFreq、PyTorch DCP、Megatron 与 DeepSpeed 的理论和工程链路。
- **后续研究路线**：Checkpoint Compression / Incremental Checkpointing、Fault Injection & Recovery Testing、Elastic Training、Checkpoint-aware Scheduling。
- **投稿位置**：`posts/training/<article-slug>/index.html`（不要将正式文章放到 `_topics/`）。
- **发布规则**：HTML、独立 SVG、`evidence.json`、可执行算例与 QA 全部通过后，再由 `content/posts.json` 将状态从 `draft` 改为 `published`。

此目录保留专题范围与研究路线，不作为站点文章或 RSS 条目发布。
