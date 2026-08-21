# Three-pass validation of task sources and synergy compatibility

## Scope and result

This file audits the ten candidates in
[`MULTI_AGENT_TASK_GENERALIZATION_CANDIDATES.md`](MULTI_AGENT_TASK_GENERALIZATION_CANDIDATES.md)
against the current repository and primary/official external sources. The audit
passed all three layers with qualifications recorded below. “Passed” does not
mean every source natively implements the proposed multi-agent experiment. It
means the report accurately labels which parts are source facts and which parts
are proposed adaptations, and that each proposed adaptation can satisfy the
existing estimator contract.

## Validation 1: primary-source fidelity

### Method

For every candidate, factual benchmark claims were checked against an original
paper and, where available, the authors' official repository. Secondary blog or
survey claims were not used as the sole evidence. The native/adapted status was
then checked explicitly.

| Candidate | Primary paper checked | Official code checked | Source-native multi-agent? | Audit result |
|---|---|---|---|---|
| SWE-bench | [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html) | [SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench) | No | Pass: report calls the team organization a proposed wrapper |
| LeanDojo | [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/4441469427094f8873d0fecb0c4e1cee-Abstract-Datasets_and_Benchmarks.html) | [lean-dojo/LeanDojo](https://github.com/lean-dojo/LeanDojo) | No | Pass: proof-team roles are labeled proposed |
| BIRD-INTERACT | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/496b549556509bbb9770bf9d335c5800-Abstract-Conference.html) | [bird-bench/BIRD-Interact](https://github.com/bird-bench/BIRD-Interact) | No; interactive agent plus environment/user simulator | Pass: dynamic CRUD/test claims are native; database team is proposed |
| Cybench | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/3e9412a9c1d93810ef3ef7825115016b-Abstract-Conference.html) | [andyzorigin/cybench](https://github.com/andyzorigin/cybench) | No | Pass: team roles are proposed and sandbox scope is explicit |
| Hanabi | [Original challenge paper](https://arxiv.org/abs/1902.00506) | [DeepMind HLE](https://github.com/google-deepmind/hanabi-learning-environment) | Yes | Pass: purely cooperative, 2–5 players, imperfect information |
| Overcooked | [NeurIPS 2019](https://proceedings.neurips.cc/paper_files/paper/2019/hash/f5b1b89d98b7286673128a5fb112cb9a-Abstract.html) | [HumanCompatibleAI/overcooked_ai](https://github.com/HumanCompatibleAI/overcooked_ai) | Yes | Pass: shared performance is native; explicit reports are new instrumentation |
| Diplomacy | [Science paper record](https://pubmed.ncbi.nlm.nih.gov/36413172/) | [facebookresearch/diplomacy_cicero](https://github.com/facebookresearch/diplomacy_cicero) | Yes | Pass: seven-player cooperation/competition and negotiation are native |
| Melting Pot | [ICML 2021](https://proceedings.mlr.press/v139/leibo21a.html) | [google-deepmind/meltingpot](https://github.com/google-deepmind/meltingpot) | Yes | Pass: social dilemmas/resource sharing/generalization claims are native |
| Watch-And-Help | [ICLR 2021](https://iclr.cc/virtual/2021/spotlight/3491) | [Watch-And-Help](https://github.com/xavierpuigf/watch_and_help), [CoELA](https://github.com/UMass-Embodied-AGI/CoELA) | Yes | Pass: collaborative household task is native; CoELA supports communicative extension |
| LLM debate | [ICML 2024](https://proceedings.mlr.press/v235/khan24a.html) | [ucl-dark/llm_debate](https://github.com/ucl-dark/llm_debate) | Yes, competing debaters and judge | Pass: answer/judge evaluation is native; structured evidence-state panels are proposed |

### Important source caveats

- The SWE-bench, LeanDojo, BIRD-INTERACT, and Cybench papers do **not** provide
  the multi-agent organizations proposed here.
- Overcooked and Melting Pot provide multi-agent environments but do not
  natively require the structured language-state panels proposed here.
- The original Hanabi Learning Environment is archived/read-only, although it
  remains the authors' released environment and is usable as a pinned artifact.
- The ICML 2024 debate implementation evaluates debaters and judges, but the
  claim/evidence state panels needed by our temporal estimator are proposed
  instrumentation rather than a source feature.

## Validation 2: fit to the current temporal coordination contract

### Seven fit gates

Each proposed experiment was evaluated *after the explicitly described
instrumentation/wrapper* against seven gates:

- **A:** at least two interdependent decision makers;
- **T:** repeated, ordered interactions with a meaningful `t+1`;
- **I:** private, local, or complementary information;
- **C:** an action or communication channel by which agents can coordinate;
- **S:** a fixed discrete individual state and deterministic macrostate can be
  serialized;
- **U:** positive task utility is machine-checkable or operationally explicit;
- **N:** a temporal null can permute future panels without changing group/stratum.

| Candidate | A | T | I | C | S | U | N | Result and main qualification |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| SWE-bench team | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Ready after access/role partition wrapper |
| LeanDojo proof team | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Ready; Lean step is the natural clock |
| BIRD-INTERACT team | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Ready; use isolated DB copies for writes |
| Cybench team | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Ready only in authorized sandbox |
| Hanabi | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Strongest direct fit; legal hints/actions are communication |
| Overcooked | ✓ | ✓ | △ | ✓ | ✓ | ✓ | ✓ | Local observations or assigned roles must create complementarity |
| Diplomacy | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Preregister coalition/system utility |
| Melting Pot | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Choose substrates with an explicit system-welfare outcome |
| Communicative WAH | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | High fit; high-dimensional visual observations stay outside categorical state |
| Evidence debate | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | Requires known-answer evidence corpus and a fixed judge protocol |

`△` is a design dependency rather than a factual failure. In fully observable
Overcooked, identical observations could make the information-complementarity
hypothesis weak. Use egocentric/local observation, distinct responsibilities,
or complementary noisy sensors, and report that intervention explicitly.

### Relation to the repository

The gates match the actual code rather than a loose description:

- [`agent_state`](../code/experiment/temporal_coordination.py) freezes a
  categorical per-agent report.
- [`macro_state`](../code/experiment/temporal_coordination.py) deterministically
  aggregates the complete panel without hidden roles.
- the pair target is the two agents' next states;
- `_macro_criterion` subtracts the **sum** of individual predictive
  information from macrostate predictive information;
- repaired source states are excluded, and future panels are permuted to form
  a temporal null.

## Validation 3: information-theoretic implementability and leakage audit

### Required implementation assertions

Each new task must pass these assertions before model experiments:

1. `X_i,t` is recorded before the selected action or message is executed.
2. Every eligible agent appears exactly once in panel `t`.
3. Legal candidate/action vocabularies and agent identities are stored with the
   panel.
4. `V_t` is reproducible byte-for-byte from panel `t` and declared public state.
5. Hidden truth, future simulator/test output, terminal winner, and evaluator
   labels do not appear in `X_i,t` or `V_t`.
6. Outcome utility is saved in a separate record and joined only for analysis.
7. Free text is not used directly as a categorical state; use enumerations,
   bins, immutable evidence IDs, or version hashes.
8. Dynamic agent/candidate sets are stratified or versioned.
9. Repaired/invalid panels are marked, with the primary estimator excluding
   affected transitions.
10. The permutation null shuffles future panels only within compatible task,
    model, condition, coalition, and state-space strata.
11. At least one known synthetic synergy case, one redundancy case, and one
    zero-information case pass before live runs.
12. Coordination metrics and positive utility are jointly reported; neither is
    described as the other.

### Candidate-specific leakage and estimator risks

| Candidate | Main leakage risk | Main sparsity/cardinality risk | Required mitigation |
|---|---|---|---|
| SWE-bench | future test result encoded in reviewer belief | file paths and patch text | pre-action states; path vocabulary + patch hashes |
| LeanDojo | post-tactic Lean result included at time `t` | raw proof-state text | proof-state hash/categories; result belongs to `t+1` |
| BIRD-INTERACT | expected row result copied from test oracle | SQL strings/schema breadth | schema IDs, operation classes, SQL hash; isolate oracle |
| Cybench | solution flag/subtask answer exposed | command/artifact strings | evidence IDs and command classes; sandboxed oracle |
| Hanabi | own hidden cards leaked | belief distribution combinations | legal observation only; discretized beliefs |
| Overcooked | future completed dish in current progress | positions/object combinations | macro-actions/zones and finite workflow stages |
| Diplomacy | simultaneous future orders leaked | board/commitment graph size | panel before order reveal; hashed finite commitments |
| Melting Pot | realized next reward placed in forecast | continuous resources/positions | resource and spatial bins; reward separate |
| Watch-And-Help | ground-truth goal given to helper state | object/location graph size | observed/inferred predicates only; graph hashes/bins |
| Evidence debate | gold answer or evidence label included | unbounded claims/text | immutable evidence/claim IDs; gold used only for utility |

### Validation conclusion

All ten tasks can support the current synergy and macro framework **if** their
proposed instrumentation is implemented as specified. Five are especially
strong pilots: Hanabi, BIRD-INTERACT, SWE-bench, Communicative Watch-And-Help,
and LeanDojo. They jointly span distinct fields while providing temporal state,
controlled information complementarity, and an external outcome oracle.

The largest scientific risk is not lack of tasks. It is silently changing the
meaning of collaboration across tasks. The common definition should therefore
be preregistered as:

> Multiple stable agents exhibit outcome-aligned collaboration when their
> time-indexed joint state contains non-null predictive information about
> future joint/macro state that is not reducible to the agents individually,
> and this coordination is associated with improved predeclared task utility.

The first clause is measured by temporal PID and the macro criterion. The
second is measured by each task's external verifier or system utility. Both are
required.

## Executed validation record (August 21, 2026)

1. **Source fidelity:** 23 unique external links in the reports were resolved
   to original conference/arXiv records, official project pages, or author
   repositories. Claims used in the report were checked against those primary
   descriptions. The audit table records every source-native/adapted boundary.
2. **Repository fidelity:** the state tuple, deterministic macro reducer,
   future-pair target, Williams--Beer `I_min` calculation, sum-based macro
   criterion, repair exclusion, and temporal permutation null were checked
   directly in `code/experiment/temporal_coordination.py` and its implementation
   note. No proposed state includes hidden roles or future outcomes.
3. **Mechanical validation:** automated checks found exactly 10 numbered task
   candidates, 10 source sections, 4 state designs, and 10 fit-matrix rows; all
   referenced local files exist. The nine directly relevant temporal-state/PID
   tests passed, including XOR synergy, redundancy, unique information,
   independent targets, hidden-role exclusion, complete panels, repair
   exclusion, and the exact sum-based macro definition.

The broader publication snapshot has additional integration tests with optional
runtime dependencies. Those are outside this document-only change; the saved
server validation in the parent [`README.md`](../README.md) records the full
environment-backed validation of the experiment code.
