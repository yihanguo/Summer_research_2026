# Temporal coordination implementation

This experiment revision makes the Werewolf trajectory directly analyzable
with the information-theoretic definitions in *Emergent Coordination in
Multi-Agent Language Models*.

## Per-turn state contract

Before every public debate turn, every living agent returns:

```text
bid
top_suspect
suspect_confidence_bin
intended_vote
evidence_state
suspect_levels for every other living player
```

The live JSON schema is specialized to the current set of legal player names.
If a model still exhausts semantic-validation retries, the last structured
response is deterministically repaired: valid reported levels are retained,
missing levels become neutral (`2`), and the required categorical choices are
derived from that complete vector. Both private and public repair indicators
are stored in events and summarized in `metrics.json`. Primary temporal PID and
macro estimates exclude transitions involving repaired source states so that a
format recovery cannot masquerade as coordination.

Suspicion and confidence use integer bins 0 through 4. The runtime rejects a
response if a living player is missing, duplicated, out of range, dead, or the
reporting player. The previous public speaker also submits a snapshot, but is
marked ineligible to speak twice consecutively. This produces one complete
private panel at every turn.

The selected speaker must then publish the same complete suspicion vector in
their `say` response. The public response is rejected if the machine-readable
vector differs from the bid-time vector or if any rated player is not named in
the public statement. Nonspeakers' snapshots remain private measurements.

Each `events.jsonl` therefore contains `belief_snapshot` records alongside
`public_message` and `round_extraction` records.

## Agent and macro states

The task-native agent state is

```text
X_i,t = (
  bid,
  top_suspect,
  suspect_confidence_bin,
  intended_vote,
  evidence_state,
  complete_suspect_levels
)
```

The macrostate is a deterministic function of the panel:

```text
V_t = (
  living_player_identities,
  per_candidate_median_suspicion_level,
  group_top_suspect,
  majority_consensus_bin
)
```

Hidden roles are not included in either state. The primary analysis uses roles
only after the game to select the good-agent coalition; a secondary analysis
includes all living agents.

## Estimators

For every unordered pair `(i,j)`, the time-delayed target is
`(X_i,t+1, X_j,t+1)`. The implementation uses Williams--Beer two-source PID
with `I_min` redundancy:

```text
I({X_i,X_j};T) = UI_i + UI_j + Red + Syn
Syn = I({X_i,X_j};T) - I(X_i;T) - I(X_j;T) + I_min
```

The group summary is the median pairwise synergy. The macro criterion preserves
the reference mathematical relation exactly:

```text
S_macro(1) = I(V_t;V_t+1) - sum_k I(X_k,t;V_t+1)
```

Categorical plugin estimates are reported in bits. A temporal-permutation null
shuffles future panels and reports null means, corrected statistics, and
finite-sample p-values. These estimates can be biased in small or sparse cells,
so the output also records transition and pair counts.

## Outputs

After a server matrix completes, the launcher writes:

```text
analysis/temporal_coordination.json
analysis/temporal_coordination.csv
analysis/temporal_coordination.md
```

The source implementation is in `experiment/temporal_coordination.py`, the CLI
is `analyze_temporal_coordination.py`, and the live snapshot contract is in
`werewolf/prompts.py`, `werewolf/model.py`, and `werewolf/game.py`.

## Verification gates

`scripts/verify_three_passes.sh` runs three independent checks before a live
matrix is launched:

1. Unit and definition tests, including XOR synergy, duplicate-source
   redundancy, unique information, complete-panel invariants, and the exact
   macro sum.
2. A deterministic 4-condition by 4-seed fake-model matrix, followed by the
   temporal coordination analyzer.
3. An OpenAI-compatible loopback HTTP test that verifies the full belief schema
   reaches the model server.

Reference: [Emergent Coordination in Multi-Agent Language Models (OpenReview)](https://openreview.net/forum?id=SRn1MtMPRq).
