# Four alternative state designs for temporal synergy analysis

## Design constraints inherited from the current Werewolf implementation

The current implementation measures a complete panel before every public turn:

```text
X_i,t = (
  bid,
  top_suspect,
  suspect_confidence_bin,
  intended_vote,
  evidence_state,
  complete_suspect_levels
)

V_t = (
  living_player_identities,
  per_candidate_median_suspicion_level,
  group_top_suspect,
  majority_consensus_bin
)
```

`V_t` is deterministically calculated from the panel and public state. Hidden
roles are absent. Pairwise PID predicts `(X_i,t+1, X_j,t+1)`, and the macro
criterion predicts `V_t+1`. These rules are encoded in
[`temporal_coordination.py`](../code/experiment/temporal_coordination.py) and
explained in
[`TEMPORAL_COORDINATION_IMPLEMENTATION.md`](../code/TEMPORAL_COORDINATION_IMPLEMENTATION.md).

Any generalization should preserve six properties:

1. **Temporal precedence:** record `X_i,t` before the action whose consequences
   appear at `t+1`.
2. **Complete panels:** the same eligible agents must report at each time index.
3. **Deterministic macrostate:** `V_t = f({X_i,t}, public_state_t)` with a fixed
   documented `f`.
4. **No target leakage:** do not encode hidden truth, future test results,
   terminal winner, or an evaluator's eventual correctness in `X_t` or `V_t`.
5. **Controlled cardinality:** use named categories, hashes, ranks, bins, and
   fixed-size summaries instead of unbounded natural language.
6. **Outcome separation:** collaboration quality is a separate utility variable;
   positive synergy alone is not evidence of a positive outcome.

The following are four reusable descriptions, not four competing estimators.
The PID and macro equations stay unchanged.

## State design A: belief, uncertainty, and intended action

### Individual state

```text
X_i,t^belief = (
  agent_identity,
  candidate_set_version,
  ranked_belief_bins,
  belief_entropy_bin,
  top_hypothesis,
  intended_action,
  action_confidence_bin,
  evidence_state
)
```

- `ranked_belief_bins` is a complete vector over the current legal candidates,
  with each value discretized, for example, to `0,...,4`.
- `belief_entropy_bin` captures diffuse versus concentrated belief without
  retaining arbitrary floating-point precision.
- `evidence_state` should enumerate provenance categories or evidence IDs, not
  copy unrestricted text.

### Whole-system state

```text
V_t^belief = (
  eligible_agent_identities,
  candidate_set_version,
  per_candidate_median_belief_bin,
  group_top_hypothesis,
  majority_consensus_bin,
  group_uncertainty_bin,
  modal_intended_action
)
```

This is a direct generalization of the current Werewolf state. Every component
is a deterministic function of the panel plus the public candidate set.

### Best uses

Hanabi, evidence debate, database intent resolution, cybersecurity diagnosis,
and any task with competing hypotheses.

### Outcome and caveat

Measure hypothesis correctness, task success, calibration, and cost separately.
The main risk is large state cardinality. Keep candidates stable within a panel,
use bins, and record the candidate-set version so that state changes are not
mistaken for belief changes.

## State design B: evidence provenance, coverage, and uptake

### Individual state

```text
X_i,t^evidence = (
  agent_identity,
  available_evidence_ids,
  newly_acquired_evidence_ids,
  cited_evidence_ids,
  source_reliability_bins,
  contradiction_ids,
  requested_evidence_type,
  intended_action,
  confidence_bin
)
```

Evidence IDs must point to immutable artifacts such as a test log, schema item,
Lean premise, packet trace, or cited document. `Available` and `cited` are kept
separate so the analysis can distinguish information possession from uptake.

### Whole-system state

```text
V_t^evidence = (
  eligible_agent_identities,
  union_available_evidence,
  union_cited_evidence,
  coverage_bin,
  redundancy_histogram,
  unresolved_contradiction_count_bin,
  shared_evidence_frontier,
  modal_intended_action
)
```

`redundancy_histogram` counts how many artifacts are known by one, two, or more
agents. `shared_evidence_frontier` is the set/hash of evidence that has entered
the public joint record. All are deterministic panel summaries.

### Best uses

SWE-bench, LeanDojo, BIRD-INTERACT, Cybench, evidence debate, and Werewolf when
the key question is disclosure rather than only suspicion.

### Outcome and caveat

Measure official task correctness, evidence validity, coverage of decisive
evidence, unsupported claims, and cost separately. Never place a label such as
“decisive,” “true,” or “correct” in the predictive state unless that label was
already observable to the agent at time `t`; use it only in offline evaluation.

## State design C: joint plan, dependency, and progress frontier

### Individual state

```text
X_i,t^plan = (
  agent_identity,
  assigned_subgoal,
  local_status,
  produced_artifact_hash,
  blocker_category,
  dependency_claims,
  proposed_next_action,
  estimated_remaining_work_bin,
  confidence_bin
)
```

The vocabulary of subgoals, statuses, blockers, and actions must be fixed per
task. Artifact content stays outside the categorical state; its stable hash or
version identifies it.

### Whole-system state

```text
V_t^plan = (
  eligible_agent_identities,
  joint_plan_version,
  completed_subgoal_set,
  active_dependency_frontier,
  artifact_version_set,
  bottleneck_category,
  modal_next_action,
  plan_agreement_bin,
  remaining_budget_bin
)
```

The joint plan and dependency frontier are derived by a fixed reducer from the
agents' declared subgoals and dependency claims. If a coordinator edits the
plan, save that public plan as part of `public_state_t` before computing `V_t`.

### Best uses

SWE-bench repository repair, Lean proof construction, Overcooked production,
Watch-And-Help household tasks, and multi-stage database operations.

### Outcome and caveat

Measure verified subgoal completion, terminal success, elapsed actions, rework,
duplicate work, and cost. A plan can be coherent but wrong, so neither plan
agreement nor macro synergy may substitute for the task verifier.

## State design D: resources, commitments, risk, and welfare

### Individual state

```text
X_i,t^resource = (
  agent_identity,
  local_resource_bins,
  local_demand_bin,
  offer_or_commitment,
  intended_allocation_or_action,
  partner_trust_bins,
  predicted_local_utility_bin,
  perceived_system_risk_bin,
  confidence_bin
)
```

Commitments use a finite schema: counterparty, resource/action category,
quantity bin, and deadline/turn bin. Trust scores are complete vectors over
current counterparties, analogous to Werewolf's complete suspicion vector.

### Whole-system state

```text
V_t^resource = (
  eligible_agent_identities,
  aggregate_resource_bins,
  allocation_distribution_bins,
  active_commitment_graph_hash,
  unmet_demand_bin,
  inequality_or_polarization_bin,
  system_risk_bin,
  coalition_structure,
  predicted_joint_utility_bin
)
```

The commitment graph and coalition structure are deterministically built from
declared offers/commitments. `predicted_joint_utility_bin` is permitted because
it is a time-`t` forecast; realized future utility is not.

### Best uses

Diplomacy, Melting Pot resource dilemmas, team allocation in Cybench, and
Overcooked/household task partitioning.

### Outcome and caveat

Report realized total utility, worst-agent utility, inequality, sustainability,
promise fulfillment, and task success. For mixed-motive tasks, preregister whose
positive outcome is being evaluated: a coalition, all participants, or an
external social objective. Otherwise “outcome-aligned” becomes undefined.

## Cross-design recommendation

Do not concatenate all four designs into one giant state. Sparse categorical
plugin estimates deteriorate rapidly as cardinality grows. Instead:

1. choose one primary design based on the task's causal bottleneck;
2. preregister one secondary design for mechanism analysis;
3. calculate PID and `S_macro` separately for each design;
4. use the same panels, lag, coalition definition, and temporal null;
5. compare conclusions across state designs as a robustness analysis.

Recommended pairing:

| Task type | Primary | Secondary |
|---|---|---|
| Diagnosis or adjudication | Belief/action | Evidence/uptake |
| Coding, proof, database workflow | Plan/progress | Evidence/uptake |
| Embodied shared task | Plan/progress | Resource/commitment |
| Negotiation or social dilemma | Resource/commitment | Belief/action |

This preserves interpretability and tests whether apparent coordination is a
property of the interaction rather than an artifact of one state encoding.
