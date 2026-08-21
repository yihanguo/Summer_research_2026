# Ten task families for testing outcome-aligned multi-agent coordination

## Executive recommendation

The strongest next-step portfolio is not ten versions of a social-deduction
game. It is a deliberately heterogeneous set of tasks that preserves the
scientific structure needed by the current temporal information-theoretic
analysis:

1. agents have stable identities and interdependent decisions;
2. each agent exposes a discrete state before every consequential step;
3. a group macrostate is a deterministic function of those states and public
   environment state;
4. the next agent panel and next macrostate are observable;
5. a task-native utility measures whether the coordination helped;
6. hidden truth and terminal outcome are excluded from the predictive states.

This separation is essential. PID synergy and the macro criterion measure
statistical coordination, not whether that coordination is beneficial. Each
experiment should therefore report both coordination and utility. The most
useful interpretation is the following two-axis design:

| Coordination | Task utility | Interpretation |
|---|---|---|
| High | High | outcome-aligned collaboration |
| High | Low | coordinated but harmful or misdirected behavior |
| Low | High | successful mostly through independent competence |
| Low | Low | failed coordination and failed task performance |

The ten candidates below cover coding, formal mathematics, database work,
cybersecurity, constrained communication, physical teamwork, social dilemmas,
mixed-motive negotiation, household assistance, and adversarial evidence
adjudication. “Native” means that the cited source already contains multiple
interacting decision makers. “Adapted” means that the source is a strong
single-agent benchmark and the multi-agent organization described here is a
new experimental wrapper, not a claim about the source paper.

## Common measurement protocol

For each task, collect complete per-step panels and calculate the existing
estimators without changing their mathematical definitions:

```text
Pair target: (X_i,t+1, X_j,t+1)

Syn_ij = I({X_i,t, X_j,t}; target)
         - I(X_i,t; target)
         - I(X_j,t; target)
         + I_min

S_macro(1) = I(V_t; V_t+1) - sum_k I(X_k,t; V_t+1)
```

The current implementation is documented in
[`TEMPORAL_COORDINATION_IMPLEMENTATION.md`](../code/TEMPORAL_COORDINATION_IMPLEMENTATION.md)
and implemented in
[`temporal_coordination.py`](../code/experiment/temporal_coordination.py).
Use the task-native utility listed below as a separate outcome variable and
retain the current future-panel permutation null.

## Candidate 1: collaborative repository repair on SWE-bench

**Field:** software engineering and coding
**Status:** adapted multi-agent wrapper around a source-native single-agent
benchmark

### Proposed task

Give a team the same issue and repository snapshot, but partition access or
responsibility among a locator, patch author, test designer, and reviewer.
Agents exchange file hypotheses, test evidence, proposed edits, and confidence.
Only patches that pass the official containerized test harness count as task
success. To make information genuinely complementary, give the locator broad
search access, the test agent execution logs, and the reviewer the issue plus
diff, while allowing requested evidence to be shared through the protocol.

### State and outcome

- Example `X_i,t`: role, current file/function hypothesis, evidence IDs,
  proposed edit/test, confidence bin, blocker, intended next action.
- Example `V_t`: union of implicated files, accepted evidence, current joint
  patch version, unresolved-test set, modal root-cause hypothesis, agreement
  bin.
- Positive utility: official resolved/not-resolved result, fraction of
  fail-to-pass and pass-to-pass tests, time/tool calls, and patch size.

### Why it fits

SWE-bench uses real repository issues, requires coordinated changes across
functions/classes/files, and provides executable evaluation. That makes the
future state and positive outcome much less subjective than in Werewolf. The
wrapper also tests whether information synergy predicts an actually correct
patch rather than persuasive agreement.

### Sources

- [SWE-bench, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html)
- [Official SWE-bench repository and evaluation harness](https://github.com/SWE-bench/SWE-bench)

## Candidate 2: collaborative formal proof construction with LeanDojo

**Field:** mathematics and formal reasoning
**Status:** adapted multi-agent wrapper around a source-native single-prover
benchmark

### Proposed task

Assign agents complementary proof responsibilities: premise retrieval, tactic
proposal, counterexample/failure diagnosis, and proof-state review. At each Lean
interaction, every agent records its current proof-state interpretation and
next tactic. A coordinator may select a tactic only after the panel is saved.
Lean, rather than another language model, verifies correctness.

### State and outcome

- Example `X_i,t`: proof-state hash, selected premises, tactic family, expected
  subgoal count, confidence bin, failure class, intended next tactic.
- Example `V_t`: current Lean proof state, union of endorsed premises, accepted
  tactic prefix, unresolved subgoals, modal tactic family, agreement bin.
- Positive utility: theorem proved, number of valid tactic steps, proof length,
  Lean errors, and wall-clock/tool budget.

### Why it fits

LeanDojo exposes proof states, tactics, and premises and supports programmatic
interaction with Lean. It therefore offers repeated, machine-verified state
transitions and a hard correctness outcome. Complementary premise and tactic
knowledge creates a clean test of whether joint information predicts proof
progress beyond the agents individually.

### Sources

- [LeanDojo, NeurIPS 2023 Datasets and Benchmarks](https://proceedings.neurips.cc/paper_files/paper/2023/hash/4441469427094f8873d0fecb0c4e1cee-Abstract-Datasets_and_Benchmarks.html)
- [Official LeanDojo repository](https://github.com/lean-dojo/LeanDojo)

## Candidate 3: collaborative database operations on BIRD-INTERACT

**Field:** databases, text-to-SQL, and operational data work
**Status:** adapted multi-agent wrapper around a source-native interactive
single-agent benchmark

### Proposed task

Create a database team consisting of a user-intent analyst, schema/knowledge
retriever, SQL author, and execution auditor. Agents receive different subsets
of the request, metadata, knowledge base, and execution feedback. They may ask
for clarification and revise a shared operation plan. Use isolated database
copies and the official executable tests, especially for write operations.

### State and outcome

- Example `X_i,t`: intent hypothesis, referenced tables/columns, evidence IDs,
  planned CRUD action, expected row-effect bin, confidence, next query/action.
- Example `V_t`: shared intent, union of selected schema items, current SQL
  candidate hash, execution-status class, unresolved ambiguities, agreement.
- Positive utility: official task success/test pass, database integrity,
  clarification count, execution errors, and interaction cost.

### Why it fits

BIRD-INTERACT is explicitly dynamic: agents can solicit clarifications,
retrieve knowledge, explore a database, and recover from execution errors. It
covers the full CRUD spectrum and guards tasks with executable tests. The
multi-agent wrapper turns its distinct information channels into controlled
complementarity while retaining the benchmark's exact outcome oracle.

### Sources

- [BIRD-INTERACT, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/496b549556509bbb9770bf9d335c5800-Abstract-Conference.html)
- [Official BIRD-INTERACT repository](https://github.com/bird-bench/BIRD-Interact)

## Candidate 4: sandboxed collaborative cybersecurity investigation on Cybench

**Field:** cybersecurity and competitive attacker/defender reasoning
**Status:** adapted multi-agent wrapper around a source-native single-agent
framework

### Proposed task

Run only inside Cybench's isolated task environment. Form a team with artifact
analyst, hypothesis generator, command planner, and verifier, or compare an
attacker coalition with a defender coalition in separately authorized
environments. Partition observations such as logs, binaries, network traces,
and subtask results. Require a structured proposal and risk classification
before any environment action.

### State and outcome

- Example `X_i,t`: current finding class, evidence IDs, vulnerability
  hypothesis, proposed safe command, expected observation, risk bin,
  confidence.
- Example `V_t`: shared finding graph, current attack/defense phase, verified
  artifacts, unresolved hypotheses, authorized action queue, agreement.
- Positive utility: official task/subtask completion, verified findings,
  minimal unsafe/irrelevant commands, time, and token/tool cost.

### Why it fits

Cybench provides standardized, reproducible cybersecurity tasks and explicit
subtasks that expose intermediate progress. Those intermediate states are
valuable for temporal coordination analysis. The sandbox restriction is
non-negotiable: the research question is collaboration under asymmetric
evidence, not real-world system access.

### Sources

- [Cybench, ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/3e9412a9c1d93810ef3ef7825115016b-Abstract-Conference.html)
- [Official Cybench repository](https://github.com/andyzorigin/cybench)

## Candidate 5: Hanabi under constrained communication

**Field:** cooperative games, theory of mind, and information asymmetry
**Status:** source-native multi-agent task; structured-state instrumentation is
new

### Proposed task

Run two-to-five-player Hanabi. Players see others' cards but not their own, use
limited hint tokens, and share one score. Before each legal action, record a
complete private belief/action panel. Compare ordinary legal signaling with
prompt interventions that encourage calibrated belief reporting, but never
reveal hidden cards to the acting player.

### State and outcome

- Example `X_i,t`: public-card knowledge, belief bins over own cards, inferred
  partner intention, intended legal action, hint-token preference, confidence.
- Example `V_t`: public tableau, discard/public hint history, information and
  fuse tokens, aggregate playability beliefs, modal intended action class.
- Positive utility: final Hanabi score, completed suits, fuse losses, hint
  efficiency, and illegal-action rate.

### Why it fits

This is the closest non-Werewolf candidate. Hanabi is purely cooperative,
imperfect-information, and explicitly designed to foreground beliefs and
intentions of other agents. Unlike Werewolf, its common payoff removes
coalition ambiguity, and its hidden-card rules create a strong leakage test.

### Sources

- [The Hanabi Challenge](https://arxiv.org/abs/1902.00506)
- [Official Hanabi Learning Environment](https://github.com/google-deepmind/hanabi-learning-environment)

## Candidate 6: Overcooked cooperative production

**Field:** embodied planning, workflow coordination, and human-AI teamwork
**Status:** source-native multi-agent task; explicit belief panels/messages are
an instrumentation extension

### Proposed task

Two agents jointly prepare and serve dishes in layouts that create movement and
strategy bottlenecks. Before each macro-action, collect role assignment,
resource belief, intended subtask, route, and collision-risk state. Compare
self-organized play with interventions that elicit task allocation and
uncertainty.

### State and outcome

- Example `X_i,t`: held object, local position/zone, assigned subtask, intended
  destination/action, partner-intent belief, blocker, confidence.
- Example `V_t`: object/order inventory, completed recipe stages, joint task
  allocation, bottleneck zone, route-conflict bin, plan agreement.
- Positive utility: shared reward/dishes served, completion time, idle time,
  collisions, duplicated work, and handoff efficiency.

### Why it fits

Overcooked was introduced specifically as a challenging coordination
environment. Shared reward and precise simulator state make positive outcome
observable, while alternative task divisions let PID distinguish genuinely
joint planning from two independently competent policies.

### Sources

- [On the Utility of Learning about Humans for Human-AI Coordination, NeurIPS 2019](https://proceedings.neurips.cc/paper_files/paper/2019/hash/f5b1b89d98b7286673128a5fb112cb9a-Abstract.html)
- [Official Overcooked-AI repository](https://github.com/HumanCompatibleAI/overcooked_ai)

## Candidate 7: coalition negotiation in Diplomacy

**Field:** negotiation, competition between parties, and mixed motives
**Status:** source-native multi-agent task

### Proposed task

Use a controlled Diplomacy environment with stable player identities, private
bilateral messages, simultaneous orders, and changing alliances. Analyze both
temporary coalitions and all players. The main positive outcome should be a
predeclared coalition-level objective, not merely agreement or message volume.

### State and outcome

- Example `X_i,t`: board-belief summary, proposed commitments, believed ally
  reliability bins, intended orders, threat target, confidence.
- Example `V_t`: public board state, coalition membership/commitment graph,
  compatible joint-order plan, contested regions, agreement and trust bins.
- Positive utility: supply-center change, order compatibility/support success,
  promise fulfillment, survival, and final score.

### Why it fits

Diplomacy combines cooperation and competition among seven players and relies
on natural-language negotiation plus tactical coordination. It generalizes the
Werewolf question from fixed hidden teams to endogenous coalitions. It also
demonstrates why high synergy cannot itself be called beneficial: a tightly
coordinated coalition can harm the rest of the system.

### Sources

- [CICERO project and primary publication links](https://ai.meta.com/research/cicero/)
- [Official CICERO Diplomacy repository](https://github.com/facebookresearch/diplomacy_cicero)
- [Science paper record and abstract](https://pubmed.ncbi.nlm.nih.gov/36413172/)

## Candidate 8: resource-sharing social dilemmas in Melting Pot

**Field:** economics-inspired social dilemmas, commons management, and
generalization
**Status:** source-native multi-agent task; structured language reports are an
instrumentation extension

### Proposed task

Select Melting Pot substrates involving resource sharing, reciprocity, task
partitioning, or commons cleanup. Give agents local observations and record a
structured resource/commitment state before each macro-step. Evaluate on novel
co-player populations and scenarios, as intended by the benchmark.

### State and outcome

- Example `X_i,t`: local resource bin, observed demand, cooperation/defection
  intent, contribution target, partner-trust bins, risk and confidence.
- Example `V_t`: total resource/cleanup state, allocation distribution,
  commitments, unmet demand, inequality bin, system-risk bin.
- Positive utility: total return, sustainability, cleanup/resource level,
  inequality, worst-agent return, and generalization to held-out co-players.

### Why it fits

Melting Pot was created to evaluate generalization in multi-agent systems and
includes social dilemmas, reciprocity, resource sharing, and task partitioning.
It directly tests the user's desired generalized description of collaboration:
coordination should align not only with individual reward but with a declared
system-level outcome.

### Sources

- [Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot, ICML 2021](https://proceedings.mlr.press/v139/leibo21a.html)
- [Official Melting Pot repository](https://github.com/google-deepmind/meltingpot)

## Candidate 9: Communicative Watch-And-Help household assistance

**Field:** embodied household assistance and complementary roles
**Status:** source-native collaborative task; use the communicative extension
for language-agent experiments

### Proposed task

One agent observes a demonstration or holds goal information; another must help
complete the household task in a new environment. In the communicative version,
agents exchange goal hypotheses, object observations, subtask claims, and
requests. Log a panel before each high-level household action.

### State and outcome

- Example `X_i,t`: inferred goal predicates, observed objects/locations,
  assigned subtask, intended action, help request, blocker, confidence.
- Example `V_t`: union of achieved predicates, shared goal hypothesis,
  object-location map, subtask allocation, critical path, agreement.
- Positive utility: task success, predicate completion, steps/time, duplicated
  effort, unnecessary actions, and communication cost.

### Why it fits

Watch-And-Help requires an assistant to infer a goal from one demonstration and
coordinate with a human-like agent in an unseen environment. Its explicit
social-perception and collaboration stages provide complementary knowledge and
a clear shared outcome. The ICLR 2024 CoELA code adds Communicative
Watch-And-Help for language-based embodied agents.

### Sources

- [Watch-And-Help, ICLR 2021](https://iclr.cc/virtual/2021/spotlight/3491)
- [Official Watch-And-Help repository](https://github.com/xavierpuigf/watch_and_help)
- [CoELA / Communicative Watch-And-Help, ICLR 2024 official code](https://github.com/UMass-Embodied-AGI/CoELA)

## Candidate 10: evidence-grounded debate and adjudication

**Field:** competitive argument, scalable oversight, and group decision making
**Status:** source-native multi-agent debate protocol, with a proposed
machine-verifiable task/outcome layer

### Proposed task

Two advocates receive complementary or conflicting evidence and argue for
candidate answers while a judge decides. Add a fact-checker or evidence clerk
as a collaborative role, and use questions with a known answer and attributable
evidence. Keep debate roles and evidence access symmetric across repeated
trials. The system objective is correct adjudication, not advocate victory.

### State and outcome

- Example `X_i,t`: answer belief, evidence IDs, claim-evidence links, planned
  argument/challenge, opponent-claim assessment, confidence.
- Example `V_t`: public claim/evidence graph, surviving hypotheses,
  corroboration/contradiction counts, judge belief bin, consensus/polarization.
- Positive utility: judge correctness, evidence precision/recall, citation
  validity, calibration, unsupported-claim rate, and deliberation cost.

### Why it fits

The ICML 2024 debate study uses two LLM experts arguing for different answers
and a non-expert selecting an answer; its released code includes debate,
interactive-debate, judge, and accuracy pipelines. The proposed extension adds
explicit claim/evidence state panels so the positive system outcome remains
auditable. It is a valuable counterpoint to pure cooperation: useful
system-level information can emerge from structured competition even when the
agents' local objectives conflict.

### Sources

- [Debating with More Persuasive LLMs Leads to More Truthful Answers, ICML 2024](https://proceedings.mlr.press/v235/khan24a.html)
- [Official `ucl-dark/llm_debate` code release](https://github.com/ucl-dark/llm_debate)
- [AI safety via debate, original proposal](https://arxiv.org/abs/1805.00899)

## Recommended implementation order

| Priority | Candidate | Reason |
|---:|---|---|
| 1 | Hanabi | Closest clean generalization from Werewolf; native private information and common payoff |
| 2 | BIRD-INTERACT | Database diversity, dynamic interaction, and executable CRUD tests |
| 3 | SWE-bench | Strong real-world coding outcome oracle and rich complementary subroles |
| 4 | Communicative Watch-And-Help | Embodied complementary information and interpretable joint progress |
| 5 | LeanDojo | Formal correctness and fine-grained temporal proof states |
| 6 | Overcooked | Fast shared-reward coordination control with simulator truth |
| 7 | Melting Pot | Best broad generalization and social-welfare stress test |
| 8 | Diplomacy | Important mixed-motive test, but coalition/outcome choices need careful preregistration |
| 9 | Evidence-grounded debate | Strong adversarial-control condition; requires a curated ground-truth corpus |
| 10 | Cybench | Useful and machine-checkable, but highest safety and sandboxing burden |

The first five form a well-rounded initial benchmark: game, database, coding,
embodied assistance, and mathematics. They should share the same panel timing,
categorical-state discipline, permutation null, model families, seeds, and
outcome-versus-coordination reporting.
