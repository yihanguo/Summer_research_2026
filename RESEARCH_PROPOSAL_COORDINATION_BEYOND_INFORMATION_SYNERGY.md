# When More Agents Know More but Perform Worse

## A Structure-Aware Theory and Evaluation Framework for Coordination in Multi-Agent Language-Model Systems

**Author:** Yihan (Andy) Guo  
**Target venue:** ICML 2027  
**Target submission window:** January 2027  
**Status:** Research proposal

## Research Question

> Under an equal computation budget, when do multi-agent language-model systems convert informational interdependence and interaction structure into performance gains over a single agent?

## Concrete Positive-Information Failure Scenario: Werewolf-Style Hidden-Role Game

Consider a 12-player Werewolf-style hidden-role game with three werewolves, one Seer, one Guard, seven villagers, and a short fixed horizon. Four village analyst agents each receive a different truthful fragment of the night and voting history. Every fragment is individually useful and increases the likelihood that Player 5 is a werewolf, but each fragment alone leaves multiple candidates. For example, the four fragments may restrict the candidate sets to `{2,5,8}`, `{1,5}`, `{5,6,9}`, and `{3,5}`. Only their intersection identifies Player 5, so no single agent can obtain the decisive identification without combining the other agents' information. The joint evidence therefore has positive information gain and positive synergy, while every clue remains true and directionally helpful.

Suppose the communication protocol requires agents to publicly disclose both their evidence and its provenance. The village correctly eliminates Player 5, but the werewolves infer which agent is the Seer from the distinctive evidence pattern and kill that agent during the following night. In the remaining rounds, the village loses its only source of future hard evidence. Its final win probability can therefore be lower than under an anonymized, lower-information protocol that does not combine the raw clues publicly and keeps the Seer hidden. The performance loss is caused by strategic leakage and finite-horizon utility, not misinformation: more internal information improves role identification while making the group easier for the adversary to exploit. This is a strategic-information failure, rather than a claim that additional information hurts an ideal Bayesian decision-maker with no disclosure cost or adversary.

## Abstract

Multi-agent language-model systems (MAS) are often motivated by the expectation that multiple agents can pool information, specialize, cross-check one another, and outperform a single agent. Yet additional agents and communication can also introduce redundancy, correlated errors, anchoring, conflict, coordination overhead, and error cascades. Consequently, a system may exhibit strong internal dependence or information-theoretic synergy without achieving better task performance under a matched computation budget.

This project asks when measurable coordination is genuinely useful. It proposes a controlled framework that jointly measures (1) information-based coordination, using time-delayed mutual information and partial information decomposition; (2) graph- and topology-based coordination, using dynamic interaction networks, role differentiation, influence concentration, path efficiency, and robustness; and (3) task-level utility under equal token, inference, latency, and tool-use budgets. The central hypothesis is that information-theoretic synergy is evidence of interdependence, not a sufficient certificate of beneficial collaboration. Structural coordination measures should explain when information is routed, integrated, and corrected effectively, and a combined coordination profile should predict the regions in which MAS outperform compute-matched single-agent baselines.

The project will construct tasks in which agents collectively possess more relevant information than any individual agent but can nevertheless underperform. It will vary topology, communication protocol, agent heterogeneity, task decomposability, uncertainty, and adversarial noise. The intended contributions are a formal distinction between coordination, useful coordination, and collective performance; a compute-controlled benchmark; structure-aware metrics and phase diagrams; and a budget-aware policy for deciding whether and how to invoke multiple agents.

## 1. Motivation

The success of an MAS is usually evaluated through final accuracy, reward, or success rate. These outcomes do not reveal whether agents genuinely coordinated, merely duplicated one another, or benefited from increased computation. Conversely, emerging work measures internal coordination through predictive information and synergy. Such measures identify higher-order dependence, but dependence alone need not be helpful: agents can jointly predict an incorrect consensus, amplify a shared misconception, or spend their budget negotiating instead of solving the task.

This creates a central scientific and practical gap:

> We lack a compute-controlled theory that connects internal coordination measurements to the conditions under which multi-agent systems outperform single agents.

Understanding this connection matters for both capability and safety. A monitor should distinguish productive specialization from redundant communication, correlated failure, deceptive alignment, or unstable cascades. A system designer should also know when the extra coordination cost is justified.

## 2. Research Gap

### 2.1 Performance is not evidence of coordination

A group may outperform a single agent because it receives more tokens, more samples, more tool calls, or a stronger aggregation mechanism. Without equal-computation controls, the gain cannot be attributed to collaboration.

### 2.2 Information-theoretic coordination is not necessarily useful coordination

Time-delayed mutual information and partial information decomposition can detect predictive dependence, redundancy, unique information, and synergy. However, high synergy may coexist with low accuracy if the joint dynamics encode a stable but wrong strategy. Existing measurements therefore require an explicit link to task utility.

### 2.3 Pairwise statistics may miss system structure

Pairwise synergy can miss higher-order organization, asymmetric influence, bottlenecks, modular specialization, hierarchy, temporal changes, and cascading failures. Two systems can have similar aggregate synergy but route information through very different interaction structures.

### 2.4 Topology is usually treated as a design choice rather than a measured mechanism

Many studies compare debate, voting, hierarchical, or fully connected protocols, but do not identify which structural properties cause success or failure. A graph-based account could reveal whether useful collaboration depends on diversity of information paths, stable specialization, balanced influence, or rapid corrective feedback.

### 2.5 There is no general guarantee that MAS should beat a single agent

For arbitrary tasks and agents, no unconditional guarantee is plausible. Communication can be noisy, agents can share the same failure mode, and coordination consumes budget. A more defensible goal is to derive sufficient conditions, empirical decision rules, and calibrated abstention policies that identify when MAS deployment is likely to help.

## 3. Core Research Question

**Under an equal computation budget, when do multi-agent language-model systems convert informational interdependence and interaction structure into performance gains over a single agent?**

### Subquestions

1. Can agents collectively receive more task-relevant information than a single agent yet perform worse because of coordination failure?
2. When does information-theoretic synergy track useful collaboration, and when does it measure interdependence without utility?
3. Do graph- and topology-based measurements predict MAS performance beyond information-theoretic measurements?
4. Which task, agent, and network conditions produce transitions from beneficial collaboration to redundancy, interference, or cascade failure?
5. Can a combined coordination profile yield a reliable policy that selects a single-agent or multi-agent configuration before spending the full inference budget?
6. What restricted assumptions support sufficient conditions or lower bounds for MAS advantage?

## 4. Definitions

Let a task instance be \(x\), the answer or optimal action be \(y\), and the total inference budget be \(B\). Let \(S_B\) denote a single-agent system and \(M_{B,G,P}\) a multi-agent system with matched budget \(B\), interaction graph \(G\), and communication protocol \(P\).

### 4.1 Multi-agent advantage

\[
\Delta_{\mathrm{MAS}} = \mathbb{E}[U(M_{B,G,P}(x),y)] - \mathbb{E}[U(S_B(x),y)],
\]

where \(U\) is task utility. Beneficial collaboration requires \(\Delta_{\mathrm{MAS}} > 0\) with uncertainty bounds that exclude zero.

### 4.2 Coordination

Coordination is statistically detectable dependence among agents' states or actions that cannot be explained by independent responses to the task alone.

### 4.3 Useful coordination

Useful coordination is the component of coordination that causally improves task utility relative to appropriate independent, shuffled, topology-ablated, and compute-matched controls.

### 4.4 Coordination efficiency

\[
\eta_{\mathrm{coord}} = \frac{\Delta_{\mathrm{MAS}}}{C_{\mathrm{comm}} + C_{\mathrm{extra\ inference}}},
\]

where the denominator measures the incremental cost of communication and additional inference. This prevents a small gain purchased with a disproportionately large coordination budget from being labeled efficient.

## 5. Hypotheses

### H1: More collective information can produce worse performance

When information is partitioned across agents, the group will sometimes have higher oracle-accessible information than any single agent but underperform because communication loss, anchoring, premature consensus, or aggregation errors prevent effective integration.

### H2: Synergy is necessary in some tasks but not sufficient for advantage

On tasks that require combining complementary evidence, successful MAS will show positive information synergy. However, high synergy alone will not guarantee positive multi-agent advantage because synergistic dynamics can encode incorrect or inefficient collective behavior.

### H3: Structural metrics add predictive value

Dynamic graph features—especially role differentiation, influence balance, path diversity, modularity, reciprocity, and recovery after perturbation—will predict performance beyond task difficulty, token count, redundancy, and synergy.

### H4: Useful coordination occupies a bounded regime

MAS gains will follow a non-monotonic relationship with communication density and coordination intensity. Sparse interaction may prevent information integration, while excessive interaction may create redundancy, conformity, and overhead. Intermediate, task-aligned structures should perform best.

### H5: Phase transitions occur as coordination load changes

Varying noise, adversarial-agent fraction, task coupling, graph connectivity, or communication cost will produce sharp transitions between independent behavior, productive specialization, consensus lock-in, and cascading failure.

### H6: A combined profile supports configuration selection

A model using early-run information and topology measurements will select between single-agent and multi-agent execution more reliably than policies based only on self-confidence, agent count, or information synergy.

## 6. Proposed Coordination Measurements

### 6.1 Information-theoretic measurements

For two agents \(i\) and \(j\), predictive information about a future joint state \(T_{ij,t+\ell}\) can be decomposed as

\[
I(\{X_{i,t},X_{j,t}\};T_{ij,t+\ell})
= UI_i + UI_j + Red_{ij} + Syn_{ij}.
\]

Following the attached paper, the study will calculate synergy at three related levels. First, the pairwise emergence-capacity measure uses the decomposition above. A positive \(Syn_{ij} > 0\) means that the two agents jointly provide predictive information about their future joint state that is not recoverable from either agent alone. This is evidence of joint predictive structure, not by itself evidence of task correctness or performance improvement.

Second, the practical macro criterion measures whether the current macrostate predicts its future better than the sum of the individual agents:

\[
S_{\mathrm{macro}}(\ell)
= I(V_t;V_{t+\ell})
- \sum_{k=1}^{n} I(X_{k,t};V_{t+\ell}).
\]

Here, \(V_t = f(X_t)\) is a macro-level group signal. A positive \(S_{\mathrm{macro}}(\ell)\) indicates that the macrostate has additional time-delayed predictive information beyond the sum of individual contributions. This is a coarse, order-agnostic emergence screen and is not equivalent to positive task utility.

Third, for a coalition of three agents, let

\[
I_3 = I((X_{i,t},X_{j,t},X_{k,t});V_{t+\ell})
\]

and define the predictive information of each pair as

\[
I_2^{(a,b)} = I((X_{a,t},X_{b,t});V_{t+\ell}).
\]

The triadic information gain over the most informative pair is

\[
G_3 = I_3 - \max\left\{I_2^{(i,j)}, I_2^{(i,k)}, I_2^{(j,k)}\right\}.
\]

A positive \(G_3\) means that no pair is sufficient to capture all of the information that the triplet provides about the future macro signal. Because this criterion is closer to a task-relevant group signal than pairwise emergence capacity, it will be reported separately, but it still does not guarantee higher final performance.

The study will measure:

- **Time-delayed mutual information:** persistence and temporal predictability of agent and group states.
- **Unique information:** task-relevant evidence contributed by one agent but not another.
- **Redundancy:** duplicated information that may improve robustness but can waste budget.
- **Synergy:** predictive information available only from agents jointly.
- **High-order synergy:** multivariate extensions or interaction-information approximations where sample size permits.
- **Task-conditioned information:** coordination remaining after conditioning on the shared prompt, task state, and public feedback.
- **Correctness-aligned synergy:** synergy about future correct evidence or actions, distinguished from synergy about arbitrary joint dynamics.

Surrogate tests will include identity shuffles, time/block shuffles, message permutations, and independent-agent controls to estimate finite-sample and common-input effects.

### 6.2 Graph- and topology-based measurements

Each run will generate a temporal, directed, weighted graph. Nodes are agents; an edge \(i \rightarrow j\) records communication, semantic influence, or causal effect from agent \(i\) to agent \(j\). Edge weights may combine message count, token flow, attention or citation, response similarity, counterfactual influence, and timing.

Candidate measurements include:

| Dimension | Example measurements | Interpretation |
|---|---|---|
| Connectivity | density, components, reachability | whether evidence can propagate |
| Efficiency | shortest-path efficiency, temporal path length | how quickly useful evidence reaches decisions |
| Influence | in/out-strength, centralization, Gini coefficient | whether one agent dominates the group |
| Specialization | role stability, structural equivalence, assortativity | whether differentiated roles emerge |
| Modularity | community structure, conductance | whether subteams divide work productively |
| Reciprocity | reciprocal edge weight, response balance | whether communication supports correction rather than broadcasting |
| Diversity | independent paths, effective resistance, spectral gap | robustness to bottlenecks and single-agent failure |
| Dynamics | graph edit rate, temporal motifs, convergence time | how organization changes during reasoning |
| Robustness | performance after node/edge removal or corruption | whether coordination survives perturbation |
| Error propagation | reproduction number, cascade size/depth | how rapidly incorrect claims spread |

### 6.3 Causal structural measurements

Observed graphs can confuse communication with influence. The project will therefore use controlled interventions:

- remove or delay selected messages;
- replace messages with semantically matched distractors;
- mask agent identities;
- rewire edges while preserving degree;
- remove central or peripheral agents;
- inject a correct minority signal or a plausible wrong signal;
- compare the actual trajectory with counterfactual aggregation.

The change in utility estimates the causal value of nodes, edges, messages, and motifs.

### 6.4 A combined coordination profile

Rather than collapse all behavior into one scalar, the primary representation will be

\[
\mathcal{C} = (Syn, Red, UI, D, R, E, M, Q, K),
\]

where \(D\) is differentiation, \(R\) robustness, \(E\) routing efficiency, \(M\) modularity, \(Q\) influence balance, and \(K\) communication cost. A secondary learned score may be used for prediction, but all results will also report the interpretable components.

## 7. Experimental Design

### 7.1 Experiment A: More information, worse outcome

Construct tasks in which evidence is distributed across agents and no individual observes the complete instance. An oracle aggregator using all private evidence establishes that the collective observations contain more answer-relevant information than any single view.

Manipulations will create coordination failures:

- one confident but incorrect early message;
- asymmetric speaking order;
- limited message bandwidth;
- lossy summarization;
- majority pressure;
- duplicated evidence mistaken for independent support;
- incompatible intermediate representations;
- adversarial or systematically biased agents.

The key result would be a region in which oracle collective information increases while realized MAS accuracy falls below a compute-matched single agent.

### 7.2 Experiment B: Information versus topology

Hold agents, tasks, and total budget fixed while changing only the communication graph:

- independent/no communication;
- star with a central coordinator;
- hierarchy/tree;
- ring;
- sparse random graph;
- small-world graph;
- fully connected graph;
- adaptive learned graph.

This isolates whether topology explains performance differences when information access and model capability are controlled.

### 7.3 Experiment C: Matched synergy, different structure

Search for or construct pairs of systems with similar aggregate synergy but different topology and outcomes. For example, one may have balanced modular specialization while another routes all information through a dominant, error-prone hub. This is the strongest direct test of whether graph metrics complement information-based measures.

### 7.4 Experiment D: Phase-transition mapping

Sweep the following axes:

- number of agents;
- communication density and rounds;
- task decomposability and coupling;
- evidence overlap and heterogeneity;
- model capability and diversity;
- noise and adversarial-agent fraction;
- memory and context-window constraints;
- tool availability;
- communication price.

For each setting, estimate performance, coordination profiles, variance across seeds, and failure regimes. Change-point detection and finite-size scaling analyses will test whether apparent transitions are robust rather than plotting artifacts.

### 7.5 Experiment E: Early routing policy

Use measurements from an inexpensive pilot round to predict the expected gain from continuing as an MAS. The policy chooses among:

1. continue with one agent;
2. use independent parallel samples with aggregation;
3. invoke a communicating MAS;
4. switch topology or terminate communication.

Evaluation will measure utility, regret relative to the best configuration, calibration, and compute saved.

## 8. Tasks and Benchmarks

The benchmark suite should span different coordination demands:

- **Complementary-evidence tasks:** private clues, distributed diagnosis, multi-document question answering.
- **Decomposable reasoning:** modular planning, coding with component interfaces, mathematical subproblems.
- **Coupled reasoning:** tasks where subanswers interact and independent decomposition can fail.
- **Verification tasks:** proposer-critic, debate, fact checking, and error localization.
- **Social-dilemma and negotiation tasks:** cooperation, bargaining, coalition formation, and collusion.
- **Sequential environments:** tool use, resource allocation, and partially observed planning.
- **Adversarial settings:** malicious minority agents, corrupted messages, and shared systematic bias.

At least one minimalist synthetic environment will enable controlled theory tests, while several established language-agent benchmarks will test external validity.

## 9. Equal-Compute Evaluation Protocol

All central claims will compare systems under a pre-registered budget vector rather than agent count alone:

\[
B=(\text{input tokens},\text{output tokens},\text{model calls},\text{tool calls},\text{wall time},\text{monetary cost}).
\]

Primary comparisons:

- one long single-agent trajectory;
- single-agent self-consistency with multiple independent samples;
- multi-agent independent samples plus voting;
- communicating homogeneous MAS;
- communicating heterogeneous MAS;
- oracle aggregation upper bound.

Budgets will be matched exactly where possible and reported transparently otherwise. The analysis will include quality-cost Pareto frontiers, not only a single nominal budget.

## 10. Analysis Plan

### 10.1 Predictive analysis

Fit hierarchical models predicting task utility from task difficulty, model family, budget, agent count, information measurements, graph measurements, and their interactions. The incremental value of graph features will be measured by held-out log loss, \(R^2\), rank correlation, and calibration improvement over information-only models.

### 10.2 Causal analysis

Randomized topology, speaking-order, message, and node interventions will estimate average treatment effects. Mediation analysis will test whether topology affects performance through evidence routing, differentiation, or error propagation.

### 10.3 Phase-transition analysis

Performance and coordination order parameters will be plotted across controlled sweeps. Candidate critical regions will be evaluated across agent counts, tasks, models, and random seeds, with uncertainty intervals and robustness to metric choices.

### 10.4 Generalization analysis

Train configuration-selection rules on some tasks and model families, then test transfer to unseen tasks, models, group sizes, and topologies. A useful coordination measurement should predict outcomes beyond the environment in which it was fitted.

## 11. Toward Conditional Performance Guarantees

The project will not claim a universal theorem that MAS always outperform single agents. Instead, it will investigate restricted sufficient conditions. A stylized result may assume:

1. agents receive conditionally independent informative signals;
2. the aggregation protocol is consistent;
3. communication preserves a bounded fraction of signal information;
4. correlated error remains below a threshold;
5. coordination cost is below the expected aggregation gain; and
6. the interaction graph meets connectivity and robustness conditions.

Under these assumptions, the goal is to derive a lower bound of the form

\[
\Delta_{\mathrm{MAS}} \geq G(\text{signal diversity},\text{routing efficiency},\text{aggregation quality})
- L(\text{correlated error},\text{communication loss},\text{coordination cost}).
\]

Positive advantage is certified only when the estimated gain term exceeds the loss term with adequate confidence. Empirically, the routing policy should abstain from MAS deployment when this condition is not supported.

## 12. Expected Contributions

1. **Conceptual:** a clear separation between statistical coordination, useful coordination, and collective task performance.
2. **Empirical:** controlled demonstrations that more collective information and higher synergy can coexist with worse performance.
3. **Methodological:** a joint information-theoretic and dynamic-graph measurement framework.
4. **Benchmarking:** an equal-compute evaluation protocol with oracle, independent-sampling, and communication controls.
5. **Scientific:** phase diagrams showing how coordination changes with topology, scale, noise, heterogeneity, and task coupling.
6. **Theoretical:** restricted sufficient conditions and bounds for positive MAS advantage.
7. **Practical:** an early routing policy that decides whether to use one agent, parallel independent agents, or a communicating MAS.
8. **Safety:** diagnostics for influence concentration, collusion, cascading errors, and fragile coordination.

## 13. Risks and Mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Scope is too broad | Theory, metrics, benchmarks, and routing may exceed one paper | Define a minimum publishable unit centered on matched-compute experiments and graph-vs-information prediction |
| Metrics are estimator-sensitive | PID and graph construction choices can change conclusions | Use multiple estimators, pre-register primary metrics, publish sensitivity analyses, and validate on synthetic ground truth |
| Graph edges are not causal | Message flow may not equal influence | Use message, node, order, and rewiring interventions |
| Compute matching is imperfect | Apparent MAS gains may reflect extra resources | Report a multidimensional budget and Pareto frontiers; include single-agent self-consistency |
| Synthetic results do not generalize | Controlled tasks may not reflect realistic agent workflows | Combine mechanistic synthetic tasks with established benchmarks and model families |
| Phase transitions are overstated | Sharp-looking curves can result from finite samples | Use repeated seeds, uncertainty intervals, change-point tests, and finite-size analyses |
| No universal guarantee is possible | Overclaiming would weaken the paper | Frame results as conditional guarantees and calibrated deployment rules |
| Model APIs change | Reproducibility may degrade | Cache prompts and outputs where permitted; report model versions and use open-weight replications when feasible |
| Coordination improves capability but harms safety | Higher task reward can hide collusion or deception | Report safety and capability outcomes separately and include adversarial monitoring tasks |

## 14. Minimum Publishable Unit and Stretch Goals

### Minimum publishable unit

- one controlled distributed-information benchmark;
- compute-matched single-agent, independent-sampling, and communicating-MAS baselines;
- PID/TDMI measurements;
- temporal interaction graphs and a small pre-registered structural metric set;
- evidence that topology predicts utility beyond synergy;
- at least one cross-task or cross-model replication.

### Stretch goals

- higher-order PID;
- formal performance bounds;
- learned adaptive topology;
- real-time monitoring dashboard;
- multi-model and open-weight replication at larger scale;
- a general early-exit/configuration-routing policy.

## 15. Timeline to an ICML 2027 Submission

| Period | Milestones and deliverables |
|---|---|
| July 2026 | Finalize research question; complete focused literature review; define terminology, causal diagram, and minimum publishable unit |
| August 2026 | Implement synthetic distributed-information environment; reproduce core TDMI/PID analyses; finalize compute-budget protocol |
| September 2026 | Implement communication topologies and temporal graph extraction; run pilot experiments and estimator validation |
| October 2026 | Run main Experiment A–C sweeps; identify matched-synergy/different-outcome cases; refine hypotheses based on preregistered criteria |
| November 2026 | Run phase-transition and adversarial experiments; add established benchmarks and cross-model replications |
| December 1–15, 2026 | Complete statistical analysis, causal ablations, robustness checks, and initial theory results |
| December 16–31, 2026 | Write full paper; create figures, appendices, reproducibility package, and internal draft |
| Early January 2027 | Obtain coauthor feedback; rerun critical checks; tighten claims and limitations |
| Mid-January 2027 | Finalize manuscript, code, data statements, and supplementary material; submit to ICML 2027 according to the official deadline |

## 16. Decision Criteria for Continuing the Direction

The direction should be prioritized if pilot experiments establish at least three results:

1. a reproducible regime in which collective information exceeds individual information but realized MAS performance is worse;
2. information synergy does not fully explain task utility under matched compute;
3. a small, interpretable set of structural measurements adds out-of-sample predictive or causal explanatory value;
4. the effect replicates across at least two task families or model settings; and
5. the analysis yields an actionable rule for choosing or modifying MAS configurations.

If graph measurements add no value after strong controls, that negative result remains informative: it would delimit when information-based coordination is sufficient and prevent unnecessary structural complexity.

## 17. Anticipated Paper Structure

1. Introduction and motivating failure case.
2. Related work on emergent coordination, information decomposition, network science, and compute-controlled agent evaluation.
3. Definitions of coordination, useful coordination, and MAS advantage.
4. Benchmark and equal-compute protocol.
5. Information-theoretic and graph-based measurements.
6. Main experiments and phase diagrams.
7. Conditional theory or deployment rule.
8. Safety implications, limitations, and conclusion.

## 18. Summary

This proposal does not assume that more agents are inherently better. It treats multi-agent collaboration as a resource-allocation and information-routing problem. Information-theoretic synergy identifies joint structure, while graph-based measurements describe how that structure is organized and whether it supports correction, specialization, and robust evidence integration. Their relationship to task performance must be tested under equal computation budgets.

The most defensible central claim is therefore:

> Information synergy can reveal that agents are jointly interdependent, but structure-aware and task-aligned measurements are needed to determine whether that interdependence constitutes useful collaboration.

Establishing this distinction would provide both a stronger scientific theory of collective language-model behavior and a practical basis for deciding when multi-agent systems should be deployed.
