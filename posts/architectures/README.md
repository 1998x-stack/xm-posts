# 模型架构 / Architectures

拆开网络的信息路径：从 ResNet 的残差学习到 Transformer 的注意力结构、RoPE 位置编码与相对位移。

该目录包含本分类文章。添加新 Post 时创建 `posts/architectures/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

RoPE 位于 `posts/architectures/rope/`，主题是 **Positional Encoding**；位置编码属于模型架构的一部分，长上下文服务与 KV Cache 的系统实现则在推理分类中交叉关联。
