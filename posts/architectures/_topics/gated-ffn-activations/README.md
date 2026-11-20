# Gated FFN & Activations

属于 `Architectures` 下的二级主题，**不是发布文章**。文章入口：[Understanding SwiGLU](../../swiglu/index.html)。

规划：经典 GLU（Dauphin 2017）→ ReGLU / GEGLU / SwiGLU（Shazeer 2020）→ PaLM / LLaMA 中的 Gated MLP → 门控融合 Kernel 与参数/训练代价。

本主题只描述每个 token 内部的前馈层乘性门控；MoE 路由归 `Mixture of Experts (MoE)`，Attention 头共享归 `Attention Head Sharing`，kernel 性能分析可交叉链接 `systems`。
