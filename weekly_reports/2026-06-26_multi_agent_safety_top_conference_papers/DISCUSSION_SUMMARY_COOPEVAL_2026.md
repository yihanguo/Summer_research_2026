# Discussion Summary: CoopEval

Paper: *CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas*  
Venue: ICML 2026  
Links: [OpenReview](https://openreview.net/forum?id=369qOr0ZnJ), [arXiv](https://arxiv.org/abs/2604.15267)

## 1. Core Question

The paper asks:

> Can game-theoretic mechanisms make self-interested LLM agents cooperate in social dilemmas?

The authors are not mainly asking whether LLMs are "nice" or morally prosocial. They deliberately instruct agents to maximize their own points, then test whether mechanisms such as repetition, reputation, mediation, and contracts can make cooperative outcomes strategically attractive.

This is why the paper describes its approach as **morality-agnostic**: cooperation should not depend on ethical prompting, altruistic preferences, or moral self-presentation. It should arise because the mechanism changes incentives.

## 2. Experimental Setting

The benchmark follows a factorized design:

```text
{mechanisms} x {games} x {LLM models}
```

The agents are prompted with natural-language descriptions of a game and are told to maximize their own total points. This design leverages the generality of LLM agents: the same model can parse a Prisoner's Dilemma, a Trust Game, a Public Goods Game, or a contract mechanism from text, without training a new policy for each environment.

The authors evaluate heterogeneous LLM societies rather than only same-model self-play. They test cross-play matchups between different LLM models, because real multi-agent AI settings may include agents from different providers with different capabilities and strategies.

## 3. Social Dilemmas Tested

The paper studies four main social dilemmas:

| Game | Cooperation problem |
|---|---|
| Prisoner's Dilemma | Mutual cooperation is collectively better, but individual defection is tempting or dominant |
| Traveler's Dilemma | High claims are collectively better, but each player has an incentive to undercut |
| Public Goods Game | Contributing helps the group, but each individual can free-ride |
| Trust Game | One player must trust, and the other must reciprocate rather than exploit |

They also include a coordination-cooperation baseline, such as Stag Hunt, to distinguish social dilemmas from ordinary coordination problems.

## 4. How the Paper Defines Cooperation

The paper defines cooperation in game-theoretic terms:

> A cooperative action is costly to the individual player but increases collective welfare.

So cooperation is not defined as "being kind." It is defined by the payoff structure.

Examples:

- In Prisoner's Dilemma, cooperation means choosing `C` even though defection may be individually tempting.
- In Public Goods, cooperation means contributing to the shared pool rather than free-riding.
- In Traveler's Dilemma, cooperation means avoiding the race to the lowest claim and supporting the higher mutually beneficial outcome.
- In the Trust Game, cooperation means trust and reciprocation rather than exploitation.

The stronger mechanism-level goal is:

> A mechanism supports cooperation if it can make a Pareto-improving outcome achievable in equilibrium.

In simpler words, the mechanism should let rational self-interested agents reach an outcome where everyone is better off than in the non-cooperative equilibrium.

## 5. Mechanisms Tested

The paper compares several cooperation-sustaining mechanisms.

### No Mechanism

The base social dilemma is left unchanged. This is the baseline.

Purpose:

```text
How often do LLM agents cooperate without any incentive-changing structure?
```

The paper finds that modern LLMs often defect in single-shot social dilemmas when simply told to maximize their own payoffs.

### Repetition

The same players interact repeatedly and remember each other's past actions.

Cooperation logic:

```text
If I defect now, my same partner can punish me later.
```

This supports **direct reciprocity**.

### Reputation

Players interact repeatedly but with varying co-players. Agents can see histories of past behavior.

Cooperation logic:

```text
If I defect now, future partners may see that and refuse to cooperate with me.
```

This supports **indirect reciprocity**.

Important clarification from our discussion:

- Agents do not see each other's current action before choosing.
- They act simultaneously.
- They do see some past action history about current co-players.
- They are also aware that their own current action will become visible to future co-players.

So Reputation is not merely:

```text
I know what others did.
```

It is also:

```text
Others will know what I did.
```

That future visibility is what gives reputation its incentive power.

The paper distinguishes reputation variants:

- **Reputation-**: more limited or first-order history.
- **Reputation+**: richer higher-order history, including histories of co-players' past co-players.

Interestingly, richer history does not necessarily improve cooperation, possibly because it overloads or confuses LLM agents.

### Mediation

Players may delegate their decision to a trusted third-party mediator. The mediator chooses actions based on how many players delegated.

Cooperation logic:

```text
If enough players delegate, the mediator can coordinate them on a cooperative action.
```

The authors ask LLM agents to propose mediators, vote on mediator proposals, and then decide whether to delegate.

### Contract

Players can agree to a contract that adds action-conditional payments or penalties.

Cooperation logic:

```text
If defection triggers compensation or penalties, cooperation can become the payoff-maximizing move.
```

The authors ask LLM agents to propose contracts, vote on contract proposals, decide whether to sign, and then play under the selected contract if accepted.

## 6. Why the Experiments Are Designed This Way

The design is motivated by three needs.

### Same Agent Across Different Mechanisms

Rule-based or RL agents are often purpose-built for one mechanism. If the environment changes from Repetition to Reputation to Contract, it can be hard to say what "the same agent" means.

LLMs can read arbitrary natural-language descriptions, so the authors can keep the model fixed and vary the game or mechanism.

This supports a clean comparison:

```text
Same LLM model, different mechanism.
```

### Mechanism x Game Comparison

Testing only one game would make the result too narrow. A mechanism may work in Prisoner's Dilemma but fail in Trust Game or Public Goods.

The factorized grid asks:

```text
Does this mechanism work across different social dilemmas?
Or only in one favorable setting?
```

### Heterogeneous LLM Societies

The authors test cross-play among multiple LLMs because realistic AI societies will likely be heterogeneous.

This asks:

```text
Does the mechanism still work when agents differ in capability, reasoning style, and strategic behavior?
```

## 7. Evaluation Metrics

The paper reports several performance views.

| Metric | Meaning |
|---|---|
| Mean payoff | Average payoff across cross-play matchups, assuming a uniform population of tested LLMs |
| Fitness | Payoff after running replicator dynamics, simulating a society where better-performing agents become more common |
| Deviation Rating (DR) | Ranking metric for general-sum games, analogous in spirit to an Elo-style ranking but designed for non-zero-sum settings |
| Action frequencies | How often agents choose cooperative or defective actions |
| Reasoning-justification analysis | Uses an LLM judge to classify why agents say they made decisions |

The paper rescales aggregated payoffs so that:

```text
0 = everyone defects
1 = everyone plays the most cooperative action
```

This makes cooperation levels comparable across games with different payoff scales.

## 8. Key Findings Discussed

Important takeaways:

- Without mechanisms, modern LLM agents often defect in social dilemmas.
- Contract and Mediation are among the most effective mechanisms.
- Repetition can support cooperation, but performance weakens when co-players vary or when the history interface is less helpful.
- Reputation is less effective than one might expect; richer higher-order reputation information may not help LLMs.
- Under evolutionary pressures, cooperation mechanisms can become more effective because agents that benefit under the mechanism survive in the simulated population.
- Many LLM decisions are justified using self-interested utility maximization and strategic equilibrium reasoning, not moral appeals.

This supports the paper's main claim: cooperation can be induced through incentive-compatible mechanisms, even when agents are selfish payoff maximizers.

## 9. Future Work Paragraph Explained

The paper says its framework opens several future directions.

### Sequential Social Dilemmas

The current benchmark mainly studies compact game-theoretic dilemmas modified by mechanisms. Future work could study richer multi-step environments.

Example:

```text
A group of AI agents manages a shared forest.
Each round, each agent decides how much to harvest.
Over-harvesting gives short-term gain but damages future resources.
```

This is more realistic because present actions change future states.

### Other Cooperation Mechanisms

The paper studies Repetition, Reputation, Mediation, and Contract, but many other mechanisms exist.

Examples from the paragraph:

- **Open-source game playing**: agents reveal their code or policy so others can condition behavior on it.
- **Pre-play**: agents communicate or coordinate before the actual game begins.
- **Gifting**: agents can transfer rewards or resources to influence future cooperation.

The open question is:

```text
Do these mechanisms sustain cooperation among LLM agents as well?
```

### Purposefully Built LLM Agents

The tested agents are mostly general-purpose LLMs prompted to play games. Future agents may be more strategic:

- fine-tuned agents,
- tool-using agents,
- memory-scaffolded agents,
- planning agents,
- RL-trained agents,
- agents optimized directly for payoff maximization.

The authors want to know whether their mechanisms remain robust when agents are deliberately built to exploit strategic environments.

## 10. Why This Matters for Multi-Agent AI Safety

The paper is relevant to AI safety because future AI systems may interact in markets, negotiations, platforms, procurement systems, and shared digital environments.

If agents are independently optimizing their own objectives, naive deployment may lead to:

- defection,
- free-riding,
- race-to-the-bottom behavior,
- exploitation of cooperative agents,
- collapse of collective welfare.

CoopEval suggests that safety work should not only ask:

```text
Are individual agents aligned?
```

It should also ask:

```text
Are the interaction protocols designed so that cooperation is rational?
```

The broader agenda is to understand **rational and robust cooperation** among AI agents: cooperation that survives strategic reasoning, heterogeneity, and optimization pressure.
