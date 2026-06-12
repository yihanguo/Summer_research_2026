# Section-by-Section Tables for `2605.14892v2`

Paper: **Beyond Individual Intelligence: Surveying Collaboration, Failure Attribution, and Self-Evolution in LLM-based Multi-Agent Systems**  
arXiv: 2605.14892v2, dated May 15, 2026  
Prepared for: **Group Meeting Jun 12**

Notes:

- “Benchmarks used/cited” means benchmarks explicitly discussed in the section, or the benchmark family the paper maps to that subsection through its evaluation tables/figures.
- “Related 2025-2026 papers” prioritizes confirmed conference papers from the paper bibliography. Closely related preprints are labeled as such when no confirmed conference version was found.
- The paper’s organizing thesis is the LIFE progression: **Lay** individual capability, **Integrate** agents through collaboration, **Find** faults through attribution, and **Evolve** through self-improvement.

## Section 1: Introduction

| Subsection | Motivation | Benchmarks used/cited | Related 2025-2026 conference papers |
|---|---|---|---|
| 1 Introduction | Argues that individual LLM agents are insufficient for long-horizon, tool-rich, real-world work; multi-agent systems help but introduce error propagation, diagnosis, and self-improvement problems. | Uses motivating examples rather than benchmark tables; points forward to agent, collaboration, attribution, and evolution evaluations. | **Who&When** (ICML 2025) for failure attribution; **MultiAgentBench** (ACL 2025) for collaboration/competition; **Optima** (Findings ACL 2025) for MAS optimization. |

## Section 2: Individual Intelligence

| Subsection | Motivation | Benchmarks used/cited | Related 2025-2026 conference papers |
|---|---|---|---|
| 2.1 From LLM to LLM-based Agent | Defines an agent as an LLM wrapped with perception, memory, planning, and tool-use modules operating in a perception-action loop. | Not benchmark-specific; Section 2.6 maps this architecture to AgentBench, GAIA, WebArena, OSWorld, SWE-bench, ToolBench, AppWorld, LongMemEval, etc. | **AndroidWorld** (ICLR 2025) for mobile agents; **MemoryAgentBench** (ICLR 2026) for memory agents; related preprint: **TheAgentCompany** (2024/2025). |
| 2.2 Reasoning | Reviews how agents improve reasoning before, during, and after generation to make decisions robust enough for planning and tools. | Math/code/factual QA settings plus integrated agent benchmarks in Section 2.6. | Related preprints: **BrowseComp** (2025) for hard browsing reasoning; **ScienceAgentBench** (2025) for scientific reasoning/code workflows. |
| 2.2.1 Input-Stage Enhancement | Improve the prompt/input so the model starts with better task framing, decompositions, examples, constraints, or context. | Mainly evaluated through math, QA, web, and tool tasks; no dedicated subsection benchmark. | Related: **LongMemEval** (ICLR 2025) where retrieval/input construction affects long-term QA; related preprint: **PaperBench** (2025). |
| 2.2.2 Reasoning-Process Enhancement | Make intermediate reasoning more reliable through search, self-consistency, reflection, process rewards, or tree/MCTS-style exploration. | MATH/GSM-style reasoning, code tasks, web tasks, and agent suites such as AgentBoard and WebArena. | **AFlow** (ICLR 2025, cited in paper bibliography) for MCTS workflow search; related preprint: **FlowReasoner** (2025) for RL-trained meta reasoning workflows. |
| 2.2.3 Output-Stage Regulation | Detect, verify, or correct unreliable outputs after reasoning to reduce hallucination and unsafe/incorrect action. | Factuality/reliability metrics; safety/tool-use benchmarks such as AgentHarm and Cybench in Section 2.6. | Related preprints: **AgentHarm** (2025) and **Cybench** (2025). |
| 2.3 Memory | Frames memory as the bridge between isolated reasoning turns and persistent agent behavior across sessions and tasks. | LoCoMo, LongMemEval, MemoryAgentBench. | **LongMemEval** (ICLR 2025); **MemoryAgentBench** (ICLR 2026). |
| 2.3.1 Memory Formation | Convert observations, dialogue, actions, and outcomes into durable memory objects. | LoCoMo, LongMemEval, MemoryAgentBench. | **LongMemEval** (ICLR 2025); **MemoryAgentBench** (ICLR 2026). |
| 2.3.2 Memory Maintenance | Keep memory useful by updating, consolidating, forgetting, or resolving contradictions. | LongMemEval tests knowledge updates and abstention; MemoryAgentBench tests selective forgetting/test-time learning. | **LongMemEval** (ICLR 2025); **MemoryAgentBench** (ICLR 2026). |
| 2.3.3 Memory Retrieval and Utilization | Retrieve the right prior experience at the right time and integrate it into action selection. | LoCoMo, LongMemEval, MemoryAgentBench; also web/tool-agent benchmarks when memory affects task completion. | **LongMemEval** (ICLR 2025); **MemoryAgentBench** (ICLR 2026). |
| 2.4 Planning | Explains planning as decomposition plus sequencing/search over actions, subtasks, tools, and environmental states. | ALFWorld, ScienceWorld, AgentBoard, WebArena, OSWorld, AndroidWorld, PaperBench. | **AndroidWorld** (ICLR 2025); related preprints: **REALM-Bench** (2025), **PaperBench** (2025). |
| 2.4.1 Decomposition-Based Planning | Break complex tasks into subtasks/subgoals to reduce long-horizon complexity. | AgentBoard subgoal metrics, PaperBench rubric subgoals, ScienceWorld/ALFWorld long-horizon tasks. | Related preprints: **PaperBench** (2025), **REALM-Bench** (2025). |
| 2.4.2 Search-Based Planning | Explore, evaluate, prune, or backtrack over candidate plans/actions instead of committing greedily. | WebArena/VisualWebArena, OSWorld/AndroidWorld, SWE-bench, science/code agent tasks. | **AFlow** (ICLR 2025); **AndroidWorld** (ICLR 2025); related preprint: **FlowReasoner** (2025). |
| 2.5 Tool Use | Tool use turns agents from text-only reasoners into actors over APIs, code, software, and web/mobile environments. | ToolBench, API-Bank, T-Eval, BFCL, AppWorld, tau-bench, ToolSandbox, OSWorld, AndroidWorld. | **AndroidWorld** (ICLR 2025); related preprints: **BFCL** (2025), **ToolSandbox** (2025), **On the Robustness of Agentic Function Calling** (2025). |
| 2.5.1 Tool Capability Acquisition | Learn tool schemas, affordances, and reusable skills before invocation. | ToolBench/API-Bank; Section 2.5 also discusses SkillWeaver and SAGE. | Related preprints: **SkillWeaver** (2025), **SAGE** (2025). |
| 2.5.2 Tool Invocation | Select tools, fill arguments, handle results, and recover from tool errors. | BFCL, AppWorld, tau-bench, ToolSandbox. | **AndroidWorld** (ICLR 2025); related preprints: **BFCL** (2025), **tau-bench** (2024/2025-adjacent), **IFEval-FC** (2025). |
| 2.5.3 Tool Generalization | Transfer tool-use behavior to unseen tasks, tools, or environments. | BFCL new-tool/new-env settings, ToolSandbox, AppWorld, AndroidWorld. | Related preprints: **SkillWeaver** (2025), **SAGE** (2025), **On the Robustness of Agentic Function Calling** (2025). |
| 2.6 Evaluation | Shows that agent evaluation is moving from isolated outcomes to long-horizon, trajectory-level, state-verification, and subgoal metrics. | AgentBench, GAIA, MINT, AgentBoard, TheAgentCompany, WebArena, VisualWebArena, BrowseComp, OSWorld, AndroidWorld, SWE-bench, Terminal-Bench, BFCL, ToolSandbox, LoCoMo, LongMemEval, MemoryAgentBench, ScienceAgentBench, PaperBench, Cybench, AgentHarm. | **AndroidWorld** (ICLR 2025); **LongMemEval** (ICLR 2025); **MemoryAgentBench** (ICLR 2026). |
| 2.7 Discussion | Highlights unresolved coupling across reasoning, memory, planning, and tools; static benchmarks miss continuous adaptation and cross-module failure modes. | Reuses Section 2.6 benchmarks as evidence of gaps. | **MemoryAgentBench** (ICLR 2026) as a move toward interactive memory evaluation; related preprints: **ScienceAgentBench**, **PaperBench**, **AgentHarm** (2025). |

## Section 3: Multi-Agent Collaboration

| Subsection | Motivation | Benchmarks used/cited | Related 2025-2026 conference papers |
|---|---|---|---|
| 3 Multi-Agent Collaboration | Motivates MAS as a way to distribute capabilities across agents with roles, communication, orchestration, and interaction patterns. | Figure 5: LLM-Coordination, LLMArena, BattleAgentBench, MultiAgentBench, AgentClinic, MVME/AI Hospital, MAC Benchmark, REALM-Bench. | **MultiAgentBench** (ACL 2025); **LLM-Coordination** (Findings NAACL 2025); **AI Hospital** (COLING 2025). |
| 3.1 Role | Specialized roles reduce prompt conflicts and let agents cover heterogeneous skills, but role design and assignment become system-level variables. | MultiAgentBench, AgentClinic, AI Hospital, enterprise/medical collaboration benchmarks. | **AgentCourt** (Findings ACL 2025); **MultiAgentBench** (ACL 2025). |
| 3.1.1 Role Capability | Studies what each role can do and how specialization changes collective performance. | AgentClinic, AI Hospital, MultiAgentBench. | **AgentCourt** (Findings ACL 2025); **AI Hospital** (COLING 2025). |
| 3.1.2 Role Allocation | Decides which agents/roles should handle which subtasks, including dynamic allocation. | MultiAgentBench, REALM-Bench, MAC-style planning benchmarks. | **EvoAgent** (NAACL 2025); related preprint: **Auto-scaling LLM-based MAS** (2025). |
| 3.2 Communication | Communication carries intermediate beliefs, plans, critiques, and evidence, but also creates bandwidth and error-propagation risks. | LLM-Coordination, MultiAgentBench, BattleAgentBench. | **LLM-Coordination** (Findings NAACL 2025); **GemMAS** (EMNLP 2025). |
| 3.2.1 Communication Modes | Compares direct, broadcast, debate, discussion, and other exchange modes. | LLM-Coordination, LLMArena, MultiAgentBench. | **LLM-Coordination** (Findings NAACL 2025); **MultiAgentBench** (ACL 2025). |
| 3.2.2 Communication Protocols | Formalizes what messages contain, who can talk to whom, and when communication is allowed. | MultiAgentBench topology/protocol evaluations; LLM-Coordination. | **GemMAS** (EMNLP 2025); **OSC** (Findings EMNLP 2025, from paper bibliography). |
| 3.3 Orchestration | Orchestration controls task routing, agent scheduling, aggregation, and dependency management. | MultiAgentBench compares star/chain/tree/graph topologies; REALM-Bench tests planning/coordination. | **Optima** (Findings ACL 2025); related preprints: **Puppeteer** (2025), **G-Designer** (2024/2025-adjacent). |
| 3.3.1 Centralized Orchestration Topology | A controller/planner routes work and aggregates results, simplifying coordination but creating bottlenecks. | MultiAgentBench, enterprise workflows, REALM-Bench. | **Optima** (Findings ACL 2025); related preprint: **Puppeteer** (2025). |
| 3.3.2 Distributed Orchestration Topology | Agents locally decide communication/routing, improving robustness and scalability. | MultiAgentBench graph settings, LLMArena dynamic environments. | Related preprints: **AgentNet** (2025), **SELFORG** (2025). |
| 3.3.3 Hybrid Orchestration Topology | Mixes central control with local autonomy to balance efficiency, fault tolerance, and specialization. | MultiAgentBench topology comparisons. | Related preprints: **MASS** (2025), **Agentic Neural Networks** (2025). |
| 3.4 Interaction | Interaction patterns define whether agents cooperate, compete, debate, verify, or negotiate. | LLMArena, BattleAgentBench, MultiAgentBench, ALYMPICS, RTBAgent. | **MultiAgentBench** (ACL 2025); **AI Hospital** (COLING 2025). |
| 3.4.1 Information Flow | Tracks how information moves across roles and rounds, which determines both collaboration quality and traceability. | MultiAgentBench, LLM-Coordination, traceability-oriented role pipelines. | **MultiAgentBench** (ACL 2025); **LLM-Coordination** (Findings NAACL 2025). |
| 3.4.2 Interaction Patterns | Covers cooperative, competitive, debate, voting, negotiation, and adversarial dynamics. | LLMArena, BattleAgentBench, MultiAgentBench, NegotiationGym-style simulations. | **MultiAgentBench** (ACL 2025); related preprint: **NegotiationGym** (2025). |
| 3.5 Evaluation | Evaluates MAS by trajectory quality, coordination, communication, planning, milestone KPIs, domain task success, and efficiency. | LLM-Coordination, LLMArena, BattleAgentBench, MultiAgentBench, AgentClinic, AI Hospital/MVME, MAC Benchmark, REALM-Bench. | **MultiAgentBench** (ACL 2025); **LLM-Coordination** (Findings NAACL 2025); **AI Hospital** (COLING 2025). |
| 3.6 Discussion | Notes unresolved tradeoffs: specialization vs redundancy, richer communication vs more error propagation, and orchestration quality vs cost. | Same as Section 3.5; benchmarks still weak on causal diagnosis and adaptation. | **GemMAS** (EMNLP 2025); **MultiAgentBench** (ACL 2025). |

## Section 4: Multi-Agent System Failure Attribution

| Subsection | Motivation | Benchmarks used/cited | Related 2025-2026 conference papers |
|---|---|---|---|
| 4 Multi-Agent System Failure Attribution | Moves from “agents failed” to “which agent, step, edge, module, or causal chain produced the failure.” | Who&When, TRAIL, AgentFail, AgentErrorBench, CORRECT-Error, AgentErrata, MP-Bench, TraceElephant. | **Who&When** (ICML 2025); **SDBL** (AAAI 2026); **Interactive Debugging and Steering of MAS** (CHI 2025). |
| 4.1 From Collaboration to Diagnosis | Collaboration creates dependencies that make root causes hard to isolate; diagnosis must model agents, messages, actions, and states. | Who&When; attribution datasets in Table 9. | **Who&When** (ICML 2025); related preprint: **TraceElephant** (2026). |
| 4.1.1 Formal Expression of the Attribution Process | Formalizes attribution as mapping trajectories/failures to responsible agents, steps, categories, or causal structures. | Who&When, TRAIL, MP-Bench. | **Who&When** (ICML 2025); **SDBL** (AAAI 2026). |
| 4.2 Failure Taxonomy | Provides vocabulary for classifying what failed before applying methods. | AgentFail, AgentErrorBench, TRAIL. | **Who&When** (ICML 2025); related preprint: **AgentErrorBench** (2025). |
| 4.2.1 System Structure | Locates failures in agents, tools, roles, communication edges, controllers, or shared state. | AgentFail, AgentErrorBench, TraceElephant. | **Interactive Debugging and Steering of MAS** (CHI 2025); related preprint: **AgentFail** (2025). |
| 4.2.2 Execution Stages | Distinguishes failures during planning, communication, tool invocation, execution, aggregation, or verification. | TRAIL, Who&When, TraceElephant. | **Who&When** (ICML 2025); **SDBL** (AAAI 2026). |
| 4.2.3 Causal Lifecycle | Separates root causes from propagated symptoms and downstream failures. | MP-Bench, TraceElephant, causal attribution datasets. | **Who&When** (ICML 2025); related preprints: **CHIEF** (2026), **MP-Bench** (2026). |
| 4.3 Failure Attribution Methods | Organizes methods into data-driven, constraint-guided, and causal-inference families. | Table 8 method comparison plus Table 9 datasets. | **Who&When** (ICML 2025); **SDBL** (AAAI 2026); **Raffles** (UIST 2026). |
| 4.3.1 Data-driven Method | Learns attribution signals from logs, synthetic failures, cross-trajectory statistics, graph features, or online risk predictors. | Who&When, CORRECT-Error, AgentErrata; methods: CORRECT, GraphTracer, AgentAsk, Trajectory Guard. | **Who&When** (ICML 2025); related preprints: **GraphTracer**, **CORRECT**, **AgentAsk** (2025). |
| 4.3.2 Constraint-Guided Method | Narrows long trajectories with explicit diagnostic scopes, rules, error taxonomies, interventions, and validation steps. | SDBL, A2P/ABDUCT, DoVer, AgentRx, Role-Trace. | **SDBL** (AAAI 2026); **Interactive Debugging and Steering of MAS** (CHI 2025); related preprint: **DoVer** (2025). |
| 4.3.3 Causal-inference Method | Uses counterfactuals, interventions, causal graphs, and effect propagation to distinguish true causes from correlations. | CDC-MAS, CHIEF, AgentTrace, MP-Bench-style causal labels. | **Counterfactual individual-agent importance** (AAAI 2025); **Raffles** (UIST 2026); related preprint: **CHIEF** (2026). |
| 4.4 Failure Attribution Evaluation | Evaluation moves from small manual logs to larger synthetic/semiautomated datasets and composite metrics. | Who&When, TRAIL, AgentFail, AgentErrorBench, CORRECT-Error, AgentErrata, MP-Bench, TraceElephant. | **Who&When** (ICML 2025); **SDBL** (AAAI 2026); related preprints: **TraceElephant**, **MP-Bench** (2026). |
| 4.5 Discussion | Attribution remains hard because logs are long, ground truth is expensive, causal chains are hidden, and evaluation is not yet standardized. | Same Table 9 datasets; also points to online detection and intervention evaluations. | **Interactive Debugging and Steering of MAS** (CHI 2025); **Raffles** (UIST 2026). |
| 4.5.1 Core Challenges | Identifies difficulty in observability, causal ambiguity, annotation cost, cross-domain generalization, and online diagnosis. | TraceElephant, MP-Bench, Who&When. | **Who&When** (ICML 2025); related preprints: **TraceElephant**, **MP-Bench** (2026). |
| 4.5.2 Future Research Direction | Calls for attribution that is process-aware, causal, online, and directly linked to system repair/evolution. | Requires new closed-loop attribution/evolution benchmarks; existing datasets are partial. | **SDBL** (AAAI 2026); **Raffles** (UIST 2026); related preprint: **Trajectory Graph Copilot** (2025). |

## Section 5: Multi-Agent System Self-Evolution

| Subsection | Motivation | Benchmarks used/cited | Related 2025-2026 conference papers |
|---|---|---|---|
| 5 Multi-Agent System Self-Evolution | Closes the loop: after diagnosing failures, MAS should modify agents, communication, topology, memory, or system designs. | Tables 10-12 compare methods; Section 5.5 discusses SWE-bench/rSDE-Bench, NegotiationGym, embodied sandboxes, safety datasets. | **Optima** (Findings ACL 2025); **EvoAgent** (NAACL 2025); related preprints: **AgentBreeder**, **MaAS**, **MAS-GPT** (2025). |
| 5.1 From Attribution to Evolution | Argues that attribution should guide targeted improvement rather than remain post-hoc explanation. | Attribution datasets from Section 4 plus evolution task benchmarks. | **SDBL** (AAAI 2026) as attribution input; **Optima** (Findings ACL 2025) as evolution/optimization target. |
| 5.2 Formal Definition of MAS Self-Evolution | Defines transition mappings that update agent parameters, prompts, roles, topologies, memories, or whole system specifications over time. | Not a benchmark subsection; formal apparatus supports Tables 10-12. | **EvoAgent** (NAACL 2025); **Optima** (Findings ACL 2025). |
| 5.3 MAS Self-Evolution Taxonomy | Classifies evolution by locus: agentic, systemic, and meta. | Tables 10, 11, 12. | **Optima** (Findings ACL 2025); **EvoAgent** (NAACL 2025); related preprint: **Agentic Neural Networks** (2025). |
| 5.3.1 Agentic Self-Evolution | Improves individual agents via prompts/profiles, memories, or model parameters using reflection, RL, SFT, peer feedback, or environment reward. | Table 10; domains include QA, math, code, legal simulation, negotiation, safety, embodied tasks. | **Optima** (Findings ACL 2025); **AgentCourt** (Findings ACL 2025); related preprints: **CoMAS**, **NegotiationGym**, **ECL**. |
| 5.3.2 Systemic Self-Evolution | Changes organization: topology, team composition, and shared memory. | Table 11; evaluated on task success, communication cost, software dev, embodied collaboration, shared-memory tasks. | **EvoAgent** (NAACL 2025); related preprints: **MASS**, **AgentNet**, **G-Memory**, **LIET**, **ANN**. |
| 5.3.3 Meta Self-Evolution | Searches over complete MAS designs or trains generators that produce system designs. | Table 12; benchmarks include workflow/code/meta-design tasks and cost-performance comparisons. | Related preprints: **AgentBreeder**, **MAS-ZERO**, **FlowReasoner**, **MaAS**, **MAS-GPT** (2025). |
| 5.4 Analyzing Evolutionary Dynamics | Compares driving mechanisms using variation-selection-retention: reflection, RL, SFT, evolutionary algorithms, textual gradient, heuristic update. | Cross-method matrix in Table 13; task families include math, code, safety, embodied, and software engineering. | **Optima** (Findings ACL 2025); **EvoAgent** (NAACL 2025); related preprint: **AgentBreeder** (2025). |
| 5.5 Evaluation | Notes that self-evolution evaluation must measure improvement, retention, cost, diversity, and safety across repeated episodes. | SWE-bench/rSDE-Bench, NegotiationGym, embodied sandboxes, safety datasets such as SaladData/adversarial self-play. | **Optima** (Findings ACL 2025); **EvoAgent** (NAACL 2025); related preprints: **NegotiationGym**, **AgentBreeder**. |
| 5.6 Discussion | Open problems: catastrophic forgetting, benchmark leakage, unsafe self-improvement, lack of standardized long-term/evolutionary protocols, and weak links back to attribution. | Calls for standardized embodied/software/safety sandboxes and closed-loop LIFE benchmarks. | **SDBL** (AAAI 2026); **Raffles** (UIST 2026); related preprints: **AgentBreeder**, **MAS-GPT**, **MaAS**. |

## Quick Benchmark Map

| LIFE stage | Benchmark families emphasized in the paper | What they mainly test |
|---|---|---|
| Individual intelligence | AgentBench, GAIA, MINT, AgentBoard, WebArena, OSWorld, AndroidWorld, SWE-bench, BFCL, AppWorld, LongMemEval, MemoryAgentBench, ScienceAgentBench, PaperBench, Cybench, AgentHarm | Reasoning, planning, memory, tool use, web/OS/mobile/code/science/safety execution |
| Collaboration | LLM-Coordination, LLMArena, BattleAgentBench, MultiAgentBench, AgentClinic, AI Hospital/MVME, MAC Benchmark, REALM-Bench | Role specialization, communication, coordination, cooperation/competition, domain teamwork |
| Failure attribution | Who&When, TRAIL, AgentFail, AgentErrorBench, CORRECT-Error, AgentErrata, MP-Bench, TraceElephant | Responsible agent/step, error category, causal chain, explanation/process faithfulness |
| Self-evolution | SWE-bench/rSDE-Bench, NegotiationGym, embodied sandboxes, safety datasets, plus method-specific math/code/QA tasks | Improvement across iterations, retention, topology/team adaptation, cost, diversity, safety |

## Selected Online Sources Consulted

- AndroidWorld: https://arxiv.org/abs/2405.14573
- LongMemEval: https://arxiv.org/abs/2410.10813
- MemoryAgentBench: https://arxiv.org/abs/2507.05257
- MultiAgentBench: https://arxiv.org/abs/2503.01935
- LLM-Coordination: https://arxiv.org/abs/2310.03903
- Who&When failure attribution: https://arxiv.org/abs/2505.00212
- EvoAgent: https://arxiv.org/abs/2406.14228
- Optima: https://arxiv.org/abs/2410.08115
- PaperBench: https://arxiv.org/abs/2504.01848
- ScienceAgentBench: https://arxiv.org/abs/2410.05080
- On the Robustness of Agentic Function Calling: https://arxiv.org/abs/2504.00914
- IFEval-FC: https://arxiv.org/abs/2509.18420

