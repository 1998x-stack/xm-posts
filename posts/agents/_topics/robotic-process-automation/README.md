# Robotic Process Automation & Agentic Process Automation

## 专题范围

本专题研究软件机器人如何在现有业务系统中执行重复、规则驱动的数字任务，以及它如何与 Process Mining、IPA 和 LLM Agent 协同。

## 核心问题

1. 哪些流程具有足够高的频率、规则稳定性和输入质量，值得自动化？
2. 如何从事件日志和 UI 交互轨迹发现真实流程与自动化候选？
3. Bot Worker、Orchestrator、Queue、Adapter、Credential Vault 和 Audit 如何组成企业级运行时？
4. 如何用状态机、幂等键、后置条件、重试与人工升级保证执行可靠性？
5. 如何把 OCR / ML / LLM 的语义理解与确定性 RPA 执行分层组合？
6. 如何评估业务状态正确性、风险、维护成本和端到端 ROI？

## 重要边界

- Traditional RPA 是规则驱动的确定性执行器，不等同于 LLM Agent。
- BPM / Workflow 管理端到端流程；RPA 通常承担任务级执行。
- API Automation 优先使用稳定系统契约；UI RPA 用于兼容遗留应用或缺乏接口的环节。
- IPA 增加文档理解、OCR、ML / NLP 等认知能力。
- Agentic Process Automation 在不确定环节引入 Agent 规划，但高影响动作仍需权限、审批与状态验证。

## 推荐研究脉络

- van der Aalst et al. (2018), Robotic Process Automation.
- Wewerka and Reichert (2021/2023), RPA systematic mapping study.
- RPA with Process Mining systematic review (2023).
- Farinha et al. (2024), process-selection framework.
- Khantong and Sriboonlue (2026), RPA–BPM systematic review.
- Chen et al. (2026), AutoRPA.
- ERPBench (2026), state-grounded enterprise computer-use evaluation.

规划占位不代表已经发布独立文章；正式文章以 content/posts.json 为准。
