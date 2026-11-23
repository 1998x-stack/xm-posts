# 评测与复现 / Evaluation

实验证据、Benchmark 设计、基线公平性与可重复性。

该目录包含本分类文章。添加新 Post 时创建 `posts/evaluation/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## 二级专题

- **Classification Metrics & ROC Analysis**：ROC、AUC、排序指标、阈值工作点；首篇 [Understanding ROC-AUC](roc-auc/index.html)。
- **Imbalanced Classification & PR Analysis**：Precision-Recall、Average Precision、基率、固定误报预算与类别不平衡评测。

`_topics/` 为二级分类占位，不是正式文章；文章通过 `content/posts.json` 发布。
## 2026-11-21 新增专题
- [LLM-as-a-Judge & Judge Reliability](./_topics/llm-as-a-judge/README.md)
- 关联文章：LLM-as-a-Judge、Agent Evaluation。

## 2026-11-23 新增研究方向
- [Safety Evaluation & Risk Testing](_topics/safety-evaluations/README.md) — 构念效度、多轮风险模拟、评分器校准与统计报告；首篇 Anthropic 案例仍为 draft。
