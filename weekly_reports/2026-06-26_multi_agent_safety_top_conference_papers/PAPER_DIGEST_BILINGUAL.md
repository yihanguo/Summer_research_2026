# Paper Digest: 2025-2026 Top-Conference Papers on Multi-Agent AI Safety

This digest groups the selected papers by how directly they support the multi-agent safety agenda.

## A. Emergence, Coordination, and Cooperation / 涌现、协同与合作

| Paper | Venue | Brief summary |
|---|---:|---|
| [Emergent Coordination in Multi-Agent Language Models](https://openreview.net/forum?id=SRn1MtMPRq) | ICLR 2026 | Uses information-theoretic decomposition to test whether multi-agent LLM systems show higher-order coordination beyond independent agent behavior. 中文：用信息论分解方法判断多智能体 LLM 是否出现超越单体行为的高阶协同结构。 |
| [MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents](https://aclanthology.org/2025.acl-long.421/) | ACL 2025 | Provides a benchmark for collaboration and competition across interactive LLM-agent scenarios. 中文：提供多场景基准，用于评测 LLM 智能体的协作与竞争能力。 |
| [SILO-BENCH: A Scalable Environment for Evaluating Distributed Coordination in Multi-Agent LLM Systems](https://aclanthology.org/2026.acl-long.1354/) | ACL 2026 | Tests whether agents can coordinate when each sees only part of the global problem. 中文：评测信息孤岛场景下多智能体是否能完成分布式协同。 |
| [CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas](https://openreview.net/forum?id=369qOr0ZnJ) | ICML 2026 | Studies mechanisms that sustain cooperation among LLM agents in social dilemmas. 中文：研究在社会困境中维持 LLM 智能体合作的机制。 |
| [Shapley-Coop: Credit Assignment for Emergent Cooperation in Self-Interested LLM Agents](https://openreview.net/forum?id=HnJ1UkuJXS) | NeurIPS 2025 | Connects emergent cooperation with credit assignment among self-interested LLM agents. 中文：研究自利 LLM 智能体中涌现合作的贡献分配问题。 |
| [The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy](https://openreview.net/forum?id=Na3YzWMXwz) | ICML 2026 | Models oversight and autonomy as a Markov game between an agent and a human overseer. 中文：将智能体自主性与人类监督之间的权衡建模为 Markov game。 |

## B. Communication, Topology, and Information Flow / 通信、拓扑与信息流

| Paper | Venue | Brief summary |
|---|---:|---|
| [Understanding the Information Propagation Effects of Communication Topologies in LLM-based Multi-Agent Systems](https://aclanthology.org/2025.emnlp-main.623/) | EMNLP 2025 | Analyzes how communication topology affects the spread of correct and incorrect answers. 中文：分析通信拓扑如何影响正确和错误信息在多智能体系统中的传播。 |
| [Dynamic Generation of Multi LLM Agents Communication Topologies with Graph Diffusion Models](https://aclanthology.org/2026.acl-long.1764/) | ACL 2026 | Generates adaptive communication topologies for multi-LLM-agent systems. 中文：用图扩散模型动态生成多 LLM 智能体通信拓扑。 |
| [G-Designer: Architecting Multi-agent Communication Topologies via Graph Neural Networks](https://proceedings.mlr.press/v267/zhang25cu.html) | ICML 2025 | Learns task-aware communication graphs to balance quality and token cost. 中文：学习任务相关通信图，在性能和 token 成本之间做权衡。 |
| [Communicating Activations Between Language Model Agents](https://proceedings.mlr.press/v267/ramesh25a.html) | ICML 2025 | Lets language-model agents communicate through internal activations rather than only natural language. 中文：让语言模型智能体通过内部激活而不仅是自然语言通信。 |
| [Thought Communication in Multiagent Collaboration](https://openreview.net/forum?id=tq9lyV9Cml) | NeurIPS 2025 | Proposes latent "thought communication" as a more direct medium for collaboration. 中文：提出潜在“思维通信”，作为比自然语言更直接的协作媒介。 |
| [Benefits and Limitations of Communication in Multi-Agent Reasoning](https://openreview.net/forum?id=0aPIVJUz5T) | ICLR 2026 | Gives theoretical analysis of when communication helps multi-agent reasoning. 中文：从理论上分析通信在多智能体推理中的收益与限制。 |
| [CoMet: Metaphor-Driven Covert Communication for Multi-Agent Language Games](https://aclanthology.org/2025.acl-long.389/) | ACL 2025 | Studies metaphor-based covert communication and semantic evasion in multi-agent language games. 中文：研究多智能体语言游戏中的隐喻式隐蔽通信和语义规避。 |
| [When LLMs Develop Languages: Symbolic Communication for Efficient Multi-Agent Reasoning](https://openreview.net/forum?id=ovpL0ujD6j) | ICML 2026 | Allows agents to invent compact symbolic communication protocols for reasoning. 中文：让智能体发明紧凑符号协议以提高多智能体推理效率。 |

## C. Safety, Oversight, and Failure Attribution / 安全、监督与失败归因

| Paper | Venue | Brief summary |
|---|---:|---|
| [Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems](https://proceedings.mlr.press/v267/zhang25cq.html) | ICML 2025 | Introduces failure attribution for identifying the responsible agent and failure step. 中文：提出多智能体失败归因任务，定位责任智能体和关键错误步骤。 |
| [TAMAS: Benchmarking Adversarial Risks in Multi-Agent LLM Systems](https://aclanthology.org/2026.acl-long.1442/) | ACL 2026 | Benchmarks adversarial risks specific to multi-agent LLM dynamics. 中文：评测多智能体 LLM 系统特有的对抗风险。 |
| [Agents Under Siege: Breaking Pragmatic Multi-Agent LLM Systems with Optimized Prompt Attacks](https://aclanthology.org/2025.acl-long.476/) | ACL 2025 | Attacks pragmatic MAS under communication, latency, and defense constraints. 中文：在通信、延迟和防御约束下攻击实用多智能体 LLM 系统。 |
| [A2ASecBench: A Protocol-Aware Security Benchmark for Agent-to-Agent Multi-Agent Systems](https://openreview.net/forum?id=LfdFnakqGJ) | ICLR 2026 | Evaluates vulnerabilities in agent-to-agent protocols and multi-agent infrastructure. 中文：评测 Agent-to-Agent 协议和多智能体基础设施中的安全漏洞。 |
| [GUARDIAN: Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling](https://openreview.net/forum?id=6j9xJ9pBjm) | NeurIPS 2025 | Models multi-agent collaboration as a temporal graph to detect and mitigate hallucination/error propagation. 中文：将多智能体协作建模为时间图，用于检测和缓解幻觉及错误传播。 |
| [Reliable Weak-to-Strong Monitoring of LLM Agents](https://openreview.net/forum?id=WV7xIboTDK) | ICLR 2026 | Stress-tests monitoring systems for covert misbehavior in tool-using agents. 中文：压力测试工具型智能体中隐蔽不当行为的监控系统。 |
| [Architecture Matters for Multi-Agent Security](https://openreview.net/forum?id=Jk4zLorDUx) | ICML 2026 | Studies how MAS architecture choices change task performance and attack resistance. 中文：研究多智能体架构选择如何影响任务表现和抗攻击能力。 |
| [AgentAuditor: Human-level Safety and Security Evaluation for LLM Agents](https://openreview.net/forum?id=2KKqp7MWJM) | NeurIPS 2025 | Uses memory-augmented reasoning to evaluate safety and security across agent trajectories. 中文：利用带记忆的推理框架评估智能体轨迹中的安全与安全性问题。 |

## Cross-Paper Synthesis / 跨论文综合

**English.** The papers form a useful pipeline for proposal design:

1. Use MultiAgentBench or SILO-BENCH to create controlled multi-agent tasks.
2. Vary communication topology using G-Designer, graph diffusion, or topology-pruning approaches.
3. Measure emergence using information-theoretic metrics from Emergent Coordination.
4. Track propagation using topology-aware information-flow analysis.
5. Stress-test the system with faulty agents, prompt attacks, protocol attacks, or collusion scenarios.
6. Use failure attribution and monitoring papers to convert observations into actionable oversight signals.

**中文。** 这些论文可以形成一个 proposal 实验管线：

1. 用 MultiAgentBench 或 SILO-BENCH 构建可控多智能体任务。
2. 通过 G-Designer、图扩散或拓扑剪枝方法改变通信结构。
3. 使用 Emergent Coordination 中的信息论指标测量涌现协同。
4. 用拓扑感知的信息流分析追踪错误传播。
5. 通过故障智能体、提示攻击、协议攻击或合谋场景进行压力测试。
6. 用失败归因和监控方法把观测结果转化为可干预的监督信号。
