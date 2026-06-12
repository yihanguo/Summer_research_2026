# Holistic Introduction to Benchmarks for LLM Agents and Multi-Agent Systems

Context: this file introduces the benchmarks and benchmark-like datasets mentioned in `MAS_LIFE_section_tables.md`, based on the survey **Beyond Individual Intelligence: Surveying Collaboration, Failure Attribution, and Self-Evolution in LLM-based Multi-Agent Systems** (`arXiv:2605.14892v2`).

The survey organizes the field with the LIFE progression:

- **Lay** the individual-agent capability foundation.
- **Integrate** agents through collaboration.
- **Find** faults through failure attribution.
- **Evolve** systems through autonomous self-improvement.

Benchmarks in this space are not interchangeable. A benchmark that tests web navigation cannot answer whether a multi-agent topology is well orchestrated; a failure-attribution dataset cannot tell whether a self-evolving system retains skills over time. The useful way to read the landscape is therefore by **evaluation target**, **environment realism**, **interaction horizon**, **observable signal**, and **diagnostic granularity**.

## Executive Map

| Evaluation target | Main question | Representative benchmarks/datasets | Typical observables |
|---|---|---|---|
| General agent capability | Can one agent reason, plan, use tools, and complete multi-step tasks? | AgentBench, GAIA, MINT, AgentBoard, TheAgentCompany | Success rate, exact match, subgoal completion, action trajectory |
| Web, OS, mobile, and app interaction | Can an agent operate realistic digital environments? | WebArena, VisualWebArena, Mind2Web, BrowseComp, OSWorld, AndroidWorld, Mobile-Bench, AppWorld, tau-bench | Browser/app state, execution trace, tool-call sequence, state verification |
| Code, software, science, and ML work | Can agents solve real technical tasks with code and experiments? | SWE-bench, Terminal-Bench, MLE-bench, MLAgentBench, CORE-Bench, ScienceAgentBench, PaperBench | Patch correctness, terminal trace, reproducibility, rubric/subgoal score |
| Tool and API use | Can agents select tools, call them correctly, and recover from errors? | ToolBench, API-Bank, T-Eval, BFCL, ToolSandbox, AppWorld, tau-bench | Function-call AST, execution result, tool sequence, milestone completion |
| Memory | Can agents remember, update, retrieve, and use information over long horizons? | LoCoMo, LongMemEval, MemoryAgentBench | Recall accuracy, entailment, abstention, multi-session task completion |
| Safety and security | Can agents avoid harmful behavior and handle adversarial/security tasks? | Cybench, AgentHarm, SaladData-style safety settings, adversarial self-play | Harmfulness, exploit/task success, safety/capability tradeoff |
| Multi-agent collaboration | Can multiple agents coordinate, communicate, specialize, and compete/cooperate? | LLM-Coordination, LLMArena, BattleAgentBench, MultiAgentBench, AgentClinic, AI Hospital/MVME, MAC Benchmark, REALM-Bench | Coordination score, communication score, KPI/milestone score, domain task success |
| Failure attribution | Can we identify the responsible agent, step, edge, module, or causal chain after a failure? | Who&When, TRAIL, AgentFail, AgentErrorBench, CORRECT-Error, AgentErrata, MP-Bench, TraceElephant | Agent/step localization, error category, causal-path accuracy, explanation quality |
| Self-evolution | Can systems improve, retain gains, and stay safe across iterations? | SWE-bench/rSDE-Bench, NegotiationGym, embodied sandboxes, safety datasets, method-specific math/code/QA tasks | Iterative improvement, retention, cost, diversity, safety, cross-task transfer |

## How to Read the Benchmark Landscape

### 1. Outcome-only benchmarks are no longer enough

Early LLM evaluation often asked only whether the final answer was correct. Agent benchmarks increasingly need to know **how** the agent got there: which actions were taken, which tool calls were issued, which subgoals were completed, and where execution drifted. This is why newer benchmarks emphasize action trajectories, execution traces, state verification, and subgoal metrics.

### 2. Environment realism increases diagnostic value but also cost

Static QA and math tasks are cheap and repeatable, but they underrepresent the deployment problem. Web, OS, mobile, terminal, CRM, and app-based benchmarks expose realistic failure modes such as wrong clicks, stale state, invalid API arguments, permission barriers, and long-horizon context loss.

### 3. Multi-agent benchmarks test organization, not just intelligence

A multi-agent system can fail even when every individual agent is strong. Collaboration benchmarks therefore ask whether roles are assigned well, communication is useful rather than noisy, orchestration topologies reduce coordination cost, and agents can resolve disagreement.

### 4. Failure-attribution benchmarks are the diagnostic layer

When a multi-agent run fails, we need to know whether the cause was an agent, a message, a tool call, a controller decision, a role assignment, or a propagated symptom. Attribution benchmarks make this measurable by labeling agents, steps, categories, paths, or causal structures.

### 5. Self-evolution needs longitudinal evaluation

Self-evolving systems cannot be judged from one task attempt. They need repeated episodes that measure improvement, retention, transfer, cost, safety, and whether adaptation fixes diagnosed failures instead of overfitting to a narrow benchmark.

## Individual-Agent Capability Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| AgentBench | Broad early benchmark for LLM-as-agent behavior across diverse environments. | Mixed tasks, multi-turn interaction. | Establishes a general-purpose agent evaluation baseline. | Broad coverage, but less realistic than later web/OS/app environments. |
| GAIA | General AI assistant benchmark combining reasoning, web, and tool use. | Web/tool-assisted questions. | Tests whether agents can solve tasks requiring multiple capabilities. | Often outcome-heavy; less granular than trajectory diagnostics. |
| MINT | Multi-turn tool-use and language-feedback evaluation. | Interactive tasks with tools and feedback. | Useful for studying iterative correction and tool-mediated reasoning. | Narrower than full operating-system or enterprise workflows. |
| AgentBoard | Analytical board for multi-turn LLM agents. | Mixed multi-turn tasks. | Adds subgoal-level progress signals, not only final success. | Still abstracts away many real deployment details. |
| TheAgentCompany | Enterprise-style long-horizon benchmark. | Web plus code in workplace-like settings. | Moves evaluation toward consequential office work. | Some details and environments may be harder to reproduce fully. |

## Web, OS, Mobile, and App Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| WebArena | Realistic self-hosted websites for web agents. | Long-horizon browser tasks. | Reproducible web environment with execution-based grading. | Primarily text/web-state focused. |
| VisualWebArena | Multimodal extension of WebArena. | Visual web tasks. | Tests visual grounding in realistic browsing. | Harder to evaluate and debug than text-only web tasks. |
| Mind2Web | Large-scale cross-website web navigation dataset. | Web action prediction/navigation. | Broad website coverage and generalization pressure. | Dataset-style evaluation may differ from full live browsing. |
| BrowseComp | Hard browsing benchmark with deeply entangled information retrieval. | Web research and retrieval. | Stresses long-chain search and information synthesis. | More retrieval-heavy than full transactional web automation. |
| OSWorld | Open-ended computer-use benchmark in real desktop environments. | Desktop OS tasks. | Measures multimodal agents acting in real computer states. | Environment setup and state verification are expensive. |
| AndroidWorld | Dynamic mobile environment benchmark. | Android app tasks. | Captures real mobile UI interaction and state changes. | Mobile automation can be brittle across versions/devices. |
| Mobile-Bench | Mobile-agent benchmark for app interaction. | Mobile multi-turn app tasks. | Complements AndroidWorld with mobile UI action evaluation. | Coverage depends on selected app/task set. |
| AppWorld | Controllable world of apps and users. | App/tool ecosystem with executable state. | Good bridge between API calls and realistic app workflows. | Synthetic app world may not cover all real app messiness. |
| tau-bench | Tool-agent-user interaction in realistic domains. | Dialogue plus tools. | Evaluates agents in user-facing tool-use loops. | Domain scope is narrower than open-ended OS/web tasks. |

## Code, Software, Science, and ML Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| SWE-bench | Software engineering issue resolution. | Real GitHub issues and patches. | De facto benchmark for coding agents that must modify repositories. | Patch success is high-value but computationally expensive. |
| Terminal-Bench | Terminal-based agent tasks. | Shell/terminal workflows. | Tests command-line competence and execution traces. | Smaller and more infrastructure-dependent. |
| MLE-bench | Machine-learning engineering tasks. | ML competitions/experiments. | Measures agents doing model/data experimentation. | Evaluation can be slow and resource intensive. |
| MLAgentBench | ML agent workflows. | Code and experiment automation. | Early benchmark for autonomous ML research loops. | Small scale relative to broader ML engineering needs. |
| CORE-Bench | Computational reproducibility benchmark. | Reproducing research artifacts. | Tests scientific reliability and executable reproduction. | Reproducibility can depend on fragile dependencies. |
| ScienceAgentBench | Data-driven scientific discovery. | Code, data, and scientific analysis. | Focuses on rigorous scientific-agent assessment. | Scientific tasks are hard to standardize across domains. |
| PaperBench | Reproducing AI research papers. | Code plus web plus rubric subgoals. | Evaluates long-horizon research replication, not just coding. | Small number of papers and high evaluation cost. |

## Tool and API-Use Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| ToolBench | Large-scale API-use evaluation. | Many API/tool calls. | Tests whether agents can select and compose external tools. | LLM-judge evaluation can introduce subjectivity. |
| API-Bank | Tool/API interaction benchmark. | API calls and dialogue. | Useful for basic tool-use competence. | Less realistic than app-state or live API environments. |
| T-Eval | Tool-use evaluation with step-level checks. | API/tool-call sequences. | Adds finer-grained tool invocation accuracy. | Still mostly tool-centric rather than full workflow-centric. |
| BFCL | Function-calling benchmark. | Structured function calls with AST/execution checks. | Strong for precise argument/schema correctness. | Function calling is only one part of agent behavior. |
| ToolSandbox | Stateful tool-use benchmark. | Dialogue plus tools with milestones. | Tests long-horizon, stateful tool use. | More complex to run and interpret than static function-call tests. |
| IFEval-FC | Instruction-following evaluation for function calling. | Function-call instruction constraints. | Probes robustness to instruction details in tool calls. | Narrower than full tool ecosystems. |

## Memory Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| LoCoMo | Very long-term conversational memory. | Long conversations with entailment/human checks. | Tests whether agents can remember over extended dialogue. | Conversation memory is not the same as action memory. |
| LongMemEval | Long-term interactive memory for chat assistants. | Multi-session memory update/retrieval. | Measures recall, updating, abstention, and long-term consistency. | Mostly assistant/dialogue oriented. |
| MemoryAgentBench | Incremental multi-turn agent memory evaluation. | Dialogue plus app/application interactions. | Couples memory with action-oriented agent tasks. | Newer benchmark; ecosystem maturity is still developing. |

## Safety, Security, and Risk Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| Cybench | Cybersecurity capability and risk evaluation. | Code plus terminal/security tasks. | Tests both useful security skill and risk exposure. | Safety interpretation depends on policy and task framing. |
| AgentHarm | Harmfulness benchmark for LLM agents. | Tool-use scenarios with harmful potential. | Measures whether tool-using agents avoid harmful actions. | Harm categories can evolve with policy and deployment context. |
| SaladData-style safety datasets | Safety behavior in generated or simulated settings. | Classification/safety tasks. | Useful as part of self-evolution safety checks. | Not always agentic or multi-agent by itself. |
| Adversarial self-play settings | Safety under co-evolution and adversarial pressure. | Multi-agent adversarial training/evaluation. | Important for self-evolving systems where unsafe strategies can emerge. | Hard to standardize and compare across implementations. |

## Multi-Agent Collaboration Benchmarks

| Benchmark | What it is for | Environment / task style | Why it matters | Main caveat |
|---|---|---|---|---|
| LLM-Coordination | Coordination abilities of multiple LLM agents. | Shared-goal coordination tasks. | Directly evaluates whether agents can share information and jointly plan. | Early benchmark; limited realism compared with domain simulations. |
| LLMArena | Dynamic multi-agent environments. | Games and incomplete-information settings. | Tests adaptability, competition, and sequential decision-making. | Game performance may not transfer to professional workflows. |
| BattleAgentBench | Cooperation and competition in MAS. | Zero-sum and non-zero-sum games. | Quantifies strategic cooperation/competition. | Strategic games emphasize adversarial dynamics over work tasks. |
| MultiAgentBench | Collaboration and competition of LLM agents. | Research, coding, database, bargaining, Werewolf-style tasks. | Evaluates orchestration, communication, planning, and coordination quality. | Broadness can make root-cause diagnosis difficult. |
| AgentClinic | Simulated clinical multi-agent benchmark. | Medical interaction and diagnosis. | Tests high-uncertainty, sequential, domain-specific coordination. | Simulated medicine is not clinical deployment validation. |
| AI Hospital / MVME | Multi-agent medical interaction simulator. | Hospital-style departments and doctors. | Evaluates medical multi-agent dialogue, examination, and diagnosis. | Domain realism depends on simulator assumptions. |
| MAC Benchmark | Multi-agent coordination benchmark family. | Planning/coordination tasks such as tours, ridesharing, scheduling. | Focuses on coordination under constraints and disruptions. | More planning-centric than natural-language collaboration. |
| REALM-Bench | Real-world planning benchmark for LLMs and MAS. | Long-horizon planning tasks. | Pushes MAS evaluation toward realistic planning. | Newer benchmark with still-developing adoption. |
| ALYMPICS | Game-theoretic playground for agent dilemmas. | Classic strategic/social dilemmas. | Useful for studying emergent cooperation/competition. | More behavioral-science flavored than task-completion oriented. |
| RTBAgent | Real-time bidding agent setting. | Competitive auction/bidding tasks. | Tests strategic adaptation in high-stakes sequential competition. | Domain-specific and less general. |
| NegotiationGym | Multi-agent social simulation for negotiation. | Bargaining/negotiation episodes. | Useful for self-optimization and social strategy evolution. | Negotiation success can be metric-sensitive. |

## Failure-Attribution Benchmarks and Datasets

| Dataset / benchmark | What it is for | Label granularity | Why it matters | Main caveat |
|---|---|---|---|---|
| Who&When | Automated failure attribution in LLM MAS. | Responsible agent plus critical step. | Establishes a core localization formulation. | Manual labels are expensive and may not capture full causal chains. |
| TRAIL | Fine-grained trajectory error analysis. | Step plus error type/category. | Moves beyond localization into category-level diagnosis. | Dataset scale is limited. |
| AgentFail | Platform-orchestrated agentic workflow failures. | Agent/root-cause category. | Connects execution failures to workflow configuration and orchestration. | Platform-specific assumptions may affect generality. |
| AgentErrorBench | Error categories and feedback for agent failures. | Category plus feedback. | Useful for studying where agents fail and how feedback can help. | Category labels may not identify causal propagation. |
| CORRECT-Error | Synthetic/semi-automatic error data for localization. | Step-level error schema. | Scales attribution data through generated failures and pattern transfer. | Synthetic failures may differ from natural failures. |
| AgentErrata | Synthetic failure/category dataset. | Agent plus category. | Provides scalable data for diagnostic modeling. | Synthetic construction can encode generation biases. |
| MP-Bench | Multi-perspective failure attribution. | Multi-step and multi-perspective labels. | Evaluates attribution beyond a single responsible step. | Newer benchmark; comparability is still emerging. |
| TraceElephant | Observability-focused attribution benchmark. | Agent plus step over full traces. | Highlights that incomplete logs bias attribution. | Requires richer trace collection than many systems currently keep. |

## Self-Evolution Evaluation Settings

Self-evolution is less standardized than single-agent or collaboration evaluation. The survey therefore treats many self-evolution “benchmarks” as **task environments** or **evaluation families** rather than one fixed leaderboard.

| Setting | What it is for | What to measure | Why it matters |
|---|---|---|---|
| SWE-bench / rSDE-Bench | Software-development self-improvement. | Patch success over iterations, regression avoidance, cost. | Concrete environment where textual gradients and evolving collaboration networks can be tested. |
| NegotiationGym | Social strategy self-optimization. | Negotiation outcome, adaptation, robustness to opponents. | Good for persistent prompt/profile or policy evolution. |
| Embodied sandboxes | Team adaptation in simulated physical/resource environments. | Navigation, resource use, team coordination, retention. | Tests whether agents can learn shared strategies beyond text-only tasks. |
| Safety datasets and adversarial self-play | Safety-aware self-improvement. | Capability gain, harmful behavior, deceptive strategy emergence. | Self-evolution can improve capability and risk at the same time. |
| Method-specific math/code/QA tasks | Controlled iterative optimization. | Accuracy, token cost, convergence, cross-task transfer. | Useful for algorithm comparisons, though less realistic. |

## Benchmark Selection Guide

| If the research question is... | Start with... | Add if you need realism or diagnosis |
|---|---|---|
| “Can a single agent solve complex tasks?” | AgentBench, GAIA, AgentBoard | WebArena, OSWorld, AndroidWorld, AppWorld |
| “Can an agent use tools correctly?” | BFCL, API-Bank, T-Eval | ToolSandbox, tau-bench, AppWorld |
| “Can an agent work on real code?” | SWE-bench, Terminal-Bench | MLE-bench, CORE-Bench, PaperBench |
| “Can an agent remember over time?” | LongMemEval, LoCoMo | MemoryAgentBench |
| “Can agents coordinate?” | LLM-Coordination, MultiAgentBench | BattleAgentBench, REALM-Bench, AgentClinic, AI Hospital |
| “Why did the MAS fail?” | Who&When, TRAIL | TraceElephant, MP-Bench, AgentFail |
| “Can the MAS improve itself?” | SWE-bench/rSDE-Bench, method-specific math/code/QA | NegotiationGym, embodied sandboxes, safety/adversarial self-play |
| “Is the agent safe under tool use?” | AgentHarm | Cybench, adversarial self-play, task-specific safety datasets |

## Cross-Benchmark Gaps

1. **Cross-capability coupling is undermeasured.** A stronger memory module can still hurt planning if retrieval adds irrelevant context; current benchmarks rarely isolate these interactions.
2. **Efficiency is inconsistently reported.** Token cost, latency, API cost, and human debugging time are often missing despite being central in real deployment.
3. **Attribution and evolution are weakly connected.** Few benchmarks test whether a diagnosed root cause leads to a targeted, durable system improvement.
4. **Multi-agent observability is not standardized.** Without full message/action/tool traces, attribution labels become unreliable.
5. **Longitudinal safety is immature.** Self-evolving agents need benchmarks that track whether capability gains produce unsafe strategies over repeated adaptation.

## Recommended Reading Path for the Group Meeting

1. Read the **Executive Map** to understand the benchmark families.
2. Skim the benchmark cards for the LIFE stage most relevant to the discussion.
3. Use the **Benchmark Selection Guide** to match future project ideas to evaluation suites.
4. Close with the **Cross-Benchmark Gaps** section, because those gaps are the most natural places to propose new research directions.

