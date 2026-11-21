# xm-posts 论文知识扩建：每批三篇

本文件将 2026-11-21 研究报告的每批 8 篇落实为 **3 篇一批、逐篇研究、逐篇构建、整批验收**。批次是编辑分组，不等于定时任务或绕过 CI 的自动合并。

## 第一批：LLM Serving

|顺序|文章|稳定一级/二级分类|论文|
|---|---|---|---|
|1|Continuous Batching / Orca|`inference/continuous-batching`|OSDI 2022|
|2|SGLang / RadixAttention|`inference/prefix-caching`|NeurIPS 2024|
|3|Sarathi-Serve|`inference/request-scheduling`|OSDI 2024|

对应目录为 `posts/inference/{continuous-batching,sglang-radixattention,sarathi-serve}/`。保持旧一级分类，不新增重复 Topic。将三篇串成 KV Cache → PagedAttention → Continuous Batching → SGLang → Sarathi-Serve 的知识路径。

## 接下来的建议批次（执行前先查主分支与现有 PR）

- 第二批：DistServe（`inference/prefill-decode-disaggregation`）、Mooncake（`inference/prefill-decode-disaggregation`）、FlashInfer（`systems/attention-kernels`）。
- 第三批：HNSW（`retrieval-rag/ann`）、DiskANN（`retrieval-rag/ann`）、ColBERTv2（`retrieval-rag/reranking`）。

## 每篇的串行质量门禁

1. 先精读论文正文、图题、附录、原始实现；核对版本、指标、数据集与实验；先写 `evidence.json`，严格区分论文结论、推导与 toy demo。
2. 按 `AGENTS.md` 与 `skills/olah-style-paper-posts/SKILL.md`：问题 → 直觉 → 机制 → 数学与维度 → 独立 SVG → 小型可运行实验 → 证据/局限。
3. 原生 MathML（可聚焦滚动区域）、独立可读且唯一 ID 的 SVG、离线/键盘/移动端/打印无缺陷、封面特异且可阅读。
4. 验证：`python skills/olah-style-paper-posts/scripts/validate.py <article>/index.html`、`python -m pytest -q`、`python scripts/build_site.py`、`python scripts/validate_site.py`。
5. 浏览器宽度 1440、768、390、360px，检查 MathML namespace、所有 SVG、Console 错误、链接、交互状态和 print；若无法执行应标记“未验证”。
6. 提交独立 PR，只有 CI 成功、审查差异、PDF 校验通过后才允许合并；合并后验证 GitHub Pages Job 和公开文章/PDF 可访问。不得把“提交”说成“部署”。

本文仅维护批次计划，质量要求仍以根 `AGENTS.md`、Canonical Skill 与 `docs/taxonomy.md` 为准。
