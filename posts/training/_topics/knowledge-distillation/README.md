# Knowledge Distillation & Teacher–Student Transfer

本专题研究如何把教师模型的输出分布、内部表征、样本关系与生成轨迹转化为学生模型可以学习的训练信号。

正式文章：[Understanding Knowledge Distillation](../../knowledge-distillation/index.html)

## 分类边界

- 主归属：`training` → `knowledge-distillation`
- 不新增 `model-compression` 一级分类：蒸馏是训练监督与知识迁移范式，可服务压缩，也可用于同规模能力迁移。
- 与 `architectures`、`reasoning`、`multimodal`、`inference` 通过 tags、论文关系和阅读路径交叉关联。

## 多维研究坐标

1. 知识信号：Response / Logit、Feature、Relation、Sequence / Rationale。
2. 教师访问：White-box / Black-box。
3. 数据机制：Offline / Online / On-policy / Self-distillation / Multi-teacher。
4. 目标能力：分类与表征、语言任务、推理、工具调用、多模态。

这些维度彼此正交；单篇论文可以同时采用多种信号与训练机制。文章仍保持一个主 category/topic，避免分类重复。

## 质量门禁

- 原始论文事实、实验数字和教学算例必须分开记录在 `evidence.json`。
- 数学公式使用可访问 MathML；每张 SVG 具有 title、desc 和正文图注。
- 区分教师训练阶段与学生蒸馏阶段；区分 Knowledge Distillation 与 Dataset Distillation。
- 交互实验必须有静态默认状态、键盘操作、移动端布局和浏览器验证。
