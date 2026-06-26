# Sources and Inclusion Notes

Date checked: 2026-06-26

## Scope

Included venues:

- ICML 2025-2026
- ICLR 2025-2026
- NeurIPS 2025-2026 where official accepted-paper metadata was available
- ACL 2025-2026
- EMNLP 2025-2026 where official proceedings were available

Excluded:

- workshops
- arXiv-only papers
- non-top-conference reports
- venues outside ICML / ICLR / NeurIPS / ACL / EMNLP

Note: EMNLP 2026 proceedings were not available in the checked official sources at the time of this report.

## Official Paper Links

### Emergence, coordination, and cooperation

- ICLR 2026: [Emergent Coordination in Multi-Agent Language Models](https://openreview.net/forum?id=SRn1MtMPRq)
- ACL 2025: [MultiAgentBench: Evaluating the Collaboration and Competition of LLM agents](https://aclanthology.org/2025.acl-long.421/)
- ACL 2026: [SILO-BENCH: A Scalable Environment for Evaluating Distributed Coordination in Multi-Agent LLM Systems](https://aclanthology.org/2026.acl-long.1354/)
- ICML 2026: [CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas](https://openreview.net/forum?id=369qOr0ZnJ)
- NeurIPS 2025: [Shapley-Coop: Credit Assignment for Emergent Cooperation in Self-Interested LLM Agents](https://openreview.net/forum?id=HnJ1UkuJXS)
- ICML 2026: [The Oversight Game: Learning to Cooperatively Balance an AI Agent's Safety and Autonomy](https://openreview.net/forum?id=Na3YzWMXwz)

### Communication, topology, and information flow

- EMNLP 2025: [Understanding the Information Propagation Effects of Communication Topologies in LLM-based Multi-Agent Systems](https://aclanthology.org/2025.emnlp-main.623/)
- ACL 2026: [Dynamic Generation of Multi LLM Agents Communication Topologies with Graph Diffusion Models](https://aclanthology.org/2026.acl-long.1764/)
- ICML 2025: [G-Designer: Architecting Multi-agent Communication Topologies via Graph Neural Networks](https://proceedings.mlr.press/v267/zhang25cu.html)
- ICML 2025: [Communicating Activations Between Language Model Agents](https://proceedings.mlr.press/v267/ramesh25a.html)
- NeurIPS 2025: [Thought Communication in Multiagent Collaboration](https://openreview.net/forum?id=tq9lyV9Cml)
- ICLR 2026: [Benefits and Limitations of Communication in Multi-Agent Reasoning](https://openreview.net/forum?id=0aPIVJUz5T)
- ACL 2025: [CoMet: Metaphor-Driven Covert Communication for Multi-Agent Language Games](https://aclanthology.org/2025.acl-long.389/)
- ICML 2026: [When LLMs Develop Languages: Symbolic Communication for Efficient Multi-Agent Reasoning](https://openreview.net/forum?id=ovpL0ujD6j)

### Safety, oversight, and failure attribution

- ICML 2025: [Which Agent Causes Task Failures and When? On Automated Failure Attribution of LLM Multi-Agent Systems](https://proceedings.mlr.press/v267/zhang25cq.html)
- ACL 2026: [TAMAS: Benchmarking Adversarial Risks in Multi-Agent LLM Systems](https://aclanthology.org/2026.acl-long.1442/)
- ACL 2025: [Agents Under Siege: Breaking Pragmatic Multi-Agent LLM Systems with Optimized Prompt Attacks](https://aclanthology.org/2025.acl-long.476/)
- ICLR 2026: [A2ASecBench: A Protocol-Aware Security Benchmark for Agent-to-Agent Multi-Agent Systems](https://openreview.net/forum?id=LfdFnakqGJ)
- NeurIPS 2025: [GUARDIAN: Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling](https://openreview.net/forum?id=6j9xJ9pBjm)
- ICLR 2026: [Reliable Weak-to-Strong Monitoring of LLM Agents](https://openreview.net/forum?id=WV7xIboTDK)
- ICML 2026: [Architecture Matters for Multi-Agent Security](https://openreview.net/forum?id=Jk4zLorDUx)
- NeurIPS 2025: [AgentAuditor: Human-level Safety and Security Evaluation for LLM Agents](https://openreview.net/forum?id=2KKqp7MWJM)

## Relation to proposal paragraph

The selected papers map to the proposal paragraph as follows:

- **Population size and heterogeneity:** MultiAgentBench, SILO-BENCH, CoopEval, Shapley-Coop.
- **Interaction topology:** Information Propagation, Dynamic Topology Generation, G-Designer, Architecture Matters.
- **Communication:** Communicating Activations, Thought Communication, Benefits and Limitations of Communication, CoMet, Symbolic Communication.
- **Safety-relevant properties:** TAMAS, A2ASecBench, Agents Under Siege, GUARDIAN, AgentAuditor.
- **Oversight and control:** Which Agent Causes Task Failures, Reliable Weak-to-Strong Monitoring, The Oversight Game.
- **Phase transitions and emergent collective behavior:** Emergent Coordination, Shapley-Coop, CoopEval, and the topology-generation papers provide the nearest current technical handles, though large-population phase-transition work remains underdeveloped.
