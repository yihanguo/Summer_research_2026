# CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas

Paper: *CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas*  
Venue: ICML 2026  
Sources: OpenReview, arXiv 2604.15267

## Core Question

The paper asks:

```text
Can game-theoretic mechanisms make self-interested LLM agents cooperate?
```

The important phrase we discussed was **morality-agnostic**. The paper does not rely on telling agents to be kind, altruistic, or moral. Instead, agents are instructed to maximize their own points, and the experiment tests whether cooperation can be sustained by mechanism design.

## Cooperation Definition

Cooperation is defined by payoff structure:

```text
a cooperative action costs the individual but increases collective welfare
```

Examples:

- In Prisoner's Dilemma, cooperation sacrifices the temptation payoff.
- In Public Goods, contribution benefits the group but invites free-riding.
- In Trust Game, one player must trust and the other must reciprocate.
- In Traveler's Dilemma, agents must avoid strategic undercutting.

## Experimental Design

The benchmark uses a factorized design:

```text
{mechanisms} x {games} x {LLM models}
```

This is possible because LLMs can parse different natural-language games and mechanisms without a new hand-coded policy for each setting.

The design matters because it compares:

- the same model under different mechanisms,
- the same mechanism across different games,
- homogeneous and heterogeneous LLM societies.

## Mechanisms

The main mechanisms are:

| Mechanism | Cooperation logic |
|---|---|
| No mechanism | Baseline single-shot dilemma |
| Repetition | Direct reciprocity with the same partner |
| Reputation | Indirect reciprocity through visible history |
| Mediation | Third-party mediator coordinates conditional cooperation |
| Contract | Action-contingent payments or penalties reshape incentives |

The clarification we discussed for **reputation**:

```text
agents know what other agents did in the past,
and they also know their own current action can affect future reputation.
```

This future visibility is what gives reputation strategic force.

## Metrics

The paper evaluates cooperation using:

- mean payoff,
- action frequencies,
- fitness under replicator dynamics,
- Deviation Rating for general-sum games,
- reasoning-justification analysis.

Aggregated payoffs are rescaled so that:

```text
0 = everyone defects
1 = everyone chooses the most cooperative action
```

This makes different games more comparable.

## Key Findings

- Without mechanisms, LLMs often defect when told to maximize payoff.
- Contract and Mediation are generally strong mechanisms.
- Repetition can support cooperation but is sensitive to implementation details.
- Reputation is less reliable than expected; richer reputation histories can overload or confuse LLM agents.
- Evolutionary population dynamics can make cooperative mechanisms appear stronger because successful agents become more common.

## Why The Paper Matters

CoopEval is important for multi-agent AI safety because it separates:

```text
prosocial language
from
incentive-compatible cooperation
```

In future AI societies, agents may be owned by different users or providers. A mechanism that works only when agents are morally prompted is fragile. CoopEval asks whether cooperation can be induced by the strategic structure itself.

## Limitations And Future Work

The paper suggests extending the benchmark to:

- sequential social dilemmas,
- open-source game playing,
- pre-play communication,
- gifting,
- purpose-built LLM agents with scaffolds or fine-tuning.

The current work is best viewed as a benchmark foundation, not a final answer about robust AI cooperation.

