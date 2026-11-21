# xm-posts 全仓库质量治理与清理手册

> 本文是仓库级清理、逐篇审计和周期性维护的统一操作规范。生产规则仍以 AGENTS.md、Canonical Skill 和自动化测试为准；本文把它们组织成可追踪的清理闭环。
> 参考基准：posts/architectures/transformer/、posts/architectures/resnet/，以及 skills/olah-style-paper-posts/references/ 中的论文提取、叙事、证据、MathML、SVG、浏览器 QA 与 scorecard 规范。

## 1. 清理目标与原则

目标不是把所有文章改成同一模板，而是确保每篇文章都达到同一条质量底线：科学内容可追溯、教学过程可理解、图解与公式正确、交互可验证、页面可访问、发布信息一致。

- **先事实，后美化。** 视觉完整、字数充足或 CI 通过，都不能代替论文事实核验。
- **经典文章是质量参照，不是复制模板。** Transformer 的注意力计算、Q/K/V、Mask、位置编码、Encoder/Decoder、手算示例与最小实现，以及 ResNet 的退化问题、残差块、梯度路径、维度匹配、Basic/Bottleneck、ResNet-50、v1/v2 和证据边界，提供可复用的教学组织方法。不同论文可采用不同章节和图解数量。
- **机器检查与人工判断分开。** HTML/MathML/SVG/链接/响应式测试通过，只能证明对应机器检查通过，不能证明论断、推导、图示拓扑和实验解释正确。
- **不为整齐而破坏知识结构。** 不轻易改公开 slug、分类 ID、topic ID、论文 permalink、RSS GUID 或文章路径；不按文章数量简单合并独立知识领域。
- **不猜测证据。** 不补造论文数据、表格编号、实验设置、代码结果或发布日期；未验证内容标为 NOT VERIFIED。
- **小步、可回滚。** 优先修复可确定的缺陷；科学内容或分类边界有争议时先写审计意见，不做批量自动改写。

## 2. 从经典文章提炼出的标准

### 2.1 Understanding Transformer

1. 以 LSTM 的序列依赖问题引出 Transformer 的设计动机。
2. 先建立 Self-Attention 直觉，再解释 Query、Key、Value 的职责。
3. 将注意力公式拆成可跟踪步骤，解释缩放、Softmax、Mask 和输出加权。
4. 提供可手算的微型例子，明确 toy example 与论文实验的区别。
5. 通过交互改变查询、注意力头或 Mask，展示输入变化如何影响结果。
6. 解释 Multi-Head、位置编码、Encoder、Decoder、Cross-Attention 与完整架构。
7. 区分训练并行与自回归生成时的逐 token 解码。
8. 以最小实现、代价、局限和原始论文收束。

### 2.2 Understanding ResNet

1. 先解释深度退化问题，区分优化退化与过拟合。
2. 由学习残差而非完整映射引出 H(x)=x+F(x)。
3. 逐步拆开 Residual Block，解释主分支、shortcut 与相加。
4. 解释恒等捷径如何影响反向传播，而不是只画一条跳跃箭头。
5. 明确输入/输出张量尺寸不同时的 projection shortcut。
6. 区分 Basic Block、Bottleneck、ResNet-50 与 v1/v2。
7. 对照论文结果说明证据支持什么、不支持什么。
8. 以最小 PyTorch block 和总结帮助读者迁移到实现。

### 2.3 通用教学叙事

读者疑问 → 旧方法/基线 → 核心转变 → 最小机制 → 逐步图解 → 公式与张量 → 手算/实验 → 完整系统 → 论文证据 → 局限与变体 → 总结与延伸。

复杂机制的图解通常采用 2–5 个渐进状态。不是每篇都必须有 16 个章节，也不是每个概念都需要交互控件；应以读者能否回答核心问题为判断依据。

## 3. 逐篇文章 Checklist

对每一篇 status=published 的文章逐项记录状态。允许 N/A，但必须说明原因；不能把未检查项默认为通过。

### A. 论文来源与科学事实
- [ ] 标明原始论文/官方标准/权威工程资料；核对标题、作者、版本、年份、DOI/arXiv/官方链接。
- [ ] 重要论断在正文附近有引用；evidence.json 中有 claim、kind、source_url、locator、status 和 notes。
- [ ] 论文原始方法、后续变体、工程实现、作者自述、本文推导和教学算例明确区分。
- [ ] 每个数字可追溯到模型、数据集/benchmark、split、指标、方向、表格/图号和对照条件。
- [ ] 不把相关性写成因果，不把预印本/厂商博客写成统一行业标准，不把 toy demo 写成论文复现。
- [ ] 对争议、版本差异或资料不可访问的结论明确标注不确定性。

### B. 教学叙事与解释
- [ ] 开篇提出具体问题或反直觉现象，不以营销话术代替问题。
- [ ] 说明旧方法/基线在哪里失效，避免把优化、表达能力、泛化混为一谈。
- [ ] 用一句话概括核心思想，并通过总览图建立心智模型。
- [ ] 先解释最小单元，再逐步组合完整架构；每一节承接上一节。
- [ ] 读者容易产生的疑问有明确回答；术语首次出现时得到解释。
- [ ] 至少有一个适合主题的手算例子、微型实验或代码走读；若不适用，说明原因。
- [ ] 解释失败模式、复杂度、适用边界和论文没有证明什么。
- [ ] 结尾给出正确的 mental model 和有依据的进一步阅读路径。

### C. 数学与技术推导
- [ ] 实质性公式使用语义化 MathML，而非仅用 Unicode、上下标 HTML 或 CSS 拼成的假公式。
- [ ] 每个关键符号、下标、维度、求和/归一化轴、边界条件和假设均有解释。
- [ ] 公式与论文版本一致；符号、正负号、分母、Mask、归一化位置和 train/inference 差异正确。
- [ ] 矩阵/张量 shape 与计算顺序可追踪；区分 batch、head、sequence、feature 等维度。
- [ ] 分式、上下标、矩阵、极限等使用正确 MathML 结构；display 公式置于键盘可聚焦的横向滚动区域。
- [ ] 每个 MathML 节点有可访问描述；没有 MathML 嵌入 SVG。
- [ ] 数学推导有独立测试或数值核对；无法自动验证的推导列入人工复核。

### D. 图解与 SVG
- [ ] 每张图只回答一个清楚的问题，拓扑与算法真实数据流一致。
- [ ] 图注描述可验证的机制，不只是“整体架构图”。
- [ ] SVG 有合法 viewBox、title、desc、可访问名称和唯一 ID；同一 HTML 文档内 ID 不冲突。
- [ ] 颜色、线型、箭头、节点与文字有稳定语义；不能只靠颜色传递含义。
- [ ] 图中文字在正常阅读尺寸下清晰，移动端不被裁切；复杂图必要时拆成多个状态。
- [ ] 独立 SVG 文件可单独打开，抽取后的样式与内嵌版本一致。
- [ ] 封面必须是该文章独有、能表达核心机制的本地 SVG；caption 准确、独特且适合小卡片。
- [ ] 不复制未经许可的论文插图、第三方图标、Colah/Annotated Transformer 原图或代码。

### E. HTML、无障碍与页面体验
- [ ] 单一 HTML5 doctype、恰好一个 H1、语义化 main、可导航目录/导航和连续的标题层级。
- [ ] 每个 figure 都有图像/SVG 与非空 figcaption。
- [ ] 控件有可访问名称、键盘操作、可见焦点和真实状态变化；没有空按钮或装饰性交互。
- [ ] 默认状态不依赖 JavaScript 才能理解文章。
- [ ] 本地离线可读，无不必要 CDN、远程字体、跟踪脚本或网络依赖。
- [ ] 360px、390px、768px、1440px 下没有页面级横向溢出；宽公式/代码只在明确的可聚焦容器内滚动。
- [ ] @media print 与 prefers-reduced-motion 有效；打印内容不缺失核心图表和公式。
- [ ] 检查 console/page errors、broken images、死链接、断裂锚点、SVG 尺寸与实际交互。

### F. 代码、实验与交互
- [ ] 对适合代码化的机制提供最小、可运行、可复现的例子；纯概念/标准综述可说明 N/A。
- [ ] 代码中的 shape、mask、边界条件、数值结果和随机性有明确说明。
- [ ] 示例有确定性断言或对应测试；不能把教学实现称为生产级实现。
- [ ] 交互确实改变被解释的变量/状态，并展示可观察结果；错误输入与边界状态有说明。
- [ ] 代码、图示和公式三者描述的是同一算法，不出现相互矛盾的版本。

### G. 元数据、分类与知识关系
- [ ] content/posts.json 中 slug 唯一，category/topic 均已注册，且每篇文章只有一个主分类与主 topic。
- [ ] category/topic 是最窄且准确的归属；跨领域概念放在 tags 和阅读路径，不复制文章或创建近义分类。
- [ ] title、subtitle、summary、tags、reading_minutes、paper、published、updated 完整且真实。
- [ ] updated >= published；不得用构建日期伪造实际发布日期。
- [ ] cover.src 指向文章自己的 assets/*.svg；cover 文件存在、内容唯一、caption 有信息量。
- [ ] evidence.json 是有效且非空的 claim ledger；ID 唯一，状态合法，source_url 与 locator 可追溯。
- [ ] 新文章加入适合的 content/reading_paths.json 路径；关联有明确的先修/进阶/同主题理由。
- [ ] 文章源目录、分类 README、规划中 topic README 和 manifest 一致；不发布占位页。

### H. 全站信息架构与发布
- [ ] 首页精选、分类入口、知识地图、阅读路径、搜索/筛选/分页和归档均能到达正确页面。
- [ ] 首页与 README 的分类说明没有遗漏当前一级分类；topic 规划中状态清晰可辨。
- [ ] RSS、Sitemap、canonical、Open Graph、文章 JSON 与 manifest 一致；草稿不进入公开产物。
- [ ] 相关阅读只推荐真实已发布文章，最多四张，不强行构造无关关系。
- [ ] PDF 对所有正式文章生成且可解析、可搜索；公式、SVG、CJK 字体与分页无明显损坏。
- [ ] PR 验证与 main 部署语义清楚；只有部署 Job 成功且公开页面/文件实际可访问，才报告线上发布成功。

## 4. 状态、严重等级与处置

每项检查只使用以下状态：
- PASS：已检查且有证据。
- FAIL：已确认违反标准，附文件路径、行/章节、截图或测试日志。
- NOT VERIFIED：尚未检查，或当前工具无法证明。
- N/A：不适用于该文章，写明原因。

| 等级 | 含义 | 处置 |
|---|---|---|
| P0 | 科学事实错误、严重安全/版权问题、错误发布/草稿泄露、损坏核心内容 | 立即阻止发布；必要时回滚 |
| P1 | 关键公式/图解/证据不完整、分类错误、主要交互失效、页面核心内容不可读 | 当前清理批次优先修复 |
| P2 | 阅读路径断裂、元数据/README/页面导航不同步、移动端局部体验问题、重复维护来源 | 纳入近期治理 |
| P3 | 视觉细节、措辞、非关键排版优化 | 有余力时处理 |

现有 skills/olah-style-paper-posts/references/scorecard.md 的 100 分评分用于人工编辑判断；评分不得由脚本伪造。任何 P0/P1 缺陷都不能被总分抵消。

## 5. 现有自动化门禁与正确解释

| 工具 | 能证明什么 | 不能证明什么 |
|---|---|---|
| scripts/validate_site.py | HTML 基础结构、链接、证据文件存在、源文章静态校验、生成站点完整性 | 论文结论本身正确 |
| skills/olah-style-paper-posts/scripts/validate.py | 文章语义结构、figure、SVG、MathML 与证据 ledger 结构 | 图解拓扑和公式推导的科学含义 |
| scripts/audit_svg.py | SVG XML、viewBox、ID、可访问描述和引用完整性 | 图中箭头是否表达真实算法 |
| tests/ | 已编码的数学、数据结构、分类、PDF、RSS 与站点回归 | 未被测试覆盖的假设 |
| scripts/browser_check_all.py | 每篇正式文章的 Chromium、多视口、公式几何、交互与打印检查 | 其他浏览器兼容性和人工可读性 |
| scripts/render_pdfs.py + validate_site.py --require-pdfs | 正式文章 PDF 存在、可解析、可提取文本 | 每一页的所有细节都没有视觉缺陷 |
| 人工逐篇审读 | 论文事实、因果解释、教学顺序、图解语义、分类边界 | 不能替代自动回归 |

推荐完整验证命令：
```bash
python scripts/sync_skills.py --check
python -m pytest -q
python scripts/audit_svg.py
python scripts/build_site.py
python scripts/validate_site.py
python scripts/browser_check_all.py --workers 2
python scripts/render_pdfs.py
python scripts/validate_site.py --require-pdfs
```

如果运行环境无法执行 Chromium/PDF，必须记录为 NOT VERIFIED，不能跳过后宣称通过。

## 6. 2026-11-22 基线盘点

| 指标 | 基线 |
|---|---:|
| 正式文章 HTML | 105 |
| 一级分类 | 16 |
| 二级主题 | 131 |
| 已有文章的 topic | 83 |
| 规划中 topic | 48 |
| evidence.json | 105 |
| 独立 SVG 文件 | 596 |
| Python / Notebook 示例 | 113 |
| 文章专属封面 | 105 / 105，SHA 内容唯一 |
| 阅读路径 | 62 |
| 2026-11-21 最新主分支 Chromium QA | 105 / 105 通过 |
| 最新主分支 Pages deploy Job | 成功 |

### 已确认的问题与决策

1. **README 分类概览遗漏两个领域：** 已补入 Decision Models 与 Knowledge Representation。
2. **分类文档计数过时：** docs/taxonomy.md 原标题写 14 个一级分类，已改为不硬编码数量的标题。
3. **证据静态校验不完整：** 文章验证器过去只检查 evidence.json 存在；需要验证 ledger 字段、ID、状态、URL 和 locator。
4. **C51 evidence notes 缺失：** 已补充前三项记录的来源说明。
5. **48 个 topic 暂无文章：** 当前知识地图明确显示“规划中”，先保留作为路线图；不因为空 topic 删除稳定分类。每次新增 topic 必须说明边界与近期建设内容。
6. **单篇文章分类：** Systems、Storage & Indexing、Knowledge Representation、Multimodal、Decision Models 当前各有单篇文章。保留其独立知识边界，观察后续扩展方向，不以数量作为合并依据。
7. **首页路线维护：** 首页 7 条精选学习路径目前在 scripts/build_site.py 中配置；每篇文章的 related-reading 图由 content/reading_paths.json 管理。两者用途不同，但都需定期检查，后续可评估是否抽取独立首页路线 manifest。
8. **人工审读状态：** 本次已确认自动化全站检查通过；尚未声称 105 篇文章的全部科学论断、公式推导和图解语义均完成逐篇人工复核。必须按清单逐批完成。

## 7. 每次清理的执行顺序

1. 读取最新 main、PR、最近 CI 和 Pages 部署状态；确认没有重复清理 PR。
2. 比较最近新增/修改的文章、manifest、分类、阅读路径、SVG、evidence 和首页构建逻辑。
3. 对所有正式文章运行自动静态检查；人工审读新增/改动文章，并按轮转计划抽查较早文章。
4. 优先处理 P0/P1，再处理 P2；P3 不得挤占科学正确性工作。
5. 修复后运行完整测试、SVG 审计、全文章 Chromium 检查和 PDF 校验；保存报告与截图。
6. 审查 diff，确保不误改论文、公开 slug、分类 ID、日期、RSS GUID 和既有图解。
7. 通过独立分支提交 PR。CI 只代表 PR 验证；合并到 main 后再确认 Pages deploy Job 与线上资源。
8. 输出变更、未解决问题、未验证项、测试结果、PR/部署链接。无实质问题时不创建空 PR。

## 8. 周期性清理策略

定时运行时，采用“增量审计 + 全库门禁 + 人工轮转”：
- **增量审计：** 检查最近新增/修改文件、文章 manifest、分类/标签、阅读路径、首页/构建脚本、工作流和文档漂移。
- **全库门禁：** 对全部 published 文章运行已有静态、数学、SVG、浏览器与 PDF 检查。
- **人工轮转：** 每次至少深读 3–5 篇尚未审读或近期改动的文章；优先覆盖不同分类和较早的经典文章，避免只审查最新文章。
- **问题去重：** 相同缺陷合并为一个根因；已在开放 PR 中处理的问题不重复处理。
- **安全修复：** 只有确定性、低风险且有测试保护的修复可以自动提交；科学论断、数学语义、论文数据、分类重构和公开路径变更必须明确复核。
- **无变化时：** 记录无新增问题即可，不生成无意义 commit/PR。

## 9. 审计记录模板

每篇文章至少保留以下字段（可写入 PR 描述或审计报告）：
```yaml
slug: transformer
category: architectures
topic: transformers
commit: <audited-main-sha>
source_evidence: PASS | FAIL | NOT VERIFIED | N/A
narrative: PASS | FAIL | NOT VERIFIED | N/A
mathematics: PASS | FAIL | NOT VERIFIED | N/A
diagrams_svg: PASS | FAIL | NOT VERIFIED | N/A
html_accessibility: PASS | FAIL | NOT VERIFIED | N/A
code_interactions: PASS | FAIL | NOT VERIFIED | N/A
metadata_taxonomy: PASS | FAIL | NOT VERIFIED | N/A
browser_pdf: PASS | FAIL | NOT VERIFIED | N/A
human_reviewed_at: YYYY-MM-DD
findings:
  - severity: P1
    path: posts/architectures/transformer/index.html
    detail: <specific finding>
    evidence: <line, section, screenshot, or test>
```

不要仅因为某个字段是 PASS 就推断其他维度也通过。每个状态必须对应实际检查证据。
