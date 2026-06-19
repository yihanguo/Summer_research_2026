# 01. Sandboxes and Testbeds

## Why this category matters

Multi-agent safety claims are difficult to validate because the relevant failures depend on interaction histories, incentives, network structure, and feedback from other agents. A useful testbed must make those variables controllable without stripping away the long horizons and social dynamics that create the risk. The four cited works span a useful ladder: matrix games, a persistent simulated society, repeated human/LLM games, and a real app-publication task.

## Paper matrix

| Subcategory | Work | Environment or benchmark | Evidence and main result | Safety use |
|---|---|---|---|---|
| Stylized games and simulated societies | Gandhi et al. (2023) | Systematically varied matrix games plus language-based negotiation scenarios | Few-shot, structured reasoning prompts generalize to changed payoffs, objectives, hidden information, and game structures; the paper reports near-perfect generalization in its matrix-game variants. | Controlled stress tests for strategic adaptation, belief reasoning, cooperation, and deception. |
| Stylized games and simulated societies | Park et al. (2023) | Smallville, a persistent sandbox with 25 generative agents | Memory, reflection, and planning produce coordinated social behavior; ablations and human evaluations identify each architecture component's contribution to believability. | Tests long-horizon propagation of information, norm formation, planning failures, and emergent coordination. |
| Stylized games and simulated societies | Akata et al. (2025) | Finitely repeated 2 x 2 games against LLMs, hand-coded human-like strategies, and human players | LLMs do well in self-interested repeated games but are weaker in coordination games such as Battle of the Sexes; opponent information and social chain-of-thought improve GPT-4 coordination. | Measures cooperation profiles and sensitivity to social prompting under controlled incentives. |
| High-fidelity frontier-agent environments | Kapoor et al. (2026) | CRUX open-world evaluation: develop and publish a simple iOS app | The agent completed the end-to-end task with one avoidable manual intervention. The study argues for small-sample qualitative evaluation alongside scalable benchmarks. | Reveals deployment bottlenecks, autonomy, and failures hidden by short, automatically graded tasks. |

## Subcategories

### Stylized games and simulated societies

**Gandhi, Sadigh, and Goodman - Strategic Reasoning with Language Models.** The paper uses generated reasoning demonstrations over states, values, and beliefs rather than game-specific training. Its central contribution is transfer: strategic behavior learned through prompting is tested under modifications to rules, payoffs, objectives, and information. For safety research, the same generator can create controlled counterfactuals around an unfavorable action and estimate how its frequency changes with incentives or information access. [Source](https://openreview.net/forum?id=MUtbsFRZwI)

**Park et al. - Generative Agents.** Twenty-five agents inhabit a Sims-like town, store experiences in natural-language memory, reflect them into higher-level summaries, and retrieve them to make plans. The Valentine's Day party case shows information spreading and plans being coordinated without a central script. This is a strong template for studying slow, path-dependent failures, though its human-believability evaluation is not itself a calibrated safety metric. [Source](https://dl.acm.org/doi/10.1145/3586183.3606763)

**Akata et al. - Playing Repeated Games with Large Language Models.** The repeated-game battery separates self-interest, coordination, and social adaptation while keeping the payoff structure explicit. Because every action has a numerical payoff, it can support per-round risk labels such as `unfavorable_action = action that lowers joint payoff below the Pareto-efficient outcome`. The paper studies behavioral signatures, not a general per-step probability forecaster, but it supplies a clean calibration environment for one. [Source](https://www.nature.com/articles/s41562-025-02172-y)

### High-fidelity frontier-agent environments

**Kapoor et al. - Open-World Evaluations / CRUX.** CRUX treats the whole deployment workflow as the evaluation object. Its first case includes coding, debugging, account and tool interaction, and App Store publication, with qualitative tracing of where a human had to intervene. The design improves external validity but has a small sample and expensive human assessment, so repeated runs and structured event logs are necessary for probabilistic claims. [Source](https://cruxevals.com/)

### Scalability, fidelity, and external validity

The call cites no paper devoted solely to a formal fidelity or external-validity measure. Together, the papers expose the main tradeoff: matrix games enable thousands of controlled trials but omit institutional detail, while CRUX preserves real-world friction but offers few trials. A robust programme should use both and report whether intervention policies transfer from the stylized environment to the open-world one.

### Reproducibility, interoperability, and logging

Park et al.'s event-rich sandbox and CRUX's trajectory reporting show why complete logs matter, but the cited set does not establish a common MAS trace schema. A reusable testbed should log agent identity, observation, message, action, tool result, environment state, model/version, random seed, risk score, intervention, and counterfactual outcome at each step.

## Design implications

1. Use games for repeated calibration and causal intervention; use persistent societies for network effects; use open-world tasks for external validity.
2. Separate task success from system safety. A high reward can coexist with collusion, unsafe tool use, or unfair allocation.
3. Pre-register the unfavorable-action label and threshold before observing outcomes.
4. Preserve raw trajectories so a step-level score can be evaluated for AUROC, calibration error, time-to-warning, false interventions, and downstream task utility.
