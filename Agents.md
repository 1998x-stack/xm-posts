# Agent instructions

Canonical repository-wide agent instructions are maintained in [`AGENTS.md`](AGENTS.md). This file is a case-sensitive discoverability alias only; keep all substantive rules in the canonical file to prevent drift.

封面设计、按文章选择 SVG、禁止通用占位图及发布验收规则，统一遵循 canonical [`AGENTS.md`](AGENTS.md) 中的 **Card cover design contract**。

相关知识卡片（推荐文章）按 canonical [`AGENTS.md`](AGENTS.md) 的 **Related reading contract** 执行：新增已发布文章时维护 `content/reading_paths.json` 的学习顺序，由 `scripts/related_posts.py` 构建时生成每篇文末的 2–4 张（最多四张）卡片；仅关联真实已发布文章，优先前置知识、后续学习和跨领域机制，不强行推荐无关文章；验证文章链接、专属 SVG 封面、响应式和 Pages 部署状态。
