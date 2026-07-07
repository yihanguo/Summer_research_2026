# MAS Attack-Defense Methods: Latest Research Notes

Date checked: 2026-07-07

## Scope Note

The user asked for latest ICML / ICLR / NeurIPS papers later than the attached paper, `When Embedding-Based Defenses Fail` (`arXiv:2605.01133`, v2 dated 2026-06-20).

Strictly speaking, I did not find a verified ICML / ICLR / NeurIPS paper after 2026-06-20 on MAS attack-defense methods. NeurIPS 2026 papers are not public/settled yet, and the newest MAS-defense methods I found are mostly 2026 arXiv preprints.

To make the folder useful, I saved:

- the attached anchor paper;
- the graph-embedding baselines it discusses directly;
- the strongest verified top-conference match I found, GUARDIAN at NeurIPS 2025;
- newer 2026 MAS-defense preprints that extend or challenge the embedding-defense line.

## Downloaded PDFs

Saved under:

`/Users/wujinhua/Desktop/Group Meeting Jun 12/mas_attack_defense_latest`

| File | Paper | Status |
|---|---|---|
| `2605.01133_embedding_defenses_fail_confidence.pdf` | When Embedding-Based Defenses Fail | arXiv 2026 anchor paper |
| `2505.19234_GUARDIAN_temporal_graph_modeling.pdf` | GUARDIAN: Safeguarding LLM Multi-Agent Collaborations with Temporal Graph Modeling | NeurIPS 2025 according to paper text/reference |
| `2502.11127_G_Safeguard_topology_guided.pdf` | G-Safeguard | ACL 2025 baseline, not in requested venue set |
| `2508.08127_BlindGuard_unknown_attacks.pdf` | BlindGuard | arXiv 2025 |
| `2601.14667_INFA_Guard_infection_aware_safeguarding.pdf` | INFA-GUARD | arXiv 2026 |
| `2603.04474_From_Spark_to_Fire_error_cascades.pdf` | From Spark to Fire | arXiv 2026 |
| `2605.28104_STAR_sentence_level_rectification.pdf` | STAR: Sentence-Level Trustworthiness Analysis and Rectification | arXiv 2026 |
| `2606.12474_SAIGuard_communication_state_simulation.pdf` | SAIGuard | arXiv 2026 |

## High-Level Map

The recent methods can be grouped into seven defense philosophies:

1. Graph/embedding anomaly detection: detect suspicious agents/messages from communication embeddings and topology.
2. Temporal graph defense: model how anomalies evolve across rounds.
3. Unsupervised unknown-attack detection: learn normal MAS behavior without labeled malicious agents.
4. Infection-aware remediation: distinguish original attackers from benign agents that became contaminated.
5. Sentence/claim-level rectification: verify and repair misleading content instead of only removing agents.
6. Proactive simulation: simulate the impact of a message before allowing it into the real MAS.
7. Confidence/internal-signal defense: use token-level uncertainty when embeddings are not separable.

## Paper Summaries

### 1. When Embedding-Based Defenses Fail

Core idea:

Existing graph/embedding defenses assume malicious messages are separable from benign messages in embedding space. This paper argues that assumption is brittle. It proposes near-benign attacks that keep malicious messages close to benign embeddings, then adds token-level confidence as a complementary defense signal.

Attack model:

- Slow Drift: gradually steer the group toward a wrong answer.
- Benign Wrapper: wrap a short malicious payload in normal-looking reasoning.
- Chaos Seeding: increase benign disagreement so the attacker no longer looks like an outlier.

Defense:

- Compute token-level uncertainty from generation logits.
- Convert uncertainty to a confidence score.
- Either prune low-confidence messages or down-weight them in later aggregation.

Application scenarios:

- LLM debate and QA-style MAS on MMLU, GSM8K, and BBH.
- Communication topologies including star, chain, sparse, and fully connected graphs.

Key limitation:

The method improves robustness empirically but does not prove universal success. The paper also shows that both embedding and confidence signals decay after misinformation circulates.

### 2. GUARDIAN

Core idea:

GUARDIAN models multi-agent collaboration as a discrete-time temporal attributed graph. Agents are nodes, inter-agent communications are edges, and agent responses are node attributes. It uses an unsupervised encoder-decoder model to reconstruct normal graph attributes/structures; large reconstruction errors indicate anomalous nodes or edges.

Method:

- Build temporal graphs over conversation rounds.
- Encode attributes and structure using graph neural components.
- Use separate decoders for node attributes and graph structure.
- Use incremental training over previous timesteps.
- Remove anomalous nodes/edges to reduce propagation.

Attack/safety scenarios:

- Hallucination amplification.
- Error injection.
- Agent-targeted attacks.
- Communication-targeted attacks.

Application scenarios:

- Multi-agent collaboration and debate settings where one agent or one communication edge can corrupt the group trajectory.

Why it matters:

Compared with one-shot embedding detection, GUARDIAN explicitly tracks how safety problems propagate over time.

Limitations:

- Still operates largely through graph/representation anomaly signals.
- Can falsely remove correct agents.
- Works best when anomalous behavior is detectably different from normal temporal patterns.

### 3. G-Safeguard

Core idea:

G-Safeguard constructs a multi-agent utterance graph and applies a GNN to detect risky agents. Once risky nodes are found, it uses topology-based intervention, such as pruning edges, to prevent malicious information from spreading.

Method:

- Represent MAS as a graph.
- Encode each agent's current/historical utterances.
- Encode communication edges.
- Run edge-featured GNN for attack detection.
- Perform edge sparsification/pruning for remediation.

Attack scenarios:

- Prompt injection.
- Tool attack.
- Memory poisoning.

Application scenarios:

- Multi-agent QA, tool-use, and memory-augmented agent systems.
- Different topologies: chain, tree, star, random/fully connected.

Why it matters:

It is a central graph-embedding baseline for MAS safety. The attached paper directly compares against it.

Limitations:

- It is not one of the requested ICML/ICLR/NeurIPS venues; it is cited as ACL 2025 in the attached paper.
- It relies on anomaly separability. Near-benign attacks can bypass it.

### 4. BlindGuard

Core idea:

BlindGuard targets unknown attacks where labeled malicious-agent examples are unavailable. It learns from normal MAS behavior and uses synthetic corruption plus contrastive learning to detect abnormal agents at inference time.

Method:

- Use a hierarchical agent encoder:
  - individual semantic features;
  - local neighborhood structure;
  - global MAS context.
- Simulate corruption on normal traces.
- Train a corruption-guided contrastive detector.
- Compute anomaly scores and prune suspicious agents.

Attack scenarios:

- Prompt injection.
- Tool attack.
- Memory attack.
- Unknown or unseen attack types.

Application scenarios:

- Real deployments where defenders cannot pre-label every attack pattern.
- MAS with changing topologies or unseen attack types.

Limitations:

- Still depends on the synthetic corruption model being representative enough.
- Better as a boundary layer than a complete defense.

### 5. INFA-GUARD

Core idea:

Most defenses treat agents as either benign or malicious. INFA-GUARD adds a third category: infected agents. These are originally benign agents that have been persuaded or contaminated by attacker messages.

Method:

- Model infection dynamics over conversation rounds.
- Classify agents as benign, infected, or attack sources.
- Use topology constraints: infected agents should be near attackers or other infected agents in the communication graph.
- Remediate differently:
  - replace attack agents;
  - rehabilitate infected agents by correcting their internal context/responses.

Attack scenarios:

- Prompt injection.
- Memory attack.
- Tool exploitation.

Application scenarios:

- MAS where malicious content propagates virally.
- Long multi-round debates where benign agents may become secondary propagators.

Metrics:

- ASR@k: attack success after k rounds.
- MDSR@k: MAS defense success rate after k rounds.

Why it matters:

It moves beyond source detection and treats propagation state as part of the defense problem.

Limitations:

- Needs runtime observation of infection dynamics.
- More complex than binary malicious-agent pruning.
- Still a 2026 arXiv preprint, not a verified ICML/ICLR/NeurIPS paper.

### 6. From Spark to Fire

Core idea:

This paper studies how a small initial error can become a full-system false consensus in LLM-MAS. It is broader than adversarial attacks: the "spark" can be an endogenous hallucination or an externally injected atomic error.

Method:

- Model MAS collaboration as a directed dependency graph.
- Track atomic claims through the workflow.
- Define propagation dynamics and early amplification risk.
- Add a genealogy-graph governance layer as middleware.
- Verify, tag, rollback, or suppress unsupported claims before they become consensus.

Attack/safety scenarios:

- Error cascades.
- False consensus.
- Single atomic error seed leading to widespread failure.
- Application-layer attacks that package false claims as credible dependencies.

Application scenarios:

- Multi-agent software, analysis, research, and task-planning workflows.
- Framework-level auditing of AutoGen, MetaGPT, CAMEL-style workflows.

Why it matters:

It reframes MAS attacks as propagation and lineage problems rather than only attacker identification.

Limitations:

- The propagation model is an early-risk heuristic, not a calibrated deployment guarantee.
- The governance layer may add verification/token overhead.

### 7. STAR: Sentence-Level Trustworthiness Analysis and Rectification

Core idea:

STAR argues that malicious agents can coordinate, not merely attack independently. It introduces cooperative attacks where malicious agents share ally context and adapt their strategy. STAR defends at sentence level, not agent level.

Attack method:

- Multiple malicious agents observe ally messages.
- If allies' arguments are strong, they reinforce the false consensus.
- If allies' arguments are weak, they introduce new deceptive angles.

Defense method:

- Decompose each response into sentences.
- Use an LLM verifier to judge factual correctness and confidence.
- Extract/correct wrong claims.
- Accumulate suspicion scores for agents.
- Rectify suspicious content.
- Exclude suspicious agents from final voting.

Application scenarios:

- QA-style MAS with debate/majority voting.
- Cooperative or collusive misinformation attacks.

Metrics:

- Task Success Rate (TSR): higher is better.
- Attack Success Rate (ASR): lower is better.

Reported direction:

STAR improves TSR and reduces ASR relative to no defense and coarse-grained baselines.

Limitations:

- Relies on LLM verifier quality.
- Can be token-expensive.
- Does not guarantee perfect detection.
- arXiv 2026 preprint; not verified as ICML/ICLR/NeurIPS.

### 8. SAIGuard

Core idea:

SAIGuard shifts from reactive detection to proactive message interception. Instead of waiting for harmful outputs and then isolating agents, it simulates what an incoming message would do to local agent state and global MAS state before letting the message propagate.

Method:

- Represent MAS as an interaction graph.
- For each incoming message, inject it into a simulated MAS state.
- Use a GNN-based simulation/reconstruction model trained on benign traces.
- Measure agent-level and system-level reconstruction deviations.
- Use robust thresholding, such as MAD-based thresholds, to flag risky messages.
- Sanitize or regenerate risky messages instead of isolating whole agents.

Attack scenarios:

- Agent-level attacks.
- Communication-level attacks.
- Prompt injection.
- Tool attack.
- Memory poisoning.
- Communication hijacking.

Application scenarios:

- Runtime MAS communication security where message-level intervention is preferable to removing agents.
- Long-horizon MAS where irreversible damage can occur if defenses only act after execution.

Metrics:

- ACC: task utility.
- ASR: attack success rate.
- F1: hazardous-message detection.

Why it matters:

It directly addresses the weakness of reactive graph defenses: by the time an agent is flagged, malicious content may already have propagated.

Limitations:

- Currently focused on text communication.
- Requires a learned simulation/reconstruction model.
- arXiv 2026 preprint; not verified as ICML/ICLR/NeurIPS.

## Comparison Table

| Method | Main Unit of Defense | Attack Assumption | Intervention | Best Application Scenario | Main Weakness |
|---|---|---|---|---|---|
| G-Safeguard | Agent/message graph | Attackers are graph/embedding anomalies | Prune risky agents/edges | Prompt/tool/memory attacks with visible abnormality | Near-benign attacks evade embedding separation |
| GUARDIAN | Temporal graph | Anomalies evolve over rounds | Remove anomalous nodes/edges | Hallucination/error propagation | Can falsely prune correct agents |
| BlindGuard | Hierarchical agent representation | Unknown attacks deviate from learned normality | Prune top anomalous agents | No labeled attack data | Synthetic corruption may not match real attacks |
| INFA-GUARD | Attack + infected states | Benign agents can become infected | Replace attackers, rehabilitate infected agents | Viral malicious propagation | More complex state modeling |
| From Spark to Fire | Atomic claim lineage | Small errors can cascade | Verify/tag/rollback claims | False-consensus prevention | Adds governance overhead |
| STAR | Sentence-level claims | Malicious agents coordinate adaptively | Verify and rectify sentences; robust voting | Cooperative/collusive misinformation | Depends on LLM verifier |
| SAIGuard | Incoming message simulation | Harm can be predicted before propagation | Sanitize/regenerate risky messages | Proactive runtime defense | Needs simulation model |
| Confidence-guided defense | Token-level uncertainty | Embeddings may be non-separable | Prune/down-weight low-confidence messages | Near-benign attacks | Signals decay over rounds |

## Key Takeaways

1. The field is moving from agent-level pruning to message-level or sentence-level intervention.
2. Pure embedding separation is increasingly treated as insufficient.
3. Topology matters: dense graphs spread attacks faster, while bottlenecked graphs preserve detection windows longer.
4. The strongest new direction is hybrid defense:
   - graph/temporal structure for propagation;
   - content verification for local misinformation;
   - confidence/internal signals for non-separable attacks;
   - proactive simulation before message propagation.
5. A robust MAS defense should probably not ask only "who is malicious?" It should also ask:
   - which message is harmful?
   - which claim is unsupported?
   - which benign agents have become infected?
   - what will happen if this message propagates one or two rounds?

## Suggested Reading Order

1. `2605.01133_embedding_defenses_fail_confidence.pdf`
2. `2505.19234_GUARDIAN_temporal_graph_modeling.pdf`
3. `2502.11127_G_Safeguard_topology_guided.pdf`
4. `2508.08127_BlindGuard_unknown_attacks.pdf`
5. `2601.14667_INFA_Guard_infection_aware_safeguarding.pdf`
6. `2605.28104_STAR_sentence_level_rectification.pdf`
7. `2606.12474_SAIGuard_communication_state_simulation.pdf`
8. `2603.04474_From_Spark_to_Fire_error_cascades.pdf`

## Source URLs

- When Embedding-Based Defenses Fail: https://arxiv.org/abs/2605.01133
- GUARDIAN: https://arxiv.org/abs/2505.19234
- G-Safeguard: https://arxiv.org/abs/2502.11127
- BlindGuard: https://arxiv.org/abs/2508.08127
- INFA-GUARD: https://arxiv.org/abs/2601.14667
- From Spark to Fire: https://arxiv.org/abs/2603.04474
- STAR: https://arxiv.org/abs/2605.28104
- SAIGuard: https://arxiv.org/abs/2606.12474
