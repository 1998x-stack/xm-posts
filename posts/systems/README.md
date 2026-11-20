# 系统与 Kernel / Systems & Kernels

内存层级、GPU 算子、编译与系统性能分析。

该目录包含本分类文章。添加新 Post 时创建 `posts/systems/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

当前长文：[`flashattention/`](flashattention/index.html) — HBM/SRAM、Online Softmax 与 FlashAttention 1–4；细分主题 `Attention Kernels` 无需新增顶层分类。

## 专题规划占位（非文章）

`systems` 聚焦 GPU 内存层次、算子/编译、分布式通信与性能模型；服务端请求/队列调度归 `inference`，训练并行切分策略归 `training`。

- [GPU Architecture & Memory Hierarchy](_topics/gpu-memory/README.md)
- [Compiler & Kernel Optimization](_topics/compiler-kernel-optimization/README.md)
- [Distributed Communication](_topics/distributed-communication/README.md)
- [Performance Modeling](_topics/performance-modeling/README.md)

上述 `_topics/` 是研究路线占位目录，正式文章仍遵循 `posts/systems/<slug>/index.html`；只有 `content/posts.json` 中的 `published` 文章才会被发布。
