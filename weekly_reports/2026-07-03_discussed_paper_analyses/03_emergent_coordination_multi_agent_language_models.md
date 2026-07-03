# Emergent Coordination in Multi-Agent Language Models

Paper: *Emergent Coordination in Multi-Agent Language Models*  
Author: Christoph Riedl  
Venue: ICLR 2026  
Existing notes: `../2026-06-26_multi_agent_safety_top_conference_papers/DEEP_DIVE_RIEDL_2026_EMERGENT_COORDINATION.md`

## Core Question

The paper asks when a group of LLM agents is merely a set of independent predictors and when it becomes a coordinated collective system.

The key distinction is:

```text
good average performance is not enough
```

The paper wants evidence that the joint system contains higher-order structure: information about future group behavior that cannot be recovered from individual agents alone.

## Experimental Setting

The task is a group guessing game, also described as group binary search.

- Each agent proposes an integer.
- The group sum is compared to a hidden target.
- Agents do not directly communicate.
- Agents do not see each other's guesses.
- Agents receive only group-level feedback: too high or too low.

This is deliberately minimal. If all agents follow the same strategy, the group can oscillate. Success requires complementary roles, such as one agent consistently moving above equal share while another moves below.

## Interventions

The paper compares prompt conditions:

- **Plain:** basic instructions only.
- **Persona:** agents receive distinct personas.
- **Theory-of-Mind style prompt:** agents are instructed to reason about what other agents might do and how their own choices affect the group.

The ToM label is operational, not a claim that the agents have human-like theory of mind.

## Synergy And PID

For agents `i` and `j`, the paper decomposes predictive information:

```text
I({X_i,t, X_j,t}; T_ij,t+ell)
  = UI_i + UI_j + Red_ij + Syn_ij
```

where:

- `UI_i` is information unique to agent `i`,
- `UI_j` is information unique to agent `j`,
- `Red_ij` is redundant information both provide,
- `Syn_ij` is information only available from the pair jointly.

Positive synergy means:

```text
the pair predicts the future better than either agent alone
```

This is the paper's main formal handle on emergence.

## TDMI

The paper also uses time-delayed mutual information:

```text
I(X_t; X_t+ell)
```

This asks whether current states predict future states at lag `ell`. It is useful because emergence is framed as information about temporal evolution, not just a static snapshot.

## Null Tests

The row-shuffle and column-shuffle tests are designed to distinguish real coordination from alternative explanations.

**Row shuffle:** breaks identity-locked structure. It asks whether apparent roles depend on stable agent identity.

**Column shuffle:** breaks dynamic alignment across time. It asks whether apparent synergy depends on the temporal arrangement of agents' actions.

These nulls help separate:

```text
real task-aligned synergy
from
spurious correlation, heterogeneous learning rates, or static persona differences
```

## Agent Differentiation Test

The paper also uses hierarchical mixed models:

```text
m0: time effects only
m1: time effects + agent random intercepts
m2: time effects + agent random intercepts + agent-by-time slopes
```

Likelihood-ratio tests compare whether adding agent identity or learning-rate-like variation significantly improves model fit.

This is a complementary non-information-theoretic diagnostic. It asks whether agents develop stable, identity-linked patterns rather than simply following the same group feedback.

## Key Interpretation

The paper is useful because it gives a vocabulary for collective LLM behavior:

- redundancy: agents are aligned but duplicate information,
- synergy: the group contains information not present in any individual,
- differentiation: agents develop stable complementary roles,
- dynamic alignment: coordination appears in the time evolution of the system.

## Caveats

- The task is artificial and intentionally minimal.
- Pairwise PID detects synergy of order two but may miss higher-order structure.
- Discretization choices, entropy estimation, and autocorrelation can affect information estimates.
- The paper is best read as a diagnostic framework for emergence, not a complete theory of multi-agent capability.

