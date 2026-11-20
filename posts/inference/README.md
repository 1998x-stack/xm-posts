# 推理与 Serving / Inference & Serving

专注自回归生成、KV Cache 的生命周期、缓存共享与内存分配、批处理策略、低延迟和高吞吐在线服务。

## 已发布文章

- [Understanding KV Cache](kv-cache/index.html)：以因果 Attention 为起点，深入 Prefill、Decode、KV 内存公式、MHA/GQA/MQA、PagedAttention、Prefix Caching，包含原创机制图、计算器、证据账本和纯 Python 数值校验。
  
  - [论文与工程证据](kv-cache/evidence.json)
  - [纯 Python 教学示例](kv-cache/mini_kv_cache.py)

## 分类边界

本分类解释端到端推理请求路径与 Serving；GPU kernel 优化与低层内存访问细节归在 `systems`。现有 `inference` 已能够容纳 KV Cache，无须为单篇文章新增一级分类。

后续主题：PagedAttention 详解、连续批处理、Prefix Caching、KV 量化/Offloading、长上下文评测。

发布依据：`content/categories.json` 定义分类；`content/posts.json` 定义正式文章。草稿不会进入站点，`README.md` 不作为文章发布。

## 专题规划占位（非文章）

`inference` 管理请求生命周期、KV Cache、Prefill/Decode、动态 batch、调度及性能指标（TTFT、TPOT、吞吐与延迟）；kernel 和编译细节归 `systems`。

- [Request Scheduling](_topics/request-scheduling/README.md)
- [Continuous Batching](_topics/continuous-batching/README.md)
- [Prefix Caching](_topics/prefix-caching/README.md)
- [Speculative Decoding](_topics/speculative-decoding/README.md)
- [Prefill / Decode Disaggregation](_topics/prefill-decode-disaggregation/README.md)

上述 `_topics/` 是研究路线占位目录，正式文章仍遵循 `posts/inference/<slug>/index.html`；只有 `content/posts.json` 中的 `published` 文章才会被发布。
