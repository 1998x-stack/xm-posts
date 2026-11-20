# xm-posts

**深度学习论文的图解实验室。** 从读者真正遇到的困惑出发，用原创机制图、可核验的公式、论文证据和可运行的最小代码，拆解经典架构与 LLM 系统技术。

[![Build & Pages](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml/badge.svg)](https://github.com/1998x-stack/xm-posts/actions/workflows/publish.yml) · [网站](https://1998x-stack.github.io/xm-posts/) · [文章归档](https://1998x-stack.github.io/xm-posts/archive/) · [RSS](https://1998x-stack.github.io/xm-posts/feed.xml) · [源 Skill](https://github.com/1998x-stack/Olah-style-posts)

> 发布源：`main` → GitHub Actions 校验与构建 → `_site/` artifact → GitHub Pages。公开网址需要仓库 Pages 功能首次启用且工作流成功；见 [启用说明](#github-pages-与持续部署)。

## 已发布的长文

| Post | 解释的问题 | 文章源码 | 核心资料 |
|---|---|---|---|
| **Understanding ResNet** | 网络越深，为什么训练反而可能更难？ | [`posts/architectures/resnet/`](posts/architectures/resnet/index.html) | [He et al.](https://arxiv.org/abs/1512.03385) |
| **Understanding Transformer** | 为什么用 Self-Attention 替代循环结构？ | [`posts/architectures/transformer/`](posts/architectures/transformer/index.html) | [Vaswani et al.](https://arxiv.org/abs/1706.03762) |
| **Understanding SVM** | 为什么分对了仍需最大间隔？ | [`posts/classical-ml/svm/`](posts/classical-ml/svm/index.html) | [Cortes & Vapnik (1995)](https://doi.org/10.1007/BF00994018) |

ResNet 具有 11 节解读与 10 幅独立 SVG；Transformer 具有 16 节解读与 13 幅独立 SVG，另有最小 PyTorch Attention 示例；SVM 具有 12 节机制推导、6 幅独立 SVG、可调 RBF 相似度矩阵和纯 Python 一维解析示例。文章在发布前经过静态内容核验、浏览器布局与交互检查；教学简化、原论文和后续变体需明确区分。

## 内容分类

| 分类 | 路径 | 范围 |
|---|---|---|
| 基础理论 | `posts/foundations/` | 表示、优化、数学直觉 |
| **经典机器学习** | `posts/classical-ml/` | SVM、核方法、线性与树模型 |
| **模型架构** | `posts/architectures/` | ResNet、Transformer、状态空间模型 |
| 训练与对齐 | `posts/training/` | 预训练、微调、偏好对齐 |
| 推理与 Serving | `posts/inference/` | KV Cache、Decode、在线 Serving |
| 系统与 Kernel | `posts/systems/` | GPU、算子、并行与性能分析 |
| 多模态 | `posts/multimodal/` | Vision/Audio/Language 与跨模态交互 |
| 评测与复现 | `posts/evaluation/` | Benchmark、消融、复现协议 |

各类别均有 `README.md` 占位；占位**不会作为文章上线**。`content/categories.json` 是分类单一数据源，`content/posts.json` 是文章元数据和发布状态的单一数据源。增加新文章不用手动编辑首页、Sitemap 或 RSS。

## 仓库结构

```text
xm-posts/
├── README.md                     # 项目入口、运行与部署说明
├── AGENTS.md                     # 各类编码 Agent 的协作契约
├── content/
│   ├── categories.json           # 分类元数据
│   └── posts.json                # 单一文章注册表；draft / published
├── posts/
│   ├── classical-ml/svm/          # SVM: HTML、SVG、代码与证据
│   ├── architectures/
│   │   ├── resnet/
│   │   │   ├── index.html
│   │   │   ├── assets/*.svg
│   │   │   └── evidence.json
│   │   └── transformer/
│   │       ├── index.html
│   │       ├── assets/*.svg
│   │       ├── mini_attention.py
│   │       └── evidence.json
│   └── {foundations,training,inference,systems,multimodal,evaluation}/
│       └── README.md             # 占位与投稿约定，不发布
├── skills/olah-style-paper-posts/ # Skill 正本；SKILL / references / assets / scripts
├── .claude/skills/olah-style-paper-posts/  # 完整 Skill 镜像
├── .pi/skills/olah-style-paper-posts/      # 完整 Skill 镜像
├── .agent/skills/olah-style-paper-posts/   # 完整 Skill 镜像
├── .opencode/skills/olah-style-paper-posts/# 完整 Skill 镜像
├── site/assets/                  # 首页及分类页面的 CSS / JS / SVG
├── scripts/
│   ├── new_post.py               # 新建 draft、注册目录与元数据
│   ├── build_site.py             # 生成 _site/、分类/归档/索引/RSS/Sitemap
│   ├── validate_site.py          # 校验文章、链接、发布排除与 SVG
│   └── sync_skills.py            # 同步四份 Skill，支持 --check
├── tests/test_site.py
├── docs/
│   ├── architecture.md           # 站点与发布架构
│   └── editorial.md              # 论文解读、图示与证据标准
├── .github/workflows/publish.yml # PR 验证；main 自动部署 GitHub Pages
└── _site/                       # CI 构建产物，gitignored
```

## 开始开发

要求 Python 3.11+。静态站点构建仅依赖 Python 标准库；验证使用 pytest、BeautifulSoup 和 Playwright。

```bash
git clone https://github.com/1998x-stack/xm-posts.git
cd xm-posts
python -m pip install -r requirements-dev.txt
python -m playwright install chromium

# 1. 构建静态站点
python scripts/build_site.py

# 2. 检查文章、目录、链接和四份 Skill
python scripts/validate_site.py
python scripts/sync_skills.py --check
python -m pytest -q

# 3. 预览产物：在 _site/ 目录启动静态服务器
cd _site && python -m http.server 8000
# 打开 http://localhost:8000/
```

生产版本链接按 GitHub Pages 项目路径 `/xm-posts/` 构建；在 `http.server` 本地预览时，页面内的相对链接照常工作。页面不使用前端框架、CDN 或远程脚本，不做追踪。

## 新增一篇 Post（可持续扩展）

1. 从分类中选定一个稳定 slug，执行：

   ```bash
   python scripts/new_post.py inference understanding-kv-cache \
     --title 'Understanding KV Cache' \
     --subtitle '为什么缓存 Key 与 Value 能加速自回归解码？' \
     --paper 'https://arxiv.org/...'
   ```

2. 这会创建 `posts/inference/understanding-kv-cache/`，并在 `content/posts.json` 注册 `status: draft`。依据 [`SKILL.md`](skills/olah-style-paper-posts/SKILL.md) 完成论文取证、渐进式图解、SVG 单独提取、数学与代码核验，填充 `evidence.json`。
3. 在本地执行 `python scripts/build_site.py && python scripts/validate_site.py && python -m pytest -q`；在 Chromium 桌面 / 手机宽度下检查文章交互、图片与溢出。
4. 论文证据和浏览器检查通过后，手动将注册条目的 `status` 改为 `published`，更新实际发布日期、摘要、阅读时长等数据。提交 PR；PR 会自动验证但**不会部署**。
5. PR 合并到 `main` 后，Actions 重新构建并部署。首页、分类列表、归档、`posts.json`、RSS 和 Sitemap 自动更新。`draft` 从线上构建完全排除。

## 多 Agent Skill 兼容

本仓库从 [Olah-style-posts](https://github.com/1998x-stack/Olah-style-posts) 引入 `olah-style-paper-posts`，并在四个 Agent 可发现的位置保留**完整文件副本**，包含 `SKILL.md`、`references/`、`assets/`、`scripts/`。实际 Agent 的发现规则视软件配置而定；这四个目录不只是指向正本的坏链接或简短转发文件。

**只编辑 `skills/olah-style-paper-posts/` 正本**，更新后运行：

```bash
python scripts/sync_skills.py
python scripts/sync_skills.py --check
```

镜像不同步会使 CI 失败。正本出处和引入版本详见 [`UPSTREAM.md`](skills/olah-style-paper-posts/UPSTREAM.md)。

## GitHub Pages 与持续部署

[`.github/workflows/publish.yml`](.github/workflows/publish.yml) 在 PR 上执行质量检查、测试、HTML 构建、浏览器 QA；在 `main` push 后，用 `actions/upload-pages-artifact` 和 `actions/deploy-pages` 发布已验证的 `_site/`。工作流申请最低所需的 `contents: read`、`pages: write` 和 `id-token: write` 权限，并将部署放在 `github-pages` 环境。

**首次启用说明（如果自动启用被仓库策略拒绝）：**

进入仓库 **Settings → Pages → Build and deployment → Source → GitHub Actions**，保存后在 **Actions → Validate & publish xm-posts → Run workflow** 重新运行。工作流会先尝试通过 GitHub Pages API 在仓库中自动初始化工作流发布源；若 token 权限不足，这一步会失败并提示人工启用（不会虚构已上线的站点）。详见 [GitHub 官方说明](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)。

预期生产入口：`https://1998x-stack.github.io/xm-posts/`。以 GitHub Actions 中成功的 `Publish GitHub Pages` Job 和在线 URL 实际访问为准，而非仅以 YAML 文件存在判定上线。

## 内容标准与归属

主要研究方法来自 Christopher Olah 的 [Understanding LSTM Networks](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) 与 Harvard NLP 的 [The Annotated Transformer](https://nlp.seas.harvard.edu/annotated-transformer/) **教学组织思路**，而不是复制其文字、代码或图片。论文实验数字标注原论文出处；示意与推导区分教学简化与论文结果；生成的文章不应出现“单文件离线”“原创 SVG”“参考某某风格”等制作过程小字。

协作请先阅读 [`AGENTS.md`](AGENTS.md)、[`docs/editorial.md`](docs/editorial.md) 和 [`CONTRIBUTING.md`](CONTRIBUTING.md)。除非明确核验并添加仓库许可证，否则不要推断第三方论文、图像、代码享有与本站相同的再分发许可。
