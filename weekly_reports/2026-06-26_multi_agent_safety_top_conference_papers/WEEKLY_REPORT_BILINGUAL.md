# Bilingual Weekly Report: Multi-Agent AI Safety Papers from Top Conferences

Date: 2026-06-26

## 1. Research Focus / 研究主题

**English.** This week I reviewed recent top-conference papers related to multi-agent AI safety, especially papers connected to emergent collective capabilities, communication, coordination, topology, oversight, and adversarial robustness. The search was restricted to ICML, ICLR, NeurIPS, ACL, and EMNLP in 2025-2026.

**中文。** 本周整理了 2025-2026 年顶会中与多智能体 AI 安全相关的论文，重点关注涌现的集体能力、智能体间通信、协同拓扑、监督控制、攻击与鲁棒性。检索范围限定为 ICML、ICLR、NeurIPS、ACL 和 EMNLP。

## 2. Why This Matters / 为什么重要

**English.** The Schmidt Sciences call asks how to model collective capabilities and communication as agent populations scale. The key idea is that safety-relevant behavior may appear only at the population level: a group of individually acceptable agents can still become unstable, collusive, vulnerable to cascading errors, or more capable than expected.

**中文。** Schmidt Sciences 资助方向关注的是：当智能体数量增加、能力差异扩大、通信结构变化时，集体能力和安全风险如何变化。核心问题在于，许多风险并不是单个智能体内部就能看出来的，而是在群体互动、通信、分工和资源共享中才会出现。

## 3. Main Findings / 主要发现

**English.**

1. **Communication topology is becoming a central object of study.** Several papers show that the structure of who talks to whom affects accuracy, cost, robustness, and error propagation.
2. **Emergent communication is no longer only a toy-game topic.** New work studies covert communication, activation-level communication, thought communication, symbolic protocols, and communication under misinformation.
3. **Multi-agent evaluation is moving from final-score benchmarks to process-aware diagnostics.** New benchmarks ask which agent failed, when failure happened, how information propagated, and whether collaboration or competition is actually useful.
4. **Security risks are system-level.** Prompt attacks, topology inference, collusion, faulty agents, and infection-like propagation can break systems even when individual agents look safe.
5. **Oversight needs attribution and intervention.** The most useful papers for AI Forge-style research are those that connect monitoring to failure attribution, auditing, or runtime control.

**中文。**

1. **通信拓扑正在成为核心研究对象。** 多篇论文表明，谁和谁通信会影响准确率、成本、鲁棒性和错误传播方式。
2. **涌现通信不再只是玩具环境问题。** 最新工作开始研究隐蔽通信、激活层通信、思维通信、符号协议以及错误信息环境下的通信演化。
3. **多智能体评测正在从最终得分转向过程诊断。** 新基准不仅看任务是否完成，还追踪哪个智能体出错、在哪一步出错、信息如何传播、协作是否真的带来收益。
4. **安全风险是系统级的。** 提示攻击、拓扑推断、合谋、故障智能体和感染式传播，都可能在单体安全评估之外破坏系统。
5. **有效监督需要归因和干预。** 与 AI Forge 最相关的论文，是那些能把监控信号连接到故障归因、审计或运行时控制的工作。

## 4. Most Relevant Papers / 最相关论文

**English.** The closest papers to the proposal paragraph are:

- **Emergent Coordination in Multi-Agent Language Models** (ICLR 2026): proposes information-theoretic measures for detecting higher-order coordination in multi-agent LLM systems.
- **Understanding the Information Propagation Effects of Communication Topologies in LLM-based Multi-Agent Systems** (EMNLP 2025): studies how correct and incorrect information travels through different MAS topologies.
- **MultiAgentBench** (ACL 2025): evaluates collaboration and competition among LLM agents.
- **SILO-BENCH** (ACL 2026): evaluates distributed coordination when each agent observes only part of the problem.
- **Which Agent Causes Task Failures and When?** (ICML 2025): introduces failure attribution for LLM multi-agent systems.
- **TAMAS** (ACL 2026): benchmarks adversarial risks specific to multi-agent LLM systems.

**中文。** 与 proposal 中那段文字最直接相关的论文包括：

- **Emergent Coordination in Multi-Agent Language Models**（ICLR 2026）：用信息论方法检测多智能体 LLM 系统中的高阶协同结构。
- **Understanding the Information Propagation Effects of Communication Topologies in LLM-based Multi-Agent Systems**（EMNLP 2025）：研究不同通信拓扑下正确信息和错误信息如何传播。
- **MultiAgentBench**（ACL 2025）：评测 LLM 智能体之间的合作与竞争。
- **SILO-BENCH**（ACL 2026）：评测信息孤岛场景下的分布式协同能力。
- **Which Agent Causes Task Failures and When?**（ICML 2025）：提出多智能体失败归因任务。
- **TAMAS**（ACL 2026）：评测多智能体 LLM 系统中的对抗风险。

## 5. Connection to AI Forge / 与 AI Forge 的关系

**English.** AI Forge emphasizes operational interpretability, control, sandboxing, runtime intervention, adversarial robustness, and credible benchmarks. The papers here provide concrete research building blocks for those goals: topology-aware monitoring, process-level failure attribution, adversarial multi-agent benchmarks, sandbox-style web-agent safety evaluation, and mechanisms for maintaining cooperation under mixed motives.

**中文。** AI Forge 强调可操作的解释性、控制、沙箱、运行时干预、对抗鲁棒性和可信评测。本周整理的论文为这些目标提供了具体技术入口：通信拓扑监控、过程级失败归因、多智能体对抗基准、Web agent 安全评测，以及在混合动机环境中维持合作的机制。

## 6. Research Gaps / 研究空白

**English.**

- Current papers often study **small or medium populations**, while the proposal asks about large-scale populations.
- Many works optimize communication for performance, but fewer evaluate **safety-relevant phase transitions**.
- There is still no standard benchmark for when benign coordination becomes collusion.
- Failure attribution remains hard: identifying the responsible agent is easier than identifying the decisive failure step.
- Most work assumes one system owner; the Schmidt call emphasizes multi-principal deployment, where agents come from different actors.

**中文。**

- 现有论文多研究小规模或中等规模智能体群体，而 proposal 关注更大规模群体。
- 很多工作优化通信以提升性能，但较少研究与安全相关的“相变”。
- 目前还缺少统一基准来区分良性协同与合谋。
- 失败归因仍然困难：找出责任智能体比找出关键错误步骤容易得多。
- 许多工作默认系统由单一主体控制，而 Schmidt call 更关注多主体部署，即智能体来自不同开发者或组织。

## 7. Possible Proposal Angle / 可发展的 Proposal 方向

**English.** A strong project could build a population-level diagnostic framework for multi-agent LLM systems. The framework would vary population size, heterogeneity, topology, tool access, and communication bandwidth, then measure collective capability, volatility, collusion risk, failure propagation, and attribution difficulty. This would directly answer the proposal paragraph while also aligning with AI Forge-style needs for evaluation, monitoring, and control.

**中文。** 一个有潜力的 proposal 方向是构建多智能体 LLM 系统的群体级诊断框架。该框架可以系统改变智能体数量、异质性、通信拓扑、工具权限和通信带宽，并测量集体能力、系统波动性、合谋风险、错误传播和失败归因难度。这一方向既直接回应 Schmidt Sciences 的研究问题，也与 AI Forge 对评测、监控和控制的需求高度一致。

## 8. Next Week Plan / 下周计划

**English.**

1. Select 6-8 core papers for deeper reading.
2. Build a comparison table of variables: population size, topology, communication channel, tools, metrics, and failure model.
3. Identify which papers can support a concrete experiment design.
4. Draft one project hypothesis around phase transitions or topology-driven risk.

**中文。**

1. 选择 6-8 篇核心论文深入阅读。
2. 建立对比表：智能体数量、拓扑、通信通道、工具、指标和失败模型。
3. 判断哪些论文可以支撑具体实验设计。
4. 围绕“相变”或“拓扑驱动风险”起草一个项目假设。
