# 推荐系统 / Recommender Systems

研究如何从用户偏好、交互反馈与物品关系中估计个体兴趣，并将候选内容转化为个性化召回与排序。

## 当前注册专题

- [Collaborative Filtering & Neighborhood Models](_topics/collaborative-filtering/README.md)：用户/物品相似性、共同评分、邻域聚合与评分预测。

## 研究边界

- 通用近邻分类与回归属于 `classical-ml/nearest-neighbors`；推荐系统中的近邻用于预测用户对候选物品的偏好。
- 查询驱动的文档召回与证据生成属于 `retrieval-rag`；推荐系统优化的是用户—物品匹配与个性化效用。
- 矩阵分解、隐式反馈、学习排序、序列推荐和图推荐将在有相应论文解读时注册为独立二级专题，不提前建立空文章。

正式文章源文件位于 `posts/recommender-systems/<slug>/index.html`，配套 SVG、证据台账和可运行示例；只有 `content/posts.json` 中的 `published` 条目才会进入站点。
