# Outcome-Aligned Coordination Experiment Pipeline for Werewolf Arena

Status: implementation specification
Repository base: `google/werewolf_arena`
Primary codebase: this directory (Werewolf Arena base plus `experiment/`)
Reference paper: `12455_Emergent_Coordination_in.pdf`

## 1. Purpose

This document specifies the first experimental pipeline for testing the following question:

> Can a multi-agent Werewolf system perform worse even when the good agents collectively possess full, accurate, and positively task-relevant information, and open conversation makes that information available to every living agent?

The experiment is deliberately narrower than the broader topology proposal.

The first version will **not** vary a protocol graph, learn a graph, or treat graph structure as a causal object. The communication setting is fixed:

- every living agent can hear every public debate utterance;
- this includes Villagers, Seer, Doctor, and Werewolves;
- public messages are broadcast to all living agents;
- private observations, night actions, bids, and votes remain private unless an agent chooses to reveal information in a public message;
- the only communication intervention in the first study is the prompt policy that determines what an agent chooses to disclose and how it reasons about disclosure.

The goal is to isolate a simpler distinction:

```text
information is available and accurate
versus
agents use, disclose, integrate, and act on that information effectively
```

The experiment should be able to produce the following scientifically meaningful result:

```text
good-agent evidence coverage increases
good-agent evidence correctness remains high
information-theoretic coordination increases or remains positive
but Good-team task utility decreases
```

If this pattern appears under matched models, roles, evidence, rounds, and budgets, it is a direct demonstration that positive information synergy is not equivalent to beneficial coordination.

## 2. Scope and Non-Goals

### In scope

- the existing eight-player Werewolf Arena game;
- open public debate among all living agents;
- good-agent private evidence that is truthful and positively relevant to the correct decision;
- strategic versus full-disclosure prompt policies;
- strategic and truth-restricted Werewolf controls;
- round-by-round extraction of information from the shared public conversation;
- evidence coverage, evidence correctness, repetition, anchoring, voting, calibration, and game outcome;
- information-theoretic measures as secondary diagnostics;
- message-level counterfactual ablations after the primary pipeline is stable;
- matched repeated games across conditions.

### Out of scope for the first version

- protocol-graph comparisons;
- star, chain, tree, or sparse-graph conditions;
- graph neural networks or graph autoencoders;
- learned routing or dynamic graph generation;
- semantic similarity as evidence of causal influence;
- an agent-full duplicated-evidence condition in which every good agent receives the same complete evidence set;
- a claim that positive synergy universally improves performance;
- a large natural-language benchmark before the controlled fixture is validated;
- changing the basic Werewolf rules during the first pilot.

## 3. Existing Arena Behavior to Preserve

The current repository already has the correct starting point for open conversation.

In `werewolf/game.py`, after a player speaks, `run_day_phase()` updates every active player's `GameView` with the same dialogue. This is the fixed open-broadcast condition for the first experiment.

The current phase sequence is:

```text
Night:
  Werewolf elimination
  Doctor protection
  Seer investigation
  Night resolution
  Winner check

Day:
  bid-based speaker selection
  debate
  public broadcast of the debate message
  voting
  exile by majority
  winner check
  round summaries and private round-level extraction for each living agent
```

The current implementation has `NUM_PLAYERS = 8`, two Werewolves, one Seer, one Doctor, and four Villagers. It has `MAX_DEBATE_TURNS = 8`, although synthetic voting is currently enabled after every debate turn.

The first experiment should preserve this open public debate behavior but make the following variables explicit in the saved experiment configuration:

- random seed;
- role assignment;
- player names;
- model assignment;
- evidence condition;
- good-agent prompt policy;
- Werewolf prompt policy;
- debate-turn limit;
- whether synthetic votes are enabled;
- model-call and token budgets;
- condition identifier.

## 4. Core Experimental Definitions

### 4.1 Good agents

Good agents are all non-Werewolves:

- Villagers;
- the Seer;
- the Doctor.

They share the Villagers' objective: identify and remove both Werewolves.

### 4.2 Open conversation

Open conversation means:

```text
for every public debate message m at turn t:
    every living player receives m in their public debate history
```

The current system already implements this using `GameView.update_debate()`.

The first experiment must not introduce selective recipient sets. We may still log the recipient set as metadata, but it will always equal the set of living players at that turn.

All agents may extract information from every completed public conversation round. A round-level extraction may be a private summary, structured evidence reference, target hypothesis, confidence update, or other memory derived from the messages visible in that round. The extracted information is available to that agent in later-round prompts, but remains private unless the agent later discloses it publicly. Extraction is a shared memory operation, not an additional communication channel.

### 4.3 Accurate positive information

The phrase “positive information” must be operationalized rather than judged by intuition.

Each injected evidence item must have ground-truth metadata:

```text
evidence_id
claim_text
holder
source_type
truth_value
target_hypothesis
direction
strength
directness
```

Required constraints for the primary positive-evidence fixture:

```text
truth_value = true
direction = +1 toward the correct good-team decision
strength > 0
```

Here, `direction = +1` means that the evidence increases the likelihood of the correct hypothesis or action under the fixture's ground-truth scoring rule. It does not mean that the statement sounds optimistic or emotionally positive.

The evidence generator must validate these constraints before a game starts. The LLM must not be responsible for determining whether an evidence item is objectively positive.

### 4.4 System-full complementary information

The union of all good agents' private evidence items is sufficient to identify the correct decision, but no individual good agent has the complete evidence set.

```text
union(E_good_1, ..., E_good_k) -> sufficient for correct action
each E_good_i -> individually insufficient
```

This is the only positive-evidence assignment used in the first experiment. A later study may test duplicated agent-full access, but it is intentionally excluded here so the primary question remains about integrating complementary information through open conversation.

## 5. Research Hypotheses

### H1: Positive information can be outcome-misaligned

Under open conversation, the full-disclosure good-agent condition will produce higher evidence coverage and positive information measures but lower Good-team utility than a matched strategic or centralized control in at least some settings.

### H2: Complementary evidence creates a communication bottleneck without a graph change

Even though everyone can hear every public message, good agents may fail to integrate complementary evidence because:

- a salient first message anchors later reasoning;
- repeated claims are mistaken for independent confirmation;
- agents summarize away uncertainty;
- public agreement becomes a proxy for truth;
- the conversation budget is exhausted before all evidence is processed;
- Werewolves can observe accurate good-agent disclosures and react strategically.

### H3: Prompt policy changes the usefulness of the same evidence

Holding role assignment, evidence, models, and open broadcast constant, a full-disclosure policy and a strategic-disclosure policy may produce different utility despite access to the same underlying evidence.

### H4: Opponent strategy is a separable mechanism

If the effect disappears when Werewolves are instructed to remain truth-restricted, the negative result is partly driven by the interaction between good-agent disclosure and adversarial response. If the effect remains, it supports an internal coordination failure among the good agents themselves.

### H5: Information-theoretic synergy is diagnostic, not sufficient

PID/TDMI-style scores may be positive in both successful and unsuccessful conditions. Their value is explanatory only if they are interpreted together with evidence correctness, disclosure order, redundancy, and held-out utility.

The reference paper motivates this separation: its reported results indicate that synergy or redundancy alone does not predict success, while their interaction is associated with performance. The first experiment should therefore treat information measures as baselines and test their relationship with utility directly.

## 6. Experimental Conditions

The primary study should be small enough to debug and interpretable enough to falsify the hypothesis.

The primary condition set is `C0` through `C3`. The previously considered
agent-full condition is removed; no primary condition gives every good agent a
duplicate copy of the complete evidence set. The optional centralized control
is `C4` and is deferred until the primary conditions are stable.

### Condition C0: Standard open Werewolf baseline

- existing game rules;
- no injected evidence fixture;
- current good-agent prompts;
- strategic Werewolf prompts;
- all public debate messages broadcast to every living player.

Purpose: establish the behavior of the unmodified task under the new logging system.

### Condition C1: Complementary positive evidence plus full disclosure

- system-full complementary evidence;
- every evidence item is truthful and positively relevant;
- each good agent sees only a subset;
- good agents are instructed to disclose as much known and certain information as possible;
- Werewolves use strategic prompts;
- all public messages remain open to all agents.

Purpose: primary test of whether complete accurate information at the team level can produce worse utility when communication is maximally disclosure-oriented.

### Condition C2: Complementary positive evidence plus strategic disclosure

- same evidence distribution as C1;
- same roles, models, seeds, and open broadcast;
- good agents are instructed to choose what and when to disclose strategically;
- good agents may withhold true information but may not invent false evidence;
- Werewolves use the same strategic prompt as C1.

Purpose: isolate the effect of the good-agent communication policy.

### Condition C3: Complementary positive evidence plus truth-restricted Werewolves

- same evidence and good-agent prompt as C1;
- Werewolves receive their private role information but must not fabricate or strategically distort claims;
- open public conversation.

Purpose: diagnose how much of the effect is caused by adversarial response to good-agent disclosure.

### Optional Condition C4: Centralized serialized control

This condition is not required for the first pilot. It can be added after C0-C3 are stable.

A designated single LLM receives the union of good-agent evidence and the public transcript in serialized form and produces the good-team decision. This provides a compute-matched comparison between distributed open conversation and centralized evidence integration.

The centralized control must be clearly labeled as a diagnostic baseline. It is not a faithful continuation of a normal Werewolf game because it changes the decision architecture.

## 7. Prompt Policies

Prompt policies should be inserted as explicit condition-specific blocks rather than rewriting the entire game prompt for each experiment.

Every condition should use the same base rules, state formatting, response schema, and output budget. Only the policy block should change unless the condition explicitly changes evidence availability.

### 7.1 Shared open-conversation instruction

Add to every player's public-debate prompt:

```text
All living players can hear every public debate statement you make. Do not assume that a public statement is private. Bids and votes remain private unless the game rules explicitly reveal them.

You may extract and retain useful information from every completed public debate
round. When you use an extracted observation later, distinguish what was directly
said, what you inferred, and how uncertain you are.
```

This makes the communication regime explicit to the model rather than relying only on code behavior.

### 7.2 Good-agent full-disclosure policy

Suggested policy block:

```text
You are a non-Werewolf and your objective is for the Villagers to win.

Display as much information as you know and are sure about. For every relevant
evidence item, state its evidence ID, the direct observation or fact, and how it
supports your conclusion. Separate direct evidence from your own inference.

Do not invent facts, exaggerate confidence, or claim that another player said
something they did not say. If you are uncertain, label the uncertainty. Your
default is to disclose all known task-relevant evidence rather than strategically
withhold it.
```

The important phrase is “all known task-relevant evidence.” The prompt should not ask the model to reveal hidden role labels directly unless the agent would naturally choose to do so in the game.

### 7.3 Good-agent strategic policy

Suggested policy block:

```text
You are a non-Werewolf and your objective is for the Villagers to win.

Choose what information to disclose, when to disclose it, and how to frame it
based on its expected effect on the team's chance of winning. You may withhold
true information temporarily if doing so improves the team's decision. You may
not fabricate evidence, alter a known fact, or present an unsupported claim as
certain. Distinguish direct evidence, inference, and uncertainty.

You may use information extracted from earlier public conversation rounds, but
keep those extracted observations private unless you choose to disclose them.
```

This condition preserves factual accuracy while allowing strategic information selection.

### 7.4 Strategic Werewolf policy

Suggested policy block:

```text
You are a Werewolf and your objective is for the Werewolves to win.

Use the public conversation strategically. Decide whether to redirect suspicion,
withhold information, challenge accurate claims, or create uncertainty. You may
mislead other players as permitted by the game, but do not break the output
format or claim that the game state itself has changed when it has not. Your role
and your Werewolf teammate's identity are private; do not reveal or explicitly
confirm either one in public.

You may extract information from every public conversation round and use it in
later decisions, while keeping the extracted memory private unless you choose to
disclose it.
```

The exact deception allowance must be recorded in the condition metadata. Otherwise, a change in the Wolf prompt can be mistaken for a change in good-agent coordination.

### 7.5 Truth-restricted Werewolf policy

Suggested diagnostic policy block:

```text
You are a Werewolf and your objective is for the Werewolves to win, but this is
a truth-restricted diagnostic condition. This instruction is internal: do not
reveal or explicitly confirm that you are a Werewolf, and do not reveal or
explicitly confirm the identity of your Werewolf teammate.

You may choose strategically what to say, but you may not fabricate, distort, or
falsely attribute evidence. Base public claims only on facts available in your
private state or the public debate. You may extract information from every
public conversation round and use it later, but keep that extracted memory
private unless you choose to disclose it. Distinguish observed facts, inferences,
and uncertainty.
```

## 8. Evidence Fixture Design

The first evidence fixture should be deterministic, structured, and easy to validate. It should not depend on an LLM deciding whether a natural-language clue is actually positive.

### 8.1 Evidence schema

Create an immutable record such as:

```python
@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    claim_text: str
    holder: str
    source_type: str
    truth_value: bool
    target_hypothesis: str
    direction: int
    strength: float
    directness: str
```

Recommended values:

```text
source_type: observation | role-constraint | vote-pattern | night-event
directness: direct | derived
direction: +1 for positive support of the correct hypothesis
truth_value: true for all primary evidence items
strength: positive real number
```

### 8.2 Evidence assignment mode

Implement the single primary mode:

```python
COMPLEMENTARY = "system_full_complementary"
```

For `COMPLEMENTARY`:

```python
all_good_evidence = generate_positive_evidence(game_state)
subsets = balanced_partition(all_good_evidence, good_players)
player.private_evidence = subsets[player.name]
```

### 8.3 Validation before an episode

Before any model call, assert:

```text
every evidence item is truth-labeled;
every evidence item has direction = +1;
every evidence item has strength > 0;
the complementary union is sufficient according to the fixture oracle;
no individual complementary holder is sufficient alone;
the assignment is identical across prompt-policy conditions for a matched seed;
```

If any assertion fails, mark the fixture invalid and do not spend an API call.

### 8.4 Avoiding a trivial task

Do not make every evidence item say “Player X is a Werewolf.” That turns the task into direct label transmission and does not test coordination.

Use multiple weak but positive facts that jointly distinguish the correct target set. The fixture oracle can compute the correct action from structured metadata, while the LLM sees only natural-language claim text and evidence IDs.

The first fixture should preferably be a one-day decision task embedded in the Arena state:

1. initialize a fixed role assignment;
2. initialize good-agent private evidence;
3. run a controlled public debate;
4. collect private votes;
5. score whether the good team selected a Werewolf.

Only after this one-day task is stable should it be run across the full multi-round game.

## 9. Required Code Changes

The implementation should be additive and preserve the original Arena behavior when no experiment condition is supplied.

### 9.1 New experiment package

Add:

```text
experiment/
  __init__.py
  conditions.py
  evidence.py
  policies.py
  events.py
  metrics.py
  interventions.py
  experiment_runner.py
  analysis.py
  fake_api.py
  tests/
    test_evidence.py
    test_open_broadcast.py
    test_policies.py
    test_metrics.py
    test_serialization.py
```

### 9.2 `conditions.py`

Define a condition object containing:

```python
@dataclass(frozen=True)
class ExperimentCondition:
    condition_id: str
    evidence_mode: str
    good_policy: str
    wolf_policy: str
    public_broadcast: bool = True
    run_synthetic_votes: bool = False
    max_debate_turns: int = 8
```

For this experiment, `public_broadcast` must always be `True`. It is included as metadata and an assertion, not as an experimental factor.

### 9.3 `evidence.py`

Implement:

```text
generate_positive_evidence(state, seed)
validate_evidence(evidence, state)
assign_complementary_evidence(evidence, good_players, seed)
evidence_sufficiency(evidence, state)
```

`evidence_sufficiency()` should be a deterministic fixture-oracle function. It must not call an LLM.

### 9.4 `policies.py`

Store the policy blocks separately from the base prompts:

```text
GOOD_FULL_DISCLOSURE
GOOD_STRATEGIC_DISCLOSURE
WOLF_STRATEGIC
WOLF_TRUTH_RESTRICTED
```

Use a single template slot such as:

```jinja2
{{ coordination_policy }}
```

This prevents accidental changes to the game rules across conditions.

### 9.5 `werewolf/model.py`

Extend `Player` with:

```python
self.private_evidence = []
self.private_round_memory = []
self.experiment_condition = None
```

Extend `_get_game_state()` with:

```python
"private_evidence": [item.to_prompt_dict() for item in self.private_evidence],
"private_round_memory": [item.to_prompt_dict() for item in self.private_round_memory],
"coordination_policy": condition.good_policy or condition.wolf_policy,
```

The evidence IDs and claim texts should be visible to the holder. The hidden gold fields such as `truth_value`, `direction`, and `strength` must not be included in the prompt.

The game state sent to a player should include:

```text
evidence_id
claim_text
source_type
directness
```

It must not include:

```text
truth_value
direction
strength
gold_target_hypothesis
```

### 9.6 `werewolf/prompts.py`

Add optional fields to debate and summary schemas:

```json
{
  "reasoning": "string",
  "say": "string",
  "evidence_refs": ["string"],
  "confidence": "number",
  "round_summary": "string",
  "memory_refs": ["string"]
}
```

For backward compatibility, make `evidence_refs`, `confidence`, `round_summary`,
and `memory_refs` optional at first. The experiment evaluator should distinguish:

```text
structured evidence reference
unstructured factual claim
unsupported assertion
```

Do not ask the model to output hidden ground-truth labels.

For the round-extraction call, use the same role-specific game view plus the
completed round's public message IDs and dialogue. The response should contain
only the extractor's private memory; never copy one player's extraction into a
different player's prompt.

### 9.7 `werewolf/game.py`

Preserve the existing open broadcast, but add explicit message metadata:

```python
message_id = f"r{round_number}_t{turn_number}_{speaker}"
recipients = list(self.this_round.players)
```

Store an event such as:

```python
PublicMessageEvent(
    message_id=message_id,
    round_number=round_number,
    turn_number=turn_number,
    speaker=speaker,
    recipients=recipients,
    dialogue=dialogue,
    evidence_refs=parsed_evidence_refs,
)
```

This is a message log, not a protocol graph. Do not add graph-learning code in this phase.

The event should be emitted immediately before the message is broadcast and immediately after the broadcast is applied, so tests can verify that every living player received it.

Make round-level extraction explicit after each completed public debate round.
The extraction operation may reuse the existing summary mechanism, but it must
be logged as a separate private event with the source message IDs, extracted
claims, confidence, and the player who owns the memory. The extraction is
available in that player's later-round prompt only; it must not be silently
injected into other players' views.

Also fix or control these existing behaviors before data collection:

- use a unique session ID;
- inject and record a random seed;
- disable synthetic votes for the main primary decision unless the analysis explicitly needs intermediate votes;
- fix the protected-target view update in `resolve_night_phase()`;
- ensure round summaries happen at the intended point in the documented sequence.
- include round-extraction calls in the declared model-call and token budgets;
- keep round-extraction prompts and responses in the raw logs, separate from public messages.

### 9.8 `werewolf/lm.py` and `werewolf/apis.py`

Extend `LmLog` with optional metadata:

```python
action
player
role
round_number
turn_number
condition_id
seed
retry_count
latency_ms
input_tokens
output_tokens
evidence_refs
```

The first implementation may leave token fields null when the provider does not return usage. It must still record the provider, model ID, temperature, and retry count.

Fix the provider interface so that the same names are used consistently:

```text
response_schema -> provider schema argument
temperature -> provider temperature argument
```

The current Vertex path uses `json_schema` while the shared call passes `response_schema`. This must be normalized before structured-output comparison.

### 9.9 `werewolf/runner.py`

Add experiment flags:

```text
--experiment_condition
--experiment_seed
--experiment_config
--output_dir
--disable_synthetic_votes
```

The runner should create a manifest before the first model call:

```json
{
  "condition_id": "C1_complementary_full_disclosure",
  "seed": 1001,
  "role_assignment": {...},
  "player_names": [...],
  "villager_model": "...",
  "werewolf_model": "...",
  "evidence_mode": "system_full_complementary",
  "good_policy": "full_disclosure",
  "wolf_policy": "strategic",
  "public_broadcast": true,
  "max_debate_turns": 8,
  "synthetic_votes": false,
  "round_extraction": true,
  "extraction_schema_version": "v1"
}
```

### 9.10 `index.ts`

The viewer is not required for the first analysis. It can be updated later to display:

- evidence IDs;
- whether an evidence item was newly introduced or repeated;
- message turn;
- evidence-reference coverage;
- good-agent versus Werewolf policy;
- intervention labels.

Do not make the viewer the source of truth. All metrics must be computed from saved JSON or JSONL artifacts.

## 10. Public-Conversation Logging Contract

Every public debate message must produce one immutable event.

Suggested JSONL event:

```json
{
  "event_type": "public_message",
  "event_id": "r1_t3_Derek",
  "round": 1,
  "turn": 3,
  "speaker": "Derek",
  "speaker_role_hidden_from_analysis": true,
  "recipients": ["Derek", "Scott", "Jacob"],
  "dialogue": "...",
  "evidence_refs": ["E02", "E04"],
  "claim_ids": ["C17", "C18"],
  "confidence": 0.72,
  "prompt_policy": "good_full_disclosure",
  "condition_id": "C1_complementary_full_disclosure"
}
```

The analysis copy may use the ground-truth role, but the model-facing prompt and any blinded evaluator must not receive it.

The recipients field should always equal the living-player set in the primary experiment. This makes openness auditable without introducing topology as a factor.

Every agent may also emit one private `round_extraction` event after each
completed public debate round. A suggested event is:

```json
{
  "event_type": "round_extraction",
  "event_id": "r1_extract_Scott",
  "round": 1,
  "player": "Scott",
  "source_message_ids": ["r1_t1_Derek", "r1_t2_Jacob"],
  "extracted_claims": ["E02 supports the same target as E04"],
  "summary": "...",
  "confidence": 0.68,
  "visible_to": ["Scott"],
  "condition_id": "C1_complementary_full_disclosure"
}
```

The extraction event records what the agent carried forward from the round; it
does not create a new broadcast. The source message IDs make later claims
auditable and allow the analysis to separate direct public information from
private cross-round memory.

## 11. Metrics

Metrics are divided into information availability, communication behavior, task utility, and causal contribution.

### 11.1 Primary task utility

At the game level:

```text
GoodTeamWin = 1 if Villagers win, else 0
WolfTeamWin = 1 if Werewolves win, else 0
```

At each day decision:

```text
correct_wolf_exile = 1 if a Werewolf is exiled
wrong_good_exile = 1 if a non-Werewolf is exiled
no_majority = 1 if nobody is exiled
```

Define a simple utility score:

```text
U_day = +1 for correct Werewolf exile
        -1 for incorrect Good-agent exile
         0 for no majority
```

Also report:

- round of first Werewolf removal;
- good-agent survival count;
- final vote entropy;
- calibration of confidence in the chosen target;
- parse failure rate;
- number of retries;
- total latency and token usage when available.

### 11.2 Evidence availability

```text
evidence_coverage = unique_gold_evidence_publicly_referenced_before_vote
                    / total_gold_evidence
```

For the complementary condition, also report whether the full union of evidence was publicly surfaced at least once before the decision.

### 11.3 Evidence correctness

For every evidence reference:

```text
correct_reference = 1 if the cited evidence ID exists and the claim matches it
unsupported_claim = 1 if a message asserts a fact without a valid evidence reference
contradiction = 1 if the message contradicts a ground-truth evidence item
```

The primary positive-information condition should have high evidence correctness. If correctness is low, the condition is not a valid test of “more accurate positive information.”

### 11.4 Novelty and redundancy

```text
novel_evidence_rate = newly introduced evidence references / all evidence references
echo_rate = repeated evidence references with no added support / all references
```

The same evidence item repeated by multiple agents is not independent evidence. The analysis must preserve the evidence ID so repeated claims are not accidentally counted as new information.

### 11.5 Anchoring and premature consensus

Measure:

- identity of the first target named;
- fraction of later messages mentioning that target;
- fraction of final votes for the first target;
- turns until a majority of votes align;
- whether later messages add independent evidence or merely repeat the first target;
- order sensitivity under replayed evidence-disclosure order.

A useful anchoring index is:

```text
anchoring_index = later_votes_for_first_named_target / later_valid_votes
```

Interpret this together with whether the first target was correct.

### 11.6 Round-level extraction

Report whether agents successfully carry public information across rounds:

```text
extraction_coverage = source messages or evidence items carried into later memory
                      / source messages or evidence items available to extract
extraction_fidelity = extracted claims consistent with their source messages
                      / all extracted claims
cross_round_reuse = later public claims supported by prior-round extraction
                    / all later supported claims
```

Also report extraction compression or loss, such as the number of distinct
evidence IDs available in a round versus the number retained in the next-round
private memory. These metrics are descriptive and should not be treated as
causal unless paired with a memory-ablation intervention.

### 11.7 Information-theoretic diagnostics

Use the paper's measures as secondary diagnostics, not as the primary utility metric.

For pairwise agent trajectories:

```text
I((X_i,t, X_j,t); T_ij,t+ell)
  = UI_i + UI_j + Red_ij + Syn_ij
```

The pairwise synergy term `Syn_ij` measures predictive information available jointly from the pair.

For the macro criterion:

```text
S_macro(ell) = I(V_t; V_t+ell)
               - sum_k I(X_k,t; V_t+ell)
```

For triplet information:

```text
I_3 = I((X_i,t, X_j,t, X_k,t); V_t+ell)
G_3 = I_3 - max(I_2{1,2}, I_2{1,3}, I_2{2,3})
```

Recommended trajectory variables for the first implementation are discrete and auditable:

```text
bid value
named target
whether a new evidence ID was introduced
whether a previous evidence ID was repeated
whether confidence increased or decreased
```

Do not apply PID directly to unconstrained raw text in the first pass. Text embeddings may be retained for exploratory analysis, but they are not a causal measure and should not replace evidence IDs.

### 11.8 Outcome-Aligned Causal Synergy candidates

For an observed message `m`, estimate:

```text
Delta_m = E[U | message kept]
          - E[U | message blocked]
```

For a pair of evidence sources or agents:

```text
Gamma_ij = U(do(i,j))
            - U(do(i))
            - U(do(j))
            + U(do(empty))
```

These quantities should be reported alongside, not hidden inside, information-only measures.

## 12. Counterfactual Message Interventions

The primary run should be natural open conversation. Interventions are a second pass used to test mechanism.

### Intervention M0: Keep

The original transcript is shown to all living players.

### Intervention M1: Remove first salient disclosure

The first public message that references a designated evidence item or target is withheld from subsequent player views.

All other rules remain unchanged.

### Intervention M2: Remove repeated evidence

After evidence item `E_i` has already been disclosed, later messages that merely repeat `E_i` are replaced with a length-matched neutral marker for the analysis replay.

### Intervention M3: Delay evidence

The message containing an evidence item is delivered after one debate turn, while preserving its content and total message budget.

### Intervention M4: Replace unsupported certainty

Replace a high-confidence unsupported statement with a neutral confidence-matched control. This tests whether confidence framing, rather than information content, caused the utility change.

### Paired-run requirements

For every intervention, preserve:

- role assignment;
- evidence assignment;
- model IDs;
- condition prompt;
- random seed;
- number of turns;
- token and response-length budgets;
- public recipient set.

Because LLM calls are stochastic, one exact replay is not enough. Use repeated paired runs per seed and report the distribution of intervention effects.

## 13. Analysis Plan

### 13.1 Primary contrasts

The first statistical comparisons are:

```text
C1 vs C0: effect of adding complementary positive evidence under full disclosure
C2 vs C1: effect of strategic versus full-disclosure good-agent prompts
C3 vs C1: effect of restricting Werewolf deception
```

### 13.2 Evidence that supports the negative-performance claim

The claim “more positive information can produce worse performance” should require all of the following:

1. C1 has higher evidence coverage than C0 or C2.
2. C1 evidence correctness remains high.
3. The union of good-agent evidence is validated as sufficient by the fixture oracle.
4. C1 has lower Good-team utility or lower `U_day`.
5. The result replicates across seeds and role assignments.
6. The effect is not explained only by parsing failures, token overrun, or a different number of model calls.
7. Message ablations identify a plausible mechanism such as anchoring, repetition, or premature consensus.

If only game win rate decreases but evidence correctness also decreases, the result is not yet evidence for the proposed phenomenon. It may simply be an evidence-generation or parsing failure.

### 13.3 Statistical reporting

Report:

- per-condition game count;
- per-condition Good-team win rate;
- mean and median `U_day`;
- bootstrap confidence intervals;
- paired differences when fixtures are matched;
- effect sizes, not only p-values;
- evidence coverage and correctness;
- echo and anchoring indices;
- model-call counts, retries, latency, and tokens;
- failed or incomplete episodes.

For multi-model studies, use a mixed-effects or blocked model with at least:

```text
condition
model assignment
role assignment
seed block
game index
```

Do not aggregate all games into one average before checking seed and role heterogeneity.

## 14. Output Artifacts

Each episode should create a directory such as:

```text
runs/
  C1_complementary_full_disclosure/
    seed_1001/
      manifest.json
      evidence.json
      game_complete.json
      game_logs.json
      events.jsonl
      metrics.json
      stdout.txt
```

The aggregate analysis should create:

```text
results/
  episode_metrics.csv
  condition_summary.csv
  intervention_effects.csv
  evidence_coverage.csv
  pid_tdmi_diagnostics.csv
  figures/
  analysis_report.md
```

The raw prompt and raw response must remain available. Do not keep only parsed actions.

## 15. Reproducibility Requirements

Every episode must record:

- Git commit hash;
- condition ID;
- random seed;
- role assignment;
- player names;
- model IDs;
- temperature;
- prompt-policy version;
- evidence-fixture version;
- response schema version;
- debate-turn limit;
- synthetic-vote setting;
- retry count;
- provider metadata;
- start and end timestamps.

The current repository has several uncontrolled random operations, including player sampling, option shuffling, prompt player ordering, and tie-breaking. The experiment runner must seed all of them or replace them with an experiment RNG whose state is logged.

## 16. Implementation Phases

### Phase 0: Offline fixture and parser tests

No external model calls.

Tests:

- positive evidence validator rejects false or non-positive items;
- complementary union is sufficient;
- each individual subset is insufficient;
- public messages reach all living players;
- dead players receive no later messages;
- evidence IDs survive serialization;
- every living agent can create a private round extraction with source message IDs;
- malformed model output is logged as a parse failure;
- condition metadata survives save/load.

### Phase 1: Deterministic fake-model game

Use `fake_api.py` to return deterministic JSON responses.

Verify:

- the game completes;
- the public transcript is identical across players;
- private evidence remains private until disclosed;
- evidence references are captured;
- every round has the expected number of events;
- metrics match hand-computed examples.

### Phase 2: One-model pilot

Run a small pilot using one model for all roles.

Recommended first pilot:

```text
5-10 games per condition
fixed role assignment block
fixed evidence fixture block
multiple random seeds
synthetic votes disabled
```

The purpose is debugging, not statistical inference.

### Phase 3: Controlled day-vote experiment

Run the one-day fixture before full games.

This is the fastest way to determine whether full accurate positive evidence can cause:

- higher coverage;
- higher public repetition;
- lower vote accuracy;
- greater anchoring;
- lower utility.

### Phase 4: Full-game replication

Run the same conditions across complete multi-round games after the day-vote effect is stable.

The number of episodes should be selected after the pilot using variance estimates and a power or precision target. A practical starting point is 50-100 episodes per primary condition, with the final count justified by confidence-interval width rather than an arbitrary number.

### Phase 5: Message interventions

Run M1-M4 on a selected subset of conditions and seeds. Do not add interventions before the natural open-broadcast pipeline is validated.

## 17. Acceptance Criteria

The pipeline is ready for analysis only when:

- all primary conditions use open broadcast;
- no protocol graph factor is present;
- evidence assignments are reproducible;
- all primary evidence items are verified truthful and positively relevant;
- the complementary union is sufficient according to the fixture oracle;
- all model prompts include the correct condition policy;
- good-agent and Werewolf policy versions are stored in the manifest;
- every public message has a message ID and recipient list;
- raw prompts, raw responses, parsed results, and retry failures are saved;
- task utility and evidence metrics are computed independently;
- a fake-model test passes;
- the viewer is not required for metric computation;
- the current protected-target state bug and session-ID collision are fixed or explicitly excluded from the pilot;
- matched conditions have equal model-call, turn, and token budgets within the declared tolerance.

## 18. Interpretation Rules

### Positive result for the central hypothesis

The strongest result would look like:

```text
C1 evidence coverage > C2 evidence coverage
C1 evidence correctness remains high
C1 Syn/TDMI diagnostic is positive or higher
C1 anchoring/repetition is higher
C1 Good-team utility is lower
C1 message ablations recover utility
```

This would support the conclusion that positive joint information can coexist with worse task performance because the open conversation protocol causes misintegration.

### Adversarial-response result

If C1 under strategic Werewolves performs worse but C3 improves substantially, the effect is partly caused by the fact that accurate good-agent disclosure gives the opponent information to counteract.

This is still a valid result, but it should be described as an interaction between truthful coordination and adversarial adaptation rather than purely internal good-agent failure.

### Internal-coordination result

If C1 remains worse than C3, the result is stronger evidence that accurate positive information can be mishandled by the good agents themselves through redundancy, anchoring, confidence, or context overload.

### Null result

If C1 improves utility, that is also informative. It would show that the fixture and prompt policy do not create the hypothesized failure under the tested conditions. Do not redefine the metric after seeing the outcome.

If PID/TDMI is positive but does not predict utility, retain that as a negative result for information-only coordination and continue testing the outcome-aligned metric.

## 19. Recommended First Implementation Order

```text
1. Freeze a commit of google/werewolf_arena.
2. Add condition and seed manifests.
3. Add the positive evidence schema and validator.
4. Add complementary evidence assignment.
5. Add full-disclosure and strategic good-agent prompt blocks.
6. Add strategic and truth-restricted Wolf prompt blocks.
7. Add evidence IDs and structured evidence references to debate outputs.
8. Add public-message event logging with all-living-player recipients.
9. Disable synthetic votes for the primary day-vote task.
10. Fix protected-target view synchronization.
11. Add fake-model tests.
12. Run the one-day controlled fixture.
13. Compute utility, evidence coverage, correctness, redundancy, and anchoring.
14. Run the small one-model pilot.
15. Add PID/TDMI diagnostics.
16. Add paired message interventions.
17. Replicate in full multi-round games.
```

## 20. Bottom Line

The first experiment should not ask whether one communication graph is better than another. It should ask a cleaner question:

> When every living agent can hear every public message, and the good agents collectively possess only truthful, positively useful evidence, does a prompt that maximizes disclosure improve or reduce the final decision quality?

The implementation must keep these quantities separate:

```text
what the good agents knew
what they disclosed
what other agents repeated
what the Werewolves observed
what the good agents believed
what they voted for
whether the vote was correct
```

That separation is the essential bridge from the existing Werewolf Arena evaluator to the proposed Outcome-Aligned Coordination study.
