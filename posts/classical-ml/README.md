# 经典机器学习 / Classical Machine Learning

研究深度学习之前的关键学习算法、统计学习思想与可解释的数学机制。收录最大间隔与核方法（SVM）、逻辑回归、决策树、集成学习（包括 XGBoost）、图模型等，侧重原始论文、推导、实验及适用边界。

新文章放在 `posts/classical-ml/<slug>/index.html`，配套 `assets/*.svg` 和 `evidence.json`。只有在 `content/posts.json` 中标记为 `published` 的完整文章才进入 GitHub Pages。

已发布文章：[Understanding Decision Tree](decision-tree/index.html)（ID3、CART、C4.5、Gini、回归与剪枝）；[Understanding SVM](svm/index.html)（最大间隔、对偶与核方法）。

[Understanding GMM](gmm/index.html) 从混合密度、潜变量与软责任走到 EM 交替优化、BIC 和协方差选型，作为概率模型下的 **Mixture Models & Density Estimation** 二级主题。

新增文章：[Understanding KNN](knn/index.html)——实例学习、局部投票、距离尺度、k 的选择、Cover–Hart 大样本界，以及 ANN 与精确分类的区别。二级主题 `Instance-based Learning & Nearest Neighbors` 归在经典机器学习，不新建一级分类。

## Clustering & Unsupervised Learning

新增二级研究主题 `clustering`，用于 K-Means、k-means++、MiniBatch K-Means，以及后续谱聚类、密度聚类与层次聚类的对比。当前论文解读位于 [Understanding K-Means](k-means/index.html)，包括五幅 SVG、原生 MathML、可交互 Lloyd 迭代、代码和证据台账。此主题属于 Classical ML，不另建一级分类。
