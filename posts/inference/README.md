# 推理与 Serving / Inference & Serving

从自回归解码、KV Cache、批处理到实际在线服务的延迟与吞吐。

该目录包含本分类文章。添加新 Post 时创建 `posts/inference/<slug>/index.html`、`assets/*.svg` 与 `evidence.json`，并在 `content/posts.json` 注册元数据。

`status: draft` 不进入线上索引；只有 `published` 会被 Actions 自动打包。不要把 README 占位文件发布到 GitHub Pages。

## Published deep dives

- [Understanding PagedAttention](pagedattention/index.html) — KV cache 分页、Block Table、Copy-on-Write、Serving 调度与 GPU kernel。

本分类已有空间容纳 KV Cache / PagedAttention / Continuous Batching；系统级 kernel 细节通过标签关联 `systems/`，无需新增顶级类别。
