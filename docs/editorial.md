# Editorial and illustration standard

## A coherent causal explanation

A post should answer one reader misconception: why depth degrades optimization in a plain network, why Q/K/V enable direct access without recurrence, why caches make incremental decoding possible, etc. Work through the sequence *problem → observation → minimum visual mechanism → mathematical derivation with dimensions → full model architecture → executable example → original-paper evidence → limits and modern variants*.

## What counts as evidence

Separate statements by role: primary-paper claim, intuition/metaphor, toy worked example, independently derived equation, modern alternative implementation and unresolved claim. Original experiment metrics must retain their model variant, dataset, split, evaluation protocol and figure/table/section locator. The per-article `evidence.json` should name meaningful sources and verification status. Do not imply a minimal attention module replicates a machine-translation system.

## Mathematical typesetting

- Use mathematically structured output, preferably native MathML Core, for self-contained offline articles. Fractions, indices, exponents and sum limits should not be long Unicode strings.
- Number major equations and separate constraints; preserve the precise symbols and mathematical scope.
- Long expressions must scroll within labeled, keyboard-focusable formula regions at 360px and 390px without page-wide overflow; validate MathML and fraction stacking in real Chromium.
- Avoid third-party CDN scripts/fonts for mathematical rendering.

## SVG visual grammar

Each figure answers a single question. Keep a consistent conceptual color role across related diagrams, label inputs, transformations, outputs, tensors and arrows, avoid decorative lines that imply incorrect computational topology. SVG must include `viewBox` plus accessible `<title>`/description, and marker/clip-path IDs must be **unique across all SVGs in one HTML document**; prefer `arrow-f03` over repeated `arrow`. Export `.svg` individually to `assets/` and inspect them standalone. Diagrams are independently drawn from model computations; never copy reference artwork without permission.

## HTML and interaction

This is an article publication, not a marketing page. Use one H1, navigable heading hierarchy, responsive readable text, accessible controls, a meaningful non-JS baseline, keyboard focus, 360px mobile and print support, and reduced-motion styles. No external JS, fonts, analytics or third-party trackers. A subtle site navigation to related articles is welcome; build-system labels are not article content.

**Forbidden process chatter inside published posts:** “原创图解 · 单文件离线 HTML”, “用直觉 → 图示 → 数学 → 工程实现，理解残差网络 · 参考 Colah 风格，非原文翻译”, “原创教程 · 单 HTML 文件”, “图形均为独立绘制的 SVG，可无损放大”. Production details belong in the repository, not article footers.

## Release check

Check 1440, 768, 390 and 360px viewport widths, missing image/SVG render, horizontal overflow, browser JS errors, actual control state changes and print layout. Code assertions must be deterministic. Cite original sources and mark any unperformed test as unknown—not successful.
