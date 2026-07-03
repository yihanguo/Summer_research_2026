# Shapley-Coop Credit Assignment

Paper: *Shapley-Coop Credit Assignment*  
Source: local PDFs `17116_Shapley_Coop_Credit_Assi.pdf` and `17116_Shapley_Coop_Credit_Assi copy.pdf`

## Core Question

The paper asks:

```text
How can self-interested LLM agents cooperate when one agent's helpful action benefits another agent more than itself?
```

This is a credit-assignment and incentive-alignment problem. Cooperation may be collectively good but individually unattractive unless the reward is redistributed fairly.

## Escape Room Scenario

The paper's cleanest example is an Escape Room game:

```text
one agent pulls a lever and receives -1
the other opens the door and receives +10
if both choose the same action, both receive -1
```

The successful group outcome has total payoff:

```text
10 - 1 = 9
```

But the raw payoff is unfair. The lever-puller takes a local loss while the door-opener receives the large reward.

## Shapley Solution

Because both agents are necessary for the successful escape, Shapley value assigns:

```text
Agent 1: 4.5
Agent 2: 4.5
```

If Agent 2 receives `+10` and Agent 1 receives `-1`, then Agent 2 should transfer:

```text
10 - 4.5 = 5.5
```

After transfer:

```text
Agent 1: -1 + 5.5 = 4.5
Agent 2: 10 - 5.5 = 4.5
```

This is the paper's main intuition:

```text
cooperation becomes rational when final reward tracks contribution
```

## Methods Compared

The paper compares:

| Method | Meaning |
|---|---|
| LLM-only | No negotiation or cooperation mechanism |
| LLM+NEG | Negotiation but no Shapley reasoning |
| LLM+STS | Short-term Shapley-style reasoning only |
| LLM+SC | Full Shapley-Coop workflow |

`LLM+NEG` can produce deals, but the payment may be arbitrary.  
`LLM+STS` helps agents reason about externalities before acting.  
`LLM+SC` adds post-task Shapley-style credit assignment.

## Communication And Rounds

Agents are allowed to communicate in the negotiation settings. The public code indicates a fixed maximum number of negotiation rounds, with a halt option after agreement. In the Escape Room, the game itself is one-shot, but there can be multiple negotiation rounds before the final action.

This distinction matters:

```text
multi-round communication
is not the same as
repeated play with remembered credit from prior episodes
```

The Raid Battle environment is genuinely multi-turn, while Escape Room is a one-shot social dilemma with pre-action negotiation.

## Evaluation

The paper evaluates both:

```text
task success
and
fair reward allocation
```

For Escape Room:

- LLM-only: 0% success,
- LLM+NEG: 25% success,
- LLM+STS: 100% success,
- LLM+SC: 100% success.

But `LLM+SC` is stronger because it also reduces payoff difference from the Shapley-fair target. The paper reports lower payoff difference for LLM+SC than LLM+STS.

For Raid Battle, the paper evaluates:

- boss defeat,
- survival,
- turns,
- damage,
- healing,
- taunt usage,
- reward-allocation accuracy.

For ChatDEV, it uses Weighted Earned Value based on code, decisions, documents, and bug fixes.

## Statistical Rigor

The paper has useful ablations and multiple environments:

- Escape Room,
- Raid Battle,
- ChatDEV,
- negotiation-round sensitivity,
- comparisons against negotiation-only and short-term-only variants.

However, the statistical reporting is not as deep as the conceptual design. The paper reports quantitative comparisons and error bars, but the main text does not always make sample sizes, variance sources, and error-bar formulas fully transparent.

## Interpretation

The strongest contribution is the distinction between:

```text
can agents cooperate?
```

and:

```text
is cooperation incentive-compatible for the agent who bears the cost?
```

Shapley-Coop tries to solve the second problem by making compensation contribution-sensitive.

## Limitations

- The illustrative Escape Room task is simple.
- Shapley calculation becomes harder in large, open-ended agent systems.
- Negotiated reward transfers may not be enforceable without an external mechanism.
- LLM negotiation can produce plausible but inaccurate contribution claims.

