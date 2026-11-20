# 查询理解、检索与 RAG / Query Understanding, Retrieval & RAG

本分类研究从用户信息需求理解到有依据回答的完整链路：Query Understanding、查询转换、向量表示、ANN、Reranking、RAG、Grounding 与 Hybrid Search。

## 已发布文章

- [Understanding Query Understanding](query-understanding/index.html) — 意图识别、语义解析、查询重写/扩展/分解、多轮澄清与 Agent 路由。

## 专题占位

- [Embedding Retrieval](_topics/embedding-retrieval/README.md) — 研究规划占位；尚非正式 Post。
- [ANN](_topics/ann/README.md) — 研究规划占位；尚非正式 Post。
- [Reranking](_topics/reranking/README.md) — 研究规划占位；尚非正式 Post。
- [RAG](_topics/rag/README.md) — 研究规划占位；尚非正式 Post。
- [Grounding](_topics/grounding/README.md) — 研究规划占位；尚非正式 Post。
- [Hybrid Search](_topics/hybrid-search/README.md) — 研究规划占位；尚非正式 Post。

## 分类边界与发布约定

- `foundations` 负责通用 Embedding 的训练与数学机制；这里专注 Embedding 在检索系统中的召回、索引和评测。
- `agents` 负责工具使用、规划与行动闭环；Query Understanding 在此分类中负责生成检索语义表示，工具执行权限仍归 Agent 执行层。
- 正式文章创建于 `posts/retrieval-rag/<slug>/index.html`，与独立 `assets/*.svg`、`evidence.json` 同目录，随后在 `content/posts.json` 登记。
- `_topics/` 内仅有 README 占位，不注册假文章、不提交空 HTML；`draft` 不进入首页、分类列表、RSS 或 Sitemap。
