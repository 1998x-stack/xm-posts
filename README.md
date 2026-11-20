# xm-posts

**从直觉到机制，从公式到证据。** 一个面向大学生、研究生与工程实践者的机器学习、LLM 与系统技术知识库。通过原创 SVG 图解、循序渐进的数学解释、可交互示例与论文证据，回答“模型为什么这样工作”。

[![Validate & publish](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml/badge.svg)](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml)

[阅读网站](https://1998x-stack.github.io/xm-posts/) · [知识地图](https://1998x-stack.github.io/xm-posts/topics/) · [文章归档](https://1998x-stack.github.io/xm-posts/archive/) · [RSS 订阅](https://1998x-stack.github.io/xm-posts/feed.xml) · [贡献指南](CONTRIBUTING.md)

> **发布状态**：源码以仓库 `main` 分支为准。GitHub Actions 在 PR 上执行验证，只有对 `main` 的成功部署才会更新 GitHub Pages。工作流通过不等于线上已更新；若页面尚未变化，请先检查 [Actions](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml)。

## 这个项目提供什么？

- **读得懂**：从具体问题和直观机制切入，再解释公式、模型结构与工程边界。
- **看得见**：以文章专属的 SVG 图解呈现信息流、张量操作和算法步骤，不使用通用占位封面。
- **查得到**：区分原论文结果、教学算例、现代变体与独立推导；重要事实可追溯到论文及 `evidence.json`。
- **动得手**：适当提供原生交互和可运行的最小代码，不把教学演示误称为完整论文复现。
- **持续更新**：文章目录、分类、搜索索引、RSS 与 Sitemap 都由同一份发布清单自动生成。

文章优先服务于**大学生 / 研究生理解水平**：解释术语、给出变量定义和具体算例，再逐层深入。

## 从哪里开始阅读？

| 入口 | 用途 |
| --- | --- |
| [首页](https://1998x-stack.github.io/xm-posts/) | 精选文章、跨领域学习路径、文章索引与搜索 |
| [知识地图](https://1998x-stack.github.io/xm-posts/topics/) | 从一级领域进入二级主题，查看已发布与规划中的研究方向 |
| [文章归档](https://1998x-stack.github.io/xm-posts/archive/) | 查看所有正式发布的文章 |
| [RSS Feed](https://1998x-stack.github.io/xm-posts/feed.xml) | 在 RSS 阅读器中订阅文章与更新 |

**推荐阅读起点**（精选，不是完整清单）：

| 学习方向 | 先读 | 接着读 |
| --- | --- | --- |
| 经典机器学习 | [Logistic Regression](posts/classical-ml/logistic-regression/index.html) | [K-Means](posts/classical-ml/k-means/index.html) · [SVM](posts/classical-ml/svm/index.html) |
| 神经网络架构 | [ResNet](posts/architectures/resnet/index.html) | [Transformer](posts/architectures/transformer/index.html) · [Multi-Head Attention](posts/architectures/multi-head-attention/index.html) |
| 训练与优化 | [SGD](posts/foundations/sgd/index.html) | [AdamW](posts/foundations/adamw/index.html) · [LoRA](posts/training/lora/index.html) · [Knowledge Distillation](posts/training/knowledge-distillation/index.html) |
| 强化学习 | [Bellman Equations](posts/reinforcement-learning/bellman-equations/index.html) | [MCTS](posts/reinforcement-learning/mcts/index.html) |
| Agent 工程化 | [ReAct](posts/agents/react/index.html) | [SWE-agent](posts/agents/swe-agent/index.html) · [Agent Memory](posts/agents/agent-memory-components/index.html) · [Harness Engineering](posts/agents/harness-engineering/index.html) |
| LLM 推理与系统 | [KV Cache](posts/inference/kv-cache/index.html) | [GQA](posts/architectures/gqa/index.html) · [FlashAttention](posts/systems/flashattention/index.html) |

**完整且权威的文章清单是 [`content/posts.json`](content/posts.json)**。新文章通过发布门禁后自动进入网站归档与 RSS；不要根据 README 的示例表格统计文章数量。

## 分类与知识地图

内容按 **一级领域 → 二级主题 → 文章** 组织。主要方向包括：

- **Foundations / Classical ML**：数学、优化、表示学习、分词与经典机器学习。
- **Architectures**：CNN、RNN、Transformer、Attention、MoE、SSM 等模型结构。
- **Training / Reinforcement Learning**：预训练、知识蒸馏与教师—学生迁移、对齐、PEFT、价值与策略学习及搜索。
- **Reasoning / Agents & Tool Use**：推理策略、工具调用、规划、Agent Memory、Harness Engineering 与可验证智能体工作流。
- **Retrieval & RAG / Inference**：向量检索、增强生成、解码、KV Cache、请求调度与 Serving。
- **Systems / Datasets / Evaluation / Multimodal**：算子与 GPU、数据、评测和多模态。
- **Storage & Indexing**：B+ Tree、存储页、LSM、事务与索引结构。

以上仅是导航概览。**分类、稳定 slug 和二级主题的唯一数据源是 [`content/categories.json`](content/categories.json)**；每篇文章在 `content/posts.json` 中只能有一个主 `category` 和 `topic`，跨领域关系使用 `tags`。详细约定见 [`docs/taxonomy.md`](docs/taxonomy.md)。

`_topics/` 下的 README 是规划占位，不会作为正式文章发布。分类或文章 slug 一旦对外公开，原则上保持稳定。

## RSS：订阅与更新语义

**订阅地址：<https://1998x-stack.github.io/xm-posts/feed.xml>**

复制此链接到支持 RSS 2.0 的阅读器即可订阅。站点导航提供显式入口；首页、知识地图、归档及正式文章页提供 RSS 自动发现链接。

RSS 由 `scripts/build_site.py` 根据文章注册表**构建时自动生成**，不人工维护 XML：

1. **发布门禁**：只有 `status: published` 进入 RSS；草稿与规划目录排除。
2. **稳定身份**：每个条目的 `guid` 和 `link` 都是永久文章 URL。修订同一篇文章不会生成新的条目 ID。
3. **日期精度**：`pubDate` 使用 `published` 的日期；由于注册表没有精确时刻，按 UTC 当日 **00:00** 序列化，这不是实际发表时间。`dcterms:modified` 使用 `updated` 的 `YYYY-MM-DD` 日期，并优先按更新日期排序。
4. **标准元信息**：包含站点语言、`atom:link rel="self"`、摘要、一级分类及二级主题；条目摘要不替代完整网页。
5. **兼容性**：不随意更改 `feed.xml` 地址、文章路径或 `guid`。阅读器是否重新提示已订阅文章的修订取决于客户端实现。

查看 [RSS 技术契约与故障排查](docs/rss.md)。单独运行 RSS 测试：

```bash
python -m pytest -q tests/test_rss.py
```

## 本地开发

需要 **Python 3.11+**。静态构建只依赖 Python 标准库；验证依赖 `requirements-dev.txt` 和 Chromium。

```bash
git clone https://github.com/1998x-stack/xm-posts.git
cd xm-posts
python -m pip install -r requirements-dev.txt
python -m playwright install chromium

# 构建静态站点（输出到 _site/）
python scripts/build_site.py

# 运行完整校验
python -m pytest -q
python scripts/validate_site.py
python scripts/sync_skills.py --check

# 本地预览
cd _site
python -m http.server 8000
```

在浏览器打开 <http://localhost:8000/>。生产环境部署在 `/xm-posts/` 子路径；内部导航使用相对链接，`--base-url` 控制输出的规范 URL、RSS 和 Sitemap：

```bash
python scripts/build_site.py --base-url https://example.org/learning/
```

不要提交 `_site/`：它是可重复生成的构建产物。

## 新增与发布文章

1. 从 `content/categories.json` 选择已登记的 `category` 和 `topic`，优先复用现有主题，再创建草稿：

   ```bash
   python scripts/new_post.py inference understanding-kv-cache \
     --topic kv-cache \
     --title 'Understanding KV Cache' \
     --subtitle '为什么缓存能减少重复计算？' \
     --paper 'https://arxiv.org/abs/...'
   ```

2. 按 [`AGENTS.md`](AGENTS.md) 与 [`olah-style-paper-posts`](skills/olah-style-paper-posts/SKILL.md) 编写：独立 HTML、清晰的原创 SVG、原生 MathML、可追溯的 `evidence.json` 和必要的数值或浏览器验证。
3. 在 `content/posts.json` 完善 `summary`、`tags`、`published`、`updated`、`reading_minutes`、`paper`、`cover.src`、`cover.caption`。**完成质量检查后**，才允许把 `status` 设为 `published`。
4. 运行构建、pytest、站点校验和浏览器 QA（桌面、平板、手机与实际交互），通过 PR 提交。PR 只验证，**不会部署**。
5. PR 审核通过并合并到 `main` 后，工作流重新构建并发布；确认部署 Job 成功且生产网页和 RSS 可访问，才能称为“已上线”。

每篇文章的封面必须选用自己解释核心机制的 SVG；禁止统一的 “Observe → Derive → Verify” 占位图。文章与公式编写标准见 [`docs/editorial.md`](docs/editorial.md)、[`AGENTS.md`](AGENTS.md)。

## 仓库结构

```text
xm-posts/
├── README.md                      # 项目入口、订阅与开发指南
├── AGENTS.md                      # Agent 协作与质量门禁
├── content/
│   ├── categories.json            # 分类与稳定二级主题
│   └── posts.json                 # 文章元数据、状态、日期与封面
├── posts/<category>/<slug>/       # index.html、assets/*.svg、evidence.json
├── site/assets/                   # 网站共享样式、脚本和图标
├── scripts/                       # 构建、校验、新建文章、Skill 同步
├── tests/                         # 数学核验、文章、站点、RSS 测试
├── docs/                          # 架构、分类、编辑、RSS 文档
├── skills/olah-style-paper-posts/ # Canonical Skill
├── .claude/skills/                # Agent Skill 镜像
├── .pi/skills/
├── .agent/skills/
├── .opencode/skills/
├── .github/workflows/publish.yml  # PR 验证与 main 部署
└── _site/                         # 本地生成，禁止入库

```

只修改 `skills/olah-style-paper-posts/` 正本；更新后执行 `python scripts/sync_skills.py` 同步四份镜像，最后以 `--check` 校验。完整技术说明见 [`docs/architecture.md`](docs/architecture.md)。

## 每篇文章下载 PDF

网站上每篇正式发布的 Post 右下角都有一个轻量的 **「下载 PDF」** 按钮，点击后直接下载 `xm-posts-<slug>.pdf`。在线阅读的原始 Olah 风格排版不变；PDF 由 Chromium 按 HTML 原有 CSS（含 `@media print`）排版，尽可能保持 SVG、数学公式、配色和代码内容。打印为 A4 时会自然分页；可交互实验在 PDF 中保留生成时的静态状态，操作仍需使用 HTML 版。

- 直接文件地址：`/xm-posts/posts/<category>/<slug>/article.pdf`。
- **自动生成**：仅处理 `content/posts.json` 中 `published` 的文章；新 Post 正式发布后不需要手动上传 PDF，也不需要逐篇修改 HTML。
- **设计原则**：下载入口是小型固定浮动控件，不挤压文章内容；打印/导出的 PDF 不显示按钮和网站导航，不改变正文 SVG 和数学表达式的源文件。
- **质量检查**：部署前要求 PDF 可解析、有正文文本、图片资源加载成功，并运行站点链接检查。极宽公式、长代码和跨页图表仍应按文章单独抽查。

本地生成（先安装 `requirements-dev.txt` 和 Playwright Chromium；Linux CI 还安装 Noto CJK 与 STIX 字体）：

```bash
python scripts/build_site.py
python scripts/render_pdfs.py
python scripts/validate_site.py
```

只检查一篇文章时，先构建再运行 `python scripts/render_pdfs.py --only transformer`；使用 `--force` 可以忽略缓存重新渲染，`--cache-dir` 可以指定独立缓存目录。正式发布始终向 `_site/` 放入**所有**已发布文章的 PDF，但只对缓存未命中的文章执行 Chromium 渲染。不要提交自动生成的 `_site/`、`.pdf-cache/` 或 `article.pdf`。

**增量 PDF 缓存机制：**

- GitHub Actions 用 `actions/cache` 跨运行恢复 `.pdf-cache/`（包含 manifest 和 PDF 文件）；缓存丢失并不影响正确性，回退到完整渲染。
- 内容指纹覆盖**构建后的 HTML**、文章资源、页面引用的本地跨文章图片、链接 CSS 及 CSS 依赖、渲染器与依赖版本、实际安装的中文/数学字体版本以及文章公开 URL。因此，编辑首页/归档页通常不触发 PDF 重建，更新打印样式或相关 SVG 会触发受影响文章重建。
- 命中缓存仍校验 PDF SHA-256、文件大小、页数、正文可检索性，并向本次构建的 HTML 注入原有轻量下载按钮；校验失败自动重渲染。
- 每个完整构建清除缓存中已取消发布的文章；`--only` 不清理其他文章。只有最终站点校验成功后才尝试保存 GitHub Actions 缓存。
- 工作流日志中的 `PDF CACHED` / `PDF RENDERED` 和末尾 `cached` / `rendered` 数字可以确认命中率。首次构建仍需渲染所有文章；缓存命中不能替代实际浏览器 QA。

## GitHub Pages 部署与排查

[Validate & publish xm-posts](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml) 在 PR 上完成测试与浏览器 QA，在 `main` push 后部署经过验证的 `_site/` Artifact。

如果 GitHub Pages 尚未启用且自动初始化失败，请由管理员在 **Settings → Pages → Build and deployment → Source → GitHub Actions** 设置发布源，并重新运行工作流。实际部署以 **Publish GitHub Pages Job 成功 + 公开网址可访问** 为准。

若看到“已提交但网页或 RSS 未变化”，先检查提交是否已在 `main`，再核对 CI 与部署 Job，最后排查浏览器、CDN 与 RSS 阅读器缓存。不要将本地构建成功误认为线上部署成功。

## 贡献、来源与版权边界

协作前请阅读 [`CONTRIBUTING.md`](CONTRIBUTING.md)、[`AGENTS.md`](AGENTS.md) 和 [`docs/editorial.md`](docs/editorial.md)。

项目借鉴 [Christopher Olah](https://colah.github.io/) 与 [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) 的**教学组织方式**，不是其文字、代码或插图的复制品。实验指标须标明论文、模型版本、数据集、实验设置和出处，教学简化不能冒充论文结论。

**许可注意**：不同引用来源可能具有不同的许可条款；未经过核实，不应推断论文图像或第三方代码可自由重新分发。


## 文章索引与归档分页

为避免随着文章数量增加而一次性渲染大量 SVG 缩略图，首页索引每页只创建 **8 张**文章卡片；点击页码、搜索或按研究领域筛选时，通过构建生成的轻量 `posts.json` 检索完整已发布文章，再只创建当前页的 DOM/图片。不开启 JavaScript 时，首页仍展示首批文章并保留归档入口。

时间归档按 **16 篇/页** 在构建时生成独立 HTML：第一页为 `/archive/`，后续为 `/archive/page/2/`、`/archive/page/3/` 等。普通链接、浏览器返回、SEO canonical、站点地图及无 JavaScript 浏览都可正常工作。原有缩略图均为文章专属 SVG，保留 lazy loading；其他分页的图片不会进入当前页面 HTML。该规范与对应测试见 `AGENTS.md`、`tests/test_site.py`、`scripts/browser_check_site.py`。


## CI 加速与性能报告

`.github/workflows/publish.yml` 仍执行完整的 pytest、SVG 审计、源文章与站点检查、所有文章的 Playwright 质量检查、专项交互检查、PDF 生成/完整性校验以及部署验收。加速首先来自**复用 Chromium 与受控并行**，而不是减少测试内容：

- 运行 `python scripts/browser_check_all.py --workers 2`：每个 Worker 使用一个 Chromium，覆盖所有已发布文章的桌面、平板、390px/360px、数学公式、SVG、交互和打印检查；失败仍会阻止发布。资源紧张时可用 `--workers 1` 完整串行复验。
- `scripts/ci_metrics.py` 在每个 CI Job 的 Summary 记录各项测试耗时、PDF 缓存命中/重渲染数、QA 覆盖文章数量和构建包大小；原始指标与截图位于 `reports/` Artifact。缓存失效、时间数据缺失会明确显示，不会伪造优化比例。
- **计时范围**：Job 内计时不含 GitHub Runner 排队和独立 Pages 部署时间。评估真正提速时请比较多次暖缓存成功部署，不能只使用首次冷缓存数据。
