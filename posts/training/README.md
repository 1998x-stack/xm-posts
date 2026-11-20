# 训练与对齐 / Training & Alignment

预训练、微调、对齐目标与优化策略的可验证拆解。

该目录包含本分类文章。添加新 Post 时创建 `posts/training/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 已发布论文解读

- [Understanding DPO](dpo/index.html) — Rafailov et al. (NeurIPS 2023)，隐式奖励、成对偏好、KL 正则化与离线对齐。

相关子主题：Preference Optimization / RLHF。DPO 属于训练与对齐，不另建同义的顶层类别。

- [Understanding Chinchilla](chinchilla/index.html) — Hoffmann et al. (NeurIPS 2022)：固定训练算力、参数/token 比、IsoFLOP 和三种 scaling-law 估计；属于 Pretraining → Scaling Laws / Compute-Optimal Training。

- [Understanding GPT-1](gpt-1/index.html) — Radford et al. (2018)：自回归预训练、任务输入转换、联合微调与消融分析。

- [Understanding QLoRA](qlora/index.html) — Dettmers et al. (NeurIPS 2023)；NF4、Double Quantization、Paged Optimizers 与 MMLU 原论文证据。二级主题：PEFT / LoRA → Quantized Fine-tuning。
