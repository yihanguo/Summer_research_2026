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

## Top 20 Representative Benchmark Definitions

This section gives operational definitions for 20 representative and commonly used benchmarks from the survey table. “Definition” states what the benchmark is designed to measure; “evaluation unit” states what one test instance looks like; “success signal” states how a run is judged; and “example” gives a concrete task shape.

### 1. AgentBench

- **Definition:** AgentBench is a multi-environment benchmark for evaluating LLMs as autonomous agents in interactive, multi-turn settings, especially their reasoning, decision-making, instruction following, and long-horizon action ability.
- **Evaluation unit:** One task instance in one of several interactive environments, such as web shopping, operating-system interaction, database work, games, house-holding, knowledge-graph reasoning, digital-card-game play, or lateral-thinking puzzles.
- **Success signal:** Environment-specific success rate or task-completion score, often based on whether the final state or answer satisfies the task.
- **Example:** The agent receives a web-shopping instruction such as finding a product with specified constraints, navigates the site, compares candidates, and submits the item that satisfies the user’s requirements.

### 2. GAIA

- **Definition:** GAIA is a benchmark for general AI assistants, built from real-world questions that require robust combinations of reasoning, web browsing, multimodal interpretation, and tool use.
- **Evaluation unit:** One question with a short, unambiguous answer, usually requiring external information gathering and multi-step reasoning.
- **Success signal:** Exact or normalized match to the gold answer.
- **Example:** The assistant must identify a specific factual answer by searching the web, reading multiple sources, doing a small calculation or comparison, and returning a concise final value.

### 3. WebArena

- **Definition:** WebArena is a realistic and reproducible web environment for evaluating language-guided agents on long-horizon website tasks.
- **Evaluation unit:** One natural-language task in self-hosted websites modeled on common domains such as e-commerce, forums, collaborative software development, and content management.
- **Success signal:** Functional correctness of task completion, usually checked through website state or environment-specific validators.
- **Example:** The agent is asked to edit an issue, post a comment, configure a setting, buy an item, or find information inside a hosted web application.

### 4. VisualWebArena

- **Definition:** VisualWebArena extends realistic web-agent evaluation to visually grounded tasks where text-only page representations are insufficient.
- **Evaluation unit:** One web task requiring image-text perception, visual grounding, instruction interpretation, and browser actions.
- **Success signal:** Whether the final web state satisfies the user objective.
- **Example:** The agent must use visual cues on a product page or content-management interface, identify the correct item or control, and complete a web action that cannot be solved reliably from text alone.

### 5. Mind2Web

- **Definition:** Mind2Web is a dataset and benchmark for training and evaluating generalist web agents that follow language instructions on real websites across many domains.
- **Evaluation unit:** One open-ended web task with a recorded crowdsourced action sequence on a real website.
- **Success signal:** Element selection accuracy, action prediction accuracy, and task-level trajectory matching against the reference action sequence.
- **Example:** Given “find the refund policy for this order” on a real e-commerce site, the model must choose the correct page elements and actions in sequence.

### 6. OSWorld

- **Definition:** OSWorld is a scalable real-computer benchmark for multimodal agents performing open-ended tasks across operating systems and desktop applications.
- **Evaluation unit:** One desktop-computer task with an initial machine state, executable environment, and evaluation script.
- **Success signal:** Execution-based verification of the final computer state.
- **Example:** The agent opens desktop apps, manipulates files, uses a browser or office application, and leaves the system in a target state checked by a script.

### 7. AndroidWorld

- **Definition:** AndroidWorld is a dynamic benchmark environment for autonomous agents controlling Android devices and apps.
- **Evaluation unit:** One parameterized natural-language task over real Android apps, with initialization, success-checking, and teardown logic.
- **Success signal:** Programmatic inspection of the Android device or app state after execution.
- **Example:** The agent receives a task such as creating a calendar event, sending or editing app content, changing a setting, or retrieving information from an Android app.

### 8. SWE-bench

- **Definition:** SWE-bench is an evaluation framework for testing whether language-model agents can resolve real-world software-engineering issues.
- **Evaluation unit:** One GitHub issue paired with a repository snapshot, where the agent must edit the codebase.
- **Success signal:** The generated patch passes the benchmark’s hidden or provided tests for that issue.
- **Example:** The agent reads a bug report from a Python project, modifies multiple files if needed, and produces a patch that fixes the failing behavior.

### 9. MLE-bench

- **Definition:** MLE-bench evaluates AI agents on machine-learning engineering tasks derived from Kaggle competitions.
- **Evaluation unit:** One ML competition task requiring data preparation, modeling, experiment execution, and submission generation.
- **Success signal:** Competition score compared with Kaggle leaderboard baselines, such as whether the agent reaches a medal-level threshold.
- **Example:** The agent receives a tabular prediction competition, writes training/evaluation code, runs experiments, and submits predictions for scoring.

### 10. PaperBench

- **Definition:** PaperBench evaluates whether AI agents can replicate modern AI research papers from scratch.
- **Evaluation unit:** One ICML 2024 Spotlight or Oral paper replication task, decomposed into many rubric-graded subtasks.
- **Success signal:** Hierarchical rubric score over paper understanding, codebase implementation, experiment execution, and result reproduction.
- **Example:** The agent reads a paper, implements the described method, runs experiments, produces outputs, and is graded against author-informed replication criteria.

### 11. ToolBench

- **Definition:** ToolBench is a large-scale tool-use benchmark/dataset built around real-world APIs, designed to evaluate whether LLMs can select and compose tools to satisfy instructions.
- **Evaluation unit:** One instruction that may require one or more API calls, together with available API documentation and expected solution path behavior.
- **Success signal:** Tool-use success as judged by ToolEval or related automatic evaluation, including whether the selected API sequence solves the instruction.
- **Example:** The agent is asked to retrieve travel, finance, weather, or media information by choosing relevant APIs and chaining their outputs.

### 12. BFCL

- **Definition:** BFCL, the Berkeley Function-Calling Leaderboard, evaluates structured function-calling ability: selecting the correct function, producing valid arguments, and handling calls across languages and invocation formats.
- **Evaluation unit:** One prompt plus function schema or tool specification, where the model must output the appropriate function call or calls.
- **Success signal:** AST-level matching, executable correctness, or response comparison depending on the test category.
- **Example:** Given a set of functions for flights, hotels, or database queries, the model outputs the exact function name and JSON-style arguments needed to satisfy the user request.

### 13. AppWorld

- **Definition:** AppWorld is a controllable execution environment and benchmark for interactive coding agents operating over multiple simulated everyday apps and APIs.
- **Evaluation unit:** One natural-language digital task in an app ecosystem with APIs, app state, users, and executable code.
- **Success signal:** Programmatic state-based unit tests that check both successful completion and absence of unintended collateral changes.
- **Example:** The agent writes and runs code that coordinates notes, shopping, messaging, or calendar APIs to complete a household or office task.

### 14. tau-bench

- **Definition:** tau-bench evaluates tool-using agents in realistic user-agent conversations governed by domain policies and API-backed state.
- **Evaluation unit:** One simulated user conversation in a domain such as retail or airline service, where the agent must talk to the user and call tools.
- **Success signal:** Final database state compared with the annotated goal state; repeated-trial reliability can be measured with pass^k.
- **Example:** The agent handles a flight-change or refund request by asking the user for missing information, applying policy rules, and updating backend state through tools.

### 15. LongMemEval

- **Definition:** LongMemEval evaluates long-term interactive memory in chat assistants across sustained user-assistant histories.
- **Evaluation unit:** One question embedded in a scalable multi-session chat history.
- **Success signal:** Accuracy on memory-dependent answers, including information extraction, multi-session reasoning, temporal reasoning, knowledge updates, and abstention.
- **Example:** After many sessions, the assistant must answer a question about a user preference that changed over time and avoid using outdated information.

### 16. MemoryAgentBench

- **Definition:** MemoryAgentBench evaluates memory agents in incremental multi-turn interactions, focusing on accurate retrieval, test-time learning, long-range understanding, and selective forgetting.
- **Evaluation unit:** One multi-turn memory scenario transformed from long-context or newly constructed datasets into incremental interaction form.
- **Success signal:** Task accuracy over the four memory competencies, often under different memory-system designs such as context-only, RAG, external memory, or tool-integrated agents.
- **Example:** The agent gradually receives information over turns, later must retrieve the relevant fact, incorporate newly learned information, and ignore obsolete or irrelevant memory.

### 17. LLM-Coordination

- **Definition:** LLM-Coordination evaluates coordination abilities of LLM agents in pure coordination games and coordination-question-answering settings.
- **Evaluation unit:** Either one agentic coordination episode in a game or one multiple-choice coordination QA item.
- **Success signal:** Game reward/success for agentic coordination, and QA accuracy over environment comprehension, theory-of-mind reasoning, and joint planning.
- **Example:** Two agents must infer a partner’s likely intent in a cooperative game such as Overcooked-style coordination and choose complementary actions without explicit centralized control.

### 18. MultiAgentBench

- **Definition:** MultiAgentBench evaluates LLM-based multi-agent systems across collaboration and competition scenarios, with explicit attention to orchestration, communication, planning, and milestone progress.
- **Evaluation unit:** One multi-agent task scenario, such as research, coding, database analysis, bargaining, or social deduction.
- **Success signal:** Milestone-based KPIs, task score, communication score, planning score, coordination score, or competition outcome depending on the task.
- **Example:** A team of specialized agents must complete a research-analysis task, exchange intermediate findings, coordinate roles, and produce a final artifact scored by milestone completion.

### 19. Who&When

- **Definition:** Who&When is a failure-attribution dataset and benchmark for LLM multi-agent systems, asking which agent caused a task failure and at which decisive step.
- **Evaluation unit:** One failed multi-agent execution log with fine-grained annotations linking the failure to a responsible agent and error step.
- **Success signal:** Accuracy in identifying the failure-responsible agent and the decisive failure step.
- **Example:** Given a failed multi-agent task transcript, the attribution model must identify that the planner agent made the first harmful decomposition at step 4 rather than blaming a later executor that merely propagated the error.

### 20. AgentHarm

- **Definition:** AgentHarm measures harmfulness and jailbreak robustness for LLM agents that can use tools and execute multi-stage tasks.
- **Evaluation unit:** One malicious agentic request, often with augmented jailbreak variants, spanning harm categories such as cybercrime, fraud, or harassment.
- **Success signal:** Whether the agent refuses harmful requests, and whether a jailbroken agent maintains enough capability to complete the harmful multi-step task.
- **Example:** The benchmark presents a harmful tool-enabled request and checks whether the agent refuses rather than using tools to carry out the malicious objective.

## Source Links for Top 20 Definitions

- AgentBench: https://arxiv.org/abs/2308.03688
- GAIA: https://arxiv.org/abs/2311.12983
- WebArena: https://arxiv.org/abs/2307.13854
- VisualWebArena: https://arxiv.org/abs/2401.13649
- Mind2Web: https://arxiv.org/abs/2306.06070
- OSWorld: https://arxiv.org/abs/2404.07972
- AndroidWorld: https://arxiv.org/abs/2405.14573
- SWE-bench: https://arxiv.org/abs/2310.06770
- MLE-bench: https://arxiv.org/abs/2410.07095
- PaperBench: https://arxiv.org/abs/2504.01848
- ToolBench / ToolLLM: https://arxiv.org/abs/2307.16789
- BFCL: https://gorilla.cs.berkeley.edu/leaderboard.html
- AppWorld: https://arxiv.org/abs/2407.18901
- tau-bench: https://arxiv.org/abs/2406.12045
- LongMemEval: https://arxiv.org/abs/2410.10813
- MemoryAgentBench: https://arxiv.org/abs/2507.05257
- LLM-Coordination: https://arxiv.org/abs/2310.03903
- MultiAgentBench: https://arxiv.org/abs/2503.01935
- Who&When: https://arxiv.org/abs/2505.00212
- AgentHarm: https://arxiv.org/abs/2410.09024
