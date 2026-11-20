# 存储与索引 / Storage & Indexing

本领域讨论数据库和存储引擎：页式有序索引、LSM 写入路径、哈希/概率过滤结构、缓冲池、事务恢复与并发控制。

- 正式文章：[Understanding B+ Tree](b-plus-tree/index.html)，主题 `ordered-tree-indexes`。
- 与 `systems`（GPU Kernel / 编译器 / 通信）以及 `retrieval-rag`（向量近邻召回 / RAG）的边界不同。
- 来源：`content/categories.json` 定义稳定二级主题；`content/posts.json` 控制文章发布。占位 README 不发布。

## 二级主题规划（占位目录，不是文章）

- [Ordered Tree Indexes & B+ Trees](_topics/ordered-tree-indexes/README.md)
- [LSM Trees, SSTables & Compaction](_topics/lsm-write-path/README.md)
- [Hash Indexes & Probabilistic Filters](_topics/hash-and-probabilistic-indexes/README.md)
- [Pages, Buffer Pools & Storage Layout](_topics/pages-buffer-management/README.md)
- [Transactions, WAL & Recovery](_topics/transactions-recovery/README.md)
- [Concurrency, Latching & MVCC](_topics/concurrency-mvcc/README.md)
