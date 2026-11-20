# Distributed Training

> **规划占位 / Planned topic** — 不是文章，也不代表已发表或已完成研究。

- **一级分类**：`training`（以 `content/categories.json` 为准）
- **研究范围**：数据并行与多机训练、模型状态分片、梯度归约、参数聚合、CPU/NVMe offload、TP/PP/Sequence Parallelism、检查点与集群训练稳定性。
- **代表性系统**：DeepSpeed / ZeRO、FSDP 与 Megatron 等；每篇文章应区分论文原始机制、当前软件 API 与具体硬件实验。
- **专题入口**：[Understanding DeepSpeed](../deepspeed/index.html)：从 16 bytes/parameter 账本推导 ZeRO Stage 1/2/3，并延伸到 Offload、3D 并行与 ZeRO++。
- **投稿位置**：`posts/training/<article-slug>/index.html`（不要将正式文章放到 `_topics/`）
- **发布规则**：先完成 HTML、独立 SVG、`evidence.json` 与 QA，再由 `content/posts.json` 控制 `draft` / `published`。

此目录仅保留专题规划，不作为站点文章或 RSS 条目发布。
