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

This project asks when measurable coordination is genuinely useful. It proposes a focused framework that measures (1) information-based coordination, using time-delayed mutual information and partial information decomposition; (2) a small set of topology variables that are assigned by the experiment rather than inferred from text embeddings; and (3) task-level utility under equal token, inference, and latency budgets. The central hypothesis is that information-theoretic synergy is evidence of interdependence, not a sufficient certificate of beneficial collaboration. The topology analysis will distinguish communication opportunity from observed message propagation and from causal influence, using randomized topology and message interventions rather than treating a graph encoder's representation as an explanation.

The project will construct one primary task in which agents collectively possess more relevant information than any individual agent but can nevertheless underperform, followed by one small external replication. The main topology comparison will use a bottlenecked and a balanced sparse protocol with the same agent count, edge budget, communication rounds, and token budget. A single near-benign message perturbation will test whether the topology result survives contamination. The intended contributions are a formal distinction between coordination, useful coordination, and collective performance; a compute-controlled benchmark; an interpretable and causally cautious topology analysis; and a test of whether topology adds explanatory value beyond information measurements.

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

### 2.4 Communication topology is not the same as influence

A communication graph records which messages can be delivered, not which claims an agent actually used or which message caused a decision. Message embeddings and graph encoders can also become unreliable when benign agents echo contaminated content or when near-benign messages overlap in representation space. A defensible topology analysis must therefore separate the assigned protocol graph, the observed message or claim lineage, and causal influence estimated by randomized interventions.

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

### H3: A small, pre-registered topology contrast may add explanatory value

After matching agent count, edge budget, communication rounds, and token budget, a balanced sparse protocol may differ from a bottlenecked protocol in evidence exposure, contamination spread, and final utility. This is an empirical test rather than an assumption: a topology feature will be retained only if it adds held-out explanatory value beyond task difficulty, synergy, redundancy, and message volume.

### H4: Matched topology can change utility without changing information access

With evidence, agents, edge budget, rounds, and token budget held fixed, the bottlenecked and balanced protocols may produce different exposure patterns and final utility. The direction and size of the effect are empirical.

### H5: Topology can change contamination without being a complete safety explanation

The near-benign stress test may produce different claim-propagation depth or contamination half-life across the two protocols. These results will be interpreted as protocol-specific propagation effects, not as a universal density law or a proof that graph structure alone explains safety.

### H6: Information measurements may be sufficient

If the four topology measurements add no held-out or randomized explanatory value beyond information measurements, the result will support a deliberately negative conclusion: topology is not necessary for this task under the tested protocol and budget.

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

### 6.2 Three-layer topology evaluation architecture

The topology analysis will use three explicitly separated objects rather than one learned temporal graph:

1. **Protocol graph \(G^{P}_r=(V,E^{P}_r)\):** the exogenously assigned communication opportunity at round \(r\). An edge means that a message may be delivered; it does not mean that the recipient used the message or that the sender caused the decision.
2. **Message log \(M_r\):** the observed messages with sender, recipient, round, token count, message ID, cited evidence IDs, decision, and model-internal confidence when available. Content representations are measurements attached to messages, not substitutes for the protocol graph.
3. **Claim-lineage graph \(G^{L}_r\):** an observed propagation record linking a claim to a later message only when the link is explicit in the synthetic task, an evidence ID is cited, or a controlled message replacement establishes the lineage. Semantic similarity alone will not be treated as proof of influence.

This separation directly addresses two risks. First, an edge in \(G^{P}_r\) is an opportunity for information flow, not an influence edge. Second, message embeddings can become non-separable after agents echo contaminated content or after a near-benign message enters the conversation. Embeddings may be used as one auxiliary content feature and as a robustness diagnostic, but never as the sole basis for declaring a message benign, anomalous, causal, or influential. The core evaluation will not rely on a GNN or graph autoencoder to produce an uninterpretable influence score.

### 6.3 Minimal pre-registered topology measurements

The primary topology analysis will use four interpretable quantities:

| Quantity | Operationalization | Claim supported |
|---|---|---|
| Temporal exposure | time and number of rounds before a claim reaches the decision node | whether a protocol makes evidence available quickly |
| Bottleneck concentration | share of delivered message tokens or claim paths passing through the most central node | whether one agent controls access to evidence |
| Claim propagation | lineage depth, breadth, repetition rate, and contamination half-life | whether a claim spreads or is repeatedly echoed |
| Redundant exposure | repeated delivery of the same claim after controlling for message count | whether communication adds independent evidence or repetition |

These are descriptive topology and propagation measures. The main claim about topology will come from randomized protocol assignment, not from correlating an observed metric with performance after the fact. Modularity, spectral measures, effective resistance, learned graph embeddings, and large topology sweeps are secondary or deferred unless the primary contrast shows a reproducible effect.

### 6.4 Causal topology interventions and safeguards

The main causal estimand will compare utility under randomized protocol interventions:

\[
ATE_{\mathrm{topology}}
= \mathbb{E}[U \mid do(G^{P}=G_{\mathrm{balanced}})]
- \mathbb{E}[U \mid do(G^{P}=G_{\mathrm{bottlenecked}})].
\]

Within a fixed protocol, message-level interventions will be limited to:

- gate or delay one assigned edge while preserving total token and call budgets;
- replace one message with a pre-registered content-matched control;
- remove a source node while preserving the remaining schedule;
- run one near-benign contamination condition to test propagation and signal decay.

The analysis will report utility, correctness, confidence, claim lineage, and safety outcomes together. A topology will not be called beneficial merely because it produces a cleaner embedding graph or higher agreement. It must improve the pre-registered task outcome or reduce measured contamination under matched resources, with uncertainty intervals that exclude the relevant null.

### 6.5 A compact coordination profile

The primary profile will be

\[
\mathcal{C}_{\mathrm{primary}}
= (Syn, Red, UI, Exposure, Bottleneck, Propagation, Cost).
\]

This profile keeps information structure, communication opportunity, observed propagation, and resource use distinguishable. Any learned predictor is secondary and must demonstrate held-out value over a simple information-only baseline.

## 7. Experimental Design

The core study is deliberately small. It contains one mechanistic benchmark, one primary topology contrast, one near-benign stress test, and one limited external replication. Large topology sweeps, learned graph architectures, phase-transition claims, and adaptive routing are stretch goals rather than requirements for the first paper.

### 7.1 Main mechanistic benchmark: truthful complementary information

Use the Werewolf-style hidden-role environment described at the beginning of the proposal. Four village analyst agents receive distinct, truthful fragments of a fixed game history. The fragments are designed so that each one is individually useful, but only their intersection identifies the decisive role. The game has a fixed horizon and reports both immediate identification accuracy and final village win probability.

The pre-registered comparisons are:

1. **Single-agent serialization:** one agent receives the complete tagged evidence packet under the same total token and model-call budget.
2. **Anonymous MAS aggregation:** the four agents share evidence IDs and a consensus without exposing source provenance.
3. **Provenance-revealing MAS:** the same evidence is shared with source identities and message history exposed.

The key test is whether the provenance-revealing condition has higher joint information and earlier role identification but lower final utility than the anonymous condition or the compute-matched single agent. This isolates strategic disclosure from misinformation. A secondary information-asymmetry comparison may give the single agent one evidence view while the MAS receives four, but it will be labeled as an information-access comparison rather than a clean causal comparison.

### 7.2 Minimal topology experiment

Within the same benchmark, randomly assign only two sparse directed protocols:

- **Bottlenecked:** most evidence must pass through one coordinator;
- **Balanced:** evidence is routed through a degree-balanced sparse graph.

The two protocols will have the same number of agents, edge count, allowed communication rounds, maximum message tokens, model calls, and decision deadline. A no-communication condition is included only as a sanity baseline. The primary estimand is the difference between the two assigned protocols; it will be interpreted as a bundled topology effect involving reachability and concentration, not as an isolated causal effect of one graph statistic.

The study will not sweep star, chain, ring, small-world, random, fully connected, and learned graphs in the main paper. A density sweep is a stretch check only if the primary contrast is reproducible.

### 7.3 One safety stress test

Repeat the primary topology contrast under one near-benign communication perturbation adapted from Lingxi Zhang et al.: a short malicious payload embedded in an otherwise task-focused message. This tests whether contamination propagates differently through the two protocols and whether early intervention changes the result. The study will log embeddings and token confidence as auxiliary signals, but it will not build or evaluate a new graph-based defense as part of the main contribution.

### 7.4 Limited external replication

Replicate the primary anonymous-versus-provenance contrast on one tagged distributed-evidence verification task, such as a small FEVER-style setting. Evidence IDs and claim provenance will be explicit so that lineage is observed rather than inferred from embedding similarity. This replication tests whether the mechanism is specific to hidden-role reasoning without opening a broad benchmark sweep.

### 7.5 Explicitly deferred experiments

The following are deferred unless the minimum study produces a stable effect:

- large topology and agent-count sweeps;
- learned adaptive graphs or graph neural network controllers;
- higher-order phase-transition mapping;
- multiple attack families;
- learned early-exit or topology-selection policies;
- broad model-family and tool-use comparisons.

## 8. Tasks and Benchmarks

The main benchmark is the controlled Werewolf-style hidden-role environment. It provides private evidence, explicit evidence IDs, a strategic opponent, a fixed horizon, and a natural distinction between anonymous aggregation and provenance disclosure. Its simulator will expose the complete event log so that claim lineage and the ground-truth source of each clue are known.

The only external replication is a small tagged fact-verification task in which evidence fragments are distributed across agents and every claim can be traced to an evidence ID. The replication is a falsification check, not a second benchmark program. Broader planning, coding, negotiation, tool-use, and multi-model suites are outside the minimum scope.

## 9. Equal-Compute Evaluation Protocol

All central claims will compare systems under a pre-registered budget vector rather than agent count alone:

\[
B=(\text{input tokens},\text{output tokens},\text{model calls},\text{wall time}).
\]

The primary comparisons are:

- single-agent serialization of the complete evidence packet;
- anonymous communicating MAS;
- provenance-revealing communicating MAS;
- the two matched sparse topology protocols.

The topology comparison will hold the evidence packet, agent prompts, number of rounds, edge count, maximum message tokens, and decision deadline fixed. Budgets will be matched exactly where possible and reported transparently otherwise. The analysis will report utility and cost together, not only a single nominal accuracy.

## 10. Analysis Plan

### 10.1 Primary outcome analysis

The primary outcome is final task utility, with immediate role-identification accuracy, village win probability, token cost, and latency reported separately. A hierarchical model will estimate the effects of information condition and assigned topology while controlling only for pre-registered task instance and seed effects. The central interaction is whether provenance exposure improves internal information measures but lowers final utility.

### 10.2 Topology and influence analysis

The topology effect will be estimated from randomized protocol assignment. Temporal exposure, bottleneck concentration, claim propagation, and redundant exposure will be analyzed as mechanisms, not as interchangeable predictors. Edge or message influence will be estimated only from the pre-registered gating, delay, replacement, and node-removal interventions:

\[
ATE_e = \mathbb{E}[U \mid do(e=1)] - \mathbb{E}[U \mid do(e=0)].
\]

Observational correlations between message embeddings, graph centrality, and accuracy will be reported as descriptive only. No graph encoder reconstruction score will be interpreted as causal influence.

### 10.3 Incremental value of topology

Compare held-out prediction from three nested models:

1. task difficulty and budget controls;
2. controls plus information measurements;
3. controls plus information measurements and the four pre-registered topology measurements.

Topology earns a substantive claim only if model 3 improves held-out prediction or explains a randomized utility difference without relying on post-outcome variables. If it does not, the result will be reported as evidence that topology is not needed for this task.

### 10.4 Replication and robustness

Repeat only the primary information-condition contrast and the two-protocol topology contrast on the tagged verification task. Report uncertainty intervals, estimator sensitivity for PID/TDMI, and robustness to the single near-benign perturbation. Phase-transition and broad generalization analyses are not required for the main claim.

## 11. Toward Conditional Performance Guarantees

The project will not claim a universal theorem that MAS always outperform single agents. Instead, it will investigate restricted sufficient conditions. A stylized result may assume:

1. agents receive conditionally independent informative signals;
2. the aggregation protocol is consistent;
3. communication preserves a bounded fraction of signal information;
4. correlated error remains below a threshold;
5. coordination cost is below the expected aggregation gain; and
6. the assigned protocol graph meets explicit reachability and bottleneck conditions.

Under these assumptions, the goal is to derive a lower bound of the form

\[
\Delta_{\mathrm{MAS}} \geq G(\text{signal diversity},\text{temporal exposure},\text{aggregation quality})
- L(\text{correlated error},\text{communication loss},\text{coordination cost}).
\]

Positive advantage is certified only when the estimated gain term exceeds the loss term with adequate confidence. This is a secondary theoretical direction, not a prerequisite for the empirical paper, and no learned routing policy is required to support the main claims.

## 12. Expected Contributions

1. **Conceptual:** a clear separation between statistical coordination, useful coordination, and collective task performance.
2. **Empirical:** controlled demonstrations that more collective information and higher synergy can coexist with worse performance.
3. **Methodological:** a layered topology evaluation that separates protocol opportunity, observed claim propagation, and intervention-based influence.
4. **Benchmarking:** an equal-compute protocol with single-agent serialization, anonymous aggregation, provenance disclosure, and one matched topology contrast.
5. **Safety:** a focused test of bottlenecks and near-benign contamination without assuming that embedding or graph reconstruction scores are causal.

## 13. Risks and Mitigations

| Risk | Why it matters | Mitigation |
|---|---|---|
| Scope is too broad | Theory, synergy metrics, topology, and safety could still exceed one paper | Make the hidden-role benchmark and one topology contrast the minimum publishable unit |
| Graph edges are not causal | Delivery opportunity may be mistaken for influence | Use assigned protocol graphs, explicit claim IDs, and randomized gating, delay, replacement, and node-removal interventions |
| Embedding signals self-mix | Near-benign messages and echoed content can erase embedding separability | Treat embeddings as auxiliary diagnostics; do not use them alone to infer influence or anomaly status |
| Topology effects are confounded | Edge count, rounds, tokens, and reachability can change together | Match edge budget, rounds, message limits, and deadline; interpret the primary contrast as a bundled protocol effect |
| PID/TDMI estimates are sensitive | Small samples and endogenous run length can create unstable synergy estimates | Pre-register early-window estimation, use synthetic ground truth, report estimator sensitivity, and avoid post-outcome windows |
| Synthetic results do not generalize | Hidden-role structure may not reflect ordinary reasoning tasks | Add one tagged fact-verification replication and keep claims mechanism-specific |
| No universal guarantee is possible | Strong claims would exceed the evidence | Frame the result as a conditional empirical relationship and a restricted bound |
| Model APIs change | Reproducibility may degrade | Cache prompts and outputs where permitted, report model versions, and use one open-weight model for confidence measurements |

## 14. Minimum Publishable Unit and Stretch Goals

### Minimum publishable unit

- one controlled Werewolf-style distributed-information benchmark;
- compute-matched single-agent serialization, anonymous MAS, and provenance-revealing MAS;
- PID/TDMI measurements with an early fixed window;
- one randomized bottlenecked-versus-balanced topology contrast;
- the four pre-registered topology and propagation measurements;
- one small tagged fact-verification replication or a clearly reported failure to replicate.

### Stretch goals

- higher-order PID;
- formal performance bounds;
- a second near-benign attack;
- a limited density sensitivity analysis;
- additional model families or a learned adaptive topology.

## 15. Timeline to an ICML 2027 Submission

| Period | Milestones and deliverables |
|---|---|
| July 2026 | Finalize the hidden-role task, causal diagram, evidence schema, and minimum publishable unit |
| August 2026 | Implement the simulator, single-agent serialization, anonymous/provenance conditions, and early-window PID/TDMI checks |
| September 2026 | Implement the two matched topology protocols and the layered graph/log data pipeline; run estimator and budget validation |
| October 2026 | Run the main randomized topology and information-condition experiments; pre-register the primary analysis before replication |
| November 2026 | Run the single near-benign stress test and tagged verification replication; complete intervention checks |
| December 1–15, 2026 | Complete statistical analysis, robustness checks, and restricted theory results if supported |
| December 16–31, 2026 | Write the manuscript, figures, appendix, and reproducibility package |
| Early January 2027 | Obtain coauthor feedback; rerun critical checks; tighten claims and limitations |
| Mid-January 2027 | Finalize manuscript, code, data statements, and supplementary material; submit to ICML 2027 according to the official deadline |

## 16. Decision Criteria for Continuing the Direction

The direction should be prioritized if pilot experiments establish all three core results:

1. a reproducible regime in which collective information exceeds individual information but realized MAS performance is worse;
2. information synergy does not fully explain task utility under matched compute;
3. the bottlenecked-versus-balanced topology contrast changes exposure, propagation, or utility under matched resources.

The external replication is a confidence-building check rather than a requirement to expand the project. If graph measurements add no value after strong controls, that negative result remains informative: it would delimit when information-based coordination is sufficient and prevent unnecessary structural complexity.

## 17. Anticipated Paper Structure

1. Introduction and motivating failure case.
2. Related work on emergent coordination, information decomposition, network science, and compute-controlled agent evaluation.
3. Definitions of coordination, useful coordination, and MAS advantage.
4. Benchmark and equal-compute protocol.
5. Layered information, topology, and claim-lineage measurements.
6. Main randomized information-condition and topology experiments.
7. Near-benign stress test, replication, and limitations.
8. Conditional theory and conclusion.

## 18. Summary

This proposal does not assume that more agents are inherently better. It treats multi-agent collaboration as a resource-allocation and information-routing problem. Information-theoretic synergy identifies joint structure, while a layered topology analysis distinguishes communication opportunity from observed claim propagation and causal influence. Their relationship to task performance must be tested under equal computation budgets and with a deliberately small experimental design.

The most defensible central claim is therefore:

> Information synergy can reveal that agents are jointly interdependent, but a small, intervention-aware topology analysis is needed to determine whether that interdependence constitutes useful collaboration or creates a propagation vulnerability.

Establishing this distinction would provide a tighter scientific test of collective language-model behavior without treating communication graphs, embeddings, or learned graph representations as causal explanations by default.
