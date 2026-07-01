# Discussion Summary: Emergent Coordination in Multi-Agent Language Models

Paper: *Emergent Coordination in Multi-Agent Language Models*  
Author: Christoph Riedl  
Venue: ICLR 2026  
Related deep dive: `DEEP_DIVE_RIEDL_2026_EMERGENT_COORDINATION.md`

## 1. Core Question

The paper asks when a multi-agent LLM system is merely a collection of independent agents and when it becomes a coordinated collective with higher-order structure.

The important distinction is:

- A group can perform well without true coordination, for example by averaging noise or following the same prompt.
- A group shows emergent coordination when the future behavior of the whole system contains information that cannot be recovered from any individual agent alone.

The paper therefore studies internal group dynamics, not just final task success.

## 2. Experimental Design

The experiment uses a minimalist group guessing game, also described as group binary search.

- Each agent privately proposes an integer.
- The agents' guesses are summed.
- The group succeeds when the sum exactly matches a hidden target number.
- Agents do not directly communicate.
- Agents do not see each other's guesses.
- Agents receive only group-level feedback: "too high" or "too low."
- If all agents follow identical binary-search behavior, the group can oscillate.
- Success requires complementary behavior: some agents need to guess higher while others guess lower.

The main intervention conditions are:

| Condition | Description | Intended effect |
|---|---|---|
| Plain | Basic task prompt | Baseline feedback-following behavior |
| Persona | Each agent receives a distinct persona | Stable identity-linked differences |
| Persona + ToM | Persona plus instruction to think about what other agents might do | Mutual modeling and complementary adaptation |

The Theory-of-Mind prompt is a prompt-level intervention, not a claim that the agents truly possess human-like theory of mind.

## 3. Main Variables

The raw data are round-by-round agent guesses. The paper converts guesses into equal-share deviations:

```text
dev_i,t = raw_guess_i,t - target / N
```

This measures whether agent `i` contributed above or below the equal share needed to hit the target.

The macro-level group error is:

```text
V_t = sum_i raw_guess_i,t - target
```

Equivalently:

```text
V_t = sum_i dev_i,t
```

Interpretation:

- `V_t > 0`: the group sum is too high.
- `V_t < 0`: the group sum is too low.
- `V_t = 0`: the group hits the target.

## 4. Algorithms and Methodology

The paper combines information-theoretic measures, surrogate null tests, and mixed-model tests.

Main algorithms and statistical tools:

| Tool | Purpose |
|---|---|
| Time-delayed mutual information (TDMI) | Measures whether current states predict future states |
| Partial information decomposition (PID) | Splits joint information into unique, redundant, and synergistic parts |
| Williams-Beer two-source PID | Main PID method |
| `I_min` redundancy | Main redundancy definition in Williams-Beer PID |
| Quantile binning | Reduces numeric deviations to low/high bins for probability estimation |
| Jeffreys prior smoothing | Adds `alpha = 1/2` pseudo-counts to avoid empty bins |
| Miller-Madow estimator | Robustness check for entropy bias correction |
| MMI redundancy | Conservative robustness check that tends to overestimate redundancy |
| Row-wise shuffle null | Breaks identity-linked structure |
| Column-wise / block time shuffle null | Breaks longer-range dynamic alignment while preserving local structure |
| Fisher's method | Combines p-values across independent groups |
| Wilcoxon signed-rank test | Tests whether bias-corrected estimates are above zero |
| Hierarchical mixed models | Tests whether agents develop stable role-like differentiation |
| Likelihood-ratio tests | Compares nested models `m0 -> m1 -> m2` |

## 5. Emergence Capacity: Pairwise PID

For a pair of agents `(i, j)`, the paper asks whether their current states jointly predict their future joint state.

Current sources:

```text
X_i,t
X_j,t
```

Future target:

```text
T_ij,t+ell = (X_i,t+ell, X_j,t+ell)
```

Predictive information is decomposed as:

```text
I({X_i,t, X_j,t}; T_ij,t+ell)
  = UI_i + UI_j + Red_ij + Syn_ij
```

Meaning:

- `UI_i`: information uniquely provided by agent `i`.
- `UI_j`: information uniquely provided by agent `j`.
- `Red_ij`: redundant information shared by both agents.
- `Syn_ij`: information available only from the pair jointly.

The group-level emergence capacity is computed by calculating `Syn_ij` for all unordered pairs and taking the median.

## 6. Numerical PID Example: XOR-Style Synergy

Use a simplified two-agent example. Let:

```text
X = current state of agent i
Y = current state of agent j
T = future target state
```

Suppose the data follow an XOR pattern:

| X | Y | T |
|---|---|---|
| Low | Low | 0 |
| Low | High | 1 |
| High | Low | 1 |
| High | High | 0 |

Assume all four rows are equally likely.

First compute the entropy of `T`:

```text
p(T = 0) = 1/2
p(T = 1) = 1/2

H(T) = -[1/2 log2(1/2) + 1/2 log2(1/2)]
     = 1 bit
```

Single-source information:

- If we know only `X`, `T` is still half 0 and half 1.
- If we know only `Y`, `T` is still half 0 and half 1.

Therefore:

```text
I(X; T) = 0
I(Y; T) = 0
```

Joint information:

- If we know `(X, Y)`, `T` is fully determined.

```text
H(T | X,Y) = 0
I(X,Y; T) = H(T) - H(T | X,Y)
          = 1 - 0
          = 1 bit
```

Because neither single source contains information:

```text
Red_XY = 0
UI_X = I(X; T) - Red_XY = 0
UI_Y = I(Y; T) - Red_XY = 0
Syn_XY = I(X,Y; T) - UI_X - UI_Y - Red_XY
       = 1 - 0 - 0 - 0
       = 1 bit
```

Interpretation:

The information is not in either agent alone. It is in the relationship between the two agents. This is the cleanest toy example of synergy.

## 7. Redundancy Example: Not Synergy

Suppose both agents give the same signal:

| X | Y | T |
|---|---|---|
| Low | Low | Low |
| High | High | High |
| Low | Low | Low |
| High | High | High |

Here:

```text
I(X; T) = 1
I(Y; T) = 1
I(X,Y; T) = 1
Red_XY = 1
UI_X = 0
UI_Y = 0
Syn_XY = 0
```

Interpretation:

The agents are aligned, but they provide overlapping information. This is redundancy, not synergy.

## 8. TDMI: Numerical Examples

Time-delayed mutual information measures whether the current state predicts a future state:

```text
TDMI(ell) = I(X_t; X_t+ell)
```

### Perfect alternating sequence

Suppose group state is either `H` for too high or `L` for too low:

```text
H, L, H, L, H, L
```

Then:

```text
H(X_t+1) = 1 bit
H(X_t+1 | X_t) = 0
I(X_t; X_t+1) = 1 - 0 = 1 bit
```

Knowing the current state completely predicts the next state.

### Random sequence

If:

```text
p(X_t+1 = H | X_t = H) = 1/2
p(X_t+1 = L | X_t = H) = 1/2
```

and similarly for `X_t = L`, then:

```text
H(X_t+1) = 1 bit
H(X_t+1 | X_t) = 1 bit
I(X_t; X_t+1) = 0
```

The current state has no predictive information about the next state.

### Partially predictable sequence

Suppose:

```text
p(X_t+1 = H | X_t = H) = 0.8
p(X_t+1 = L | X_t = H) = 0.2
p(X_t+1 = L | X_t = L) = 0.8
p(X_t+1 = H | X_t = L) = 0.2
```

Then:

```text
H(X_t+1) = 1 bit
H(X_t+1 | X_t)
  = -[0.8 log2(0.8) + 0.2 log2(0.2)]
  = 0.722 bits

I(X_t; X_t+1) = 1 - 0.722
              = 0.278 bits
```

The current state is informative, but not fully predictive.

## 9. Practical Emergence Criterion

The practical criterion asks whether the macro group state predicts its future better than the summed individual parts:

```text
S_macro(ell) = I(V_t; V_t+ell) - sum_k I(X_k,t; V_t+ell)
```

Interpretation:

- Positive `S_macro`: the macro state has predictive structure beyond individual agents.
- Near zero: the macro state is not more informative than its parts.
- Negative: the individual agents contain redundant information, so the summed individual terms outweigh the macro self-predictability.

This is a coarse, order-agnostic screen for multi-agent emergence.

## 10. Coalition Test

The coalition test examines triplets:

```text
I_3 = I((X_i,t, X_j,t, X_k,t); V_t+ell)
```

Then it asks whether the full triplet adds information beyond the best pair:

```text
G_3 = I_3 - max(I_2{1,2}, I_2{1,3}, I_2{2,3})
```

Interpretation:

- High `I_3`: the triplet jointly predicts future macro behavior.
- Positive `G_3`: the triplet has beyond-pair structure.
- Near-zero `G_3`: pairwise alignment explains most of the useful information.

## 11. Null Distributions and Shuffling Examples

The paper uses surrogate null distributions to test whether observed structure is stronger than expected under controlled disruptions.

### Row-wise / horizontal shuffle

Think of rows as rounds and columns as agents:

```text
          Agent A   Agent B   Agent C
Round 1     +8       -7        -1
Round 2     +6       -5        -1
Round 3     +3       -2        -1
```

A row-wise shuffle permutes agent values within each round:

```text
          Agent A   Agent B   Agent C
Round 1     -1       +8        -7
Round 2     -5       -1        +6
Round 3     +3       -1        -2
```

This preserves the round-level distribution but breaks stable agent identity. If observed synergy disappears under this null, the original structure depended on persistent roles.

### Column-wise / vertical block shuffle

A column-wise or block time shuffle disrupts time alignment while preserving local structure:

```text
Original blocks:
[Round 1, Round 2] [Round 3, Round 4] [Round 5, Round 6]

Block-shuffled:
[Round 5, Round 6] [Round 1, Round 2] [Round 3, Round 4]
```

The paper uses block size `ell = 2` in robustness checks. This preserves short-range autocorrelation but breaks longer-range temporal coupling.

## 12. Bias-Corrected Estimates

For a metric such as synergy, the paper compares the observed value against a null distribution:

```text
Observed synergy = 0.30
Null median = 0.10

BC = observed - median(null)
   = 0.30 - 0.10
   = 0.20
```

If `BC > 0`, the observed effect is stronger than the null baseline. The paper then uses Wilcoxon signed-rank tests to evaluate whether bias-corrected values are consistently above zero across groups.

## 13. Time-Demeaning and Functional Baseline

The paper worries that apparent synergy may come from shared time trends or autocorrelation.

Example trend:

```text
Agent A: 20, 15, 10, 5, 0
Agent B: 18, 13, 8, 3, -2
```

These agents look related, but both may simply be following the same group feedback.

The paper uses:

```text
dev_i,t = alpha_i + beta_i * time + residual_i,t
```

and analyzes the residuals to remove linear time trends.

It also uses a functional baseline: a naive deterministic binary-search agent without between-agent synergy. This baseline can oscillate between too high and too low. If observed synergy exceeds this baseline, it is less likely to be explained by ordinary feedback-following behavior.

## 14. Agent Differentiation: Mixed Models

The paper tests whether agents develop stable, person-specific behavior patterns using hierarchical mixed models:

```text
m0: y_i = beta_0 + u_time[i] + epsilon_i
m1: y_i = beta_0 + u_time[i] + u_agent[i] + epsilon_i
m2: y_i = beta_0 + u_time[i] + u_agent[i],0 + u_agent[i],time[i] + epsilon_i
```

where:

```text
y_i = dev_i,t
```

Interpretation:

- `m0`: only shared round-to-round effects.
- `m1`: adds stable agent-level differences in contribution level.
- `m2`: adds agent-specific slopes, meaning agents can change at different rates.

Comparisons:

- `m0 -> m1`: asks whether agents differ in average contribution.
- `m1 -> m2`: asks whether agents differ in learning/adaptation rate.

## 15. Numerical Log-Likelihood Example

Suppose observed deviations are:

```text
             Round 1   Round 2   Round 3
Agent A        +4        +5        +6
Agent B        -4        -5        -6
```

### Simple model `m0`

Assume `m0` predicts zero for all observations:

```text
SSE_m0 = 4^2 + 5^2 + 6^2 + (-4)^2 + (-5)^2 + (-6)^2
       = 154

sigma^2_m0 = SSE / n
           = 154 / 6
           = 25.67
```

For a Gaussian model:

```text
log L = -n/2 [log(2*pi) + 1 + log(SSE/n)]
```

So:

```text
log L_m0 = -6/2 [1.838 + 1 + log(25.67)]
         = -3 [1.838 + 1 + 3.245]
         = -18.25
```

### More complex model `m1`

Let `m1` estimate agent-level intercepts:

```text
Agent A mean = 5
Agent B mean = -5
```

Residuals:

```text
Agent A: -1, 0, +1
Agent B: +1, 0, -1
```

Therefore:

```text
SSE_m1 = 4
sigma^2_m1 = 4 / 6 = 0.67

log L_m1 = -6/2 [1.838 + 1 + log(0.67)]
         = -3 [1.838 + 1 - 0.405]
         = -7.30
```

Likelihood-ratio statistic:

```text
D = 2 [log L_m1 - log L_m0]
  = 2 [-7.30 - (-18.25)]
  = 21.90
```

Using a chi-square reference distribution with one extra parameter:

```text
p = P(chi-square_1 >= 21.90)
```

This p-value is below 0.001. The interpretation is that adding agent-level identity effects greatly improves model fit.

## 16. Main Findings We Discussed

Key findings and interpretations:

- Multi-agent LLM systems can show emergence capacity, meaning their future behavior can contain information available only from combinations of agents.
- Plain prompting may produce temporal coupling, but it can be unstable or incidental.
- Persona prompts introduce stable identity-linked differentiation.
- Persona + ToM prompts produce the clearest goal-directed alignment and stable collective behavior.
- Coordination can emerge without direct communication because agents share group-level feedback and can model how others may respond.
- Good performance depends on both synergy and redundancy: complementarity without alignment is unstable, while alignment without complementarity can produce redundant oscillation.
- Robustness tests are essential because time trends, autocorrelation, empty bins, and heterogeneous learning rates can all create false evidence of synergy.

## 17. Relevance to Multi-Agent AI Safety and AI Forge

This paper is useful because it turns vague concepts into measurable diagnostics:

| Safety concept | Paper contribution |
|---|---|
| Emergent collective capability | Measured through PID, TDMI, macro predictability, and coalition tests |
| Hidden coordination | Detectable even when agents do not directly communicate |
| Role specialization | Tested through mixed models and identity-sensitive nulls |
| Phase-like transitions | Prompt interventions shift group dynamics from unstable to stable regimes |
| Robust evaluation | Surrogate nulls and bias-corrected estimates distinguish real structure from artifacts |
| Oversight | Metrics provide warning signals when a multi-agent system becomes more integrated |

For AI Forge-style evaluation, the main lesson is that final task performance is not enough. We also need diagnostics that reveal how agent populations coordinate internally, whether their coordination is goal-aligned, and whether measured synergy survives conservative null baselines.
