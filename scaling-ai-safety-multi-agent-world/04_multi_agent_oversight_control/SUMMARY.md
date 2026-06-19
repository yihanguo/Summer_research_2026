# 04. Multi-Agent Oversight and Control

## Why this category matters

Oversight turns observations about multi-agent risk into operational decisions: detect suspicious coordination, identify the responsible agent and step, and intervene without destroying task utility. These papers cover black-box behavioral statistics, white-box activation probes, causal attribution, threshold-based AI control, and architectural isolation.

## Paper matrix

| Subcategory | Work | Error or threat context | Benchmark or evaluation | Main result |
|---|---|---|---|---|
| Collusion and covert-communication detection | Bonjour et al. (2022) | Agents covertly coordinate actions against other players | Iterated Rock-Paper-Scissors and partially observable poker | Mutual information between agents' actions detects varying collusion strengths without a domain-specific collusion script. |
| Collusion and covert-communication detection | Rose et al. (2026) | Group-level collusion hidden from text monitoring | NARCBENCH across four open-weight models, six probe architectures, shifted scenarios, and steganographic blackjack | 1.00 in-distribution AUROC; 0.73-0.93 zero-shot AUROC on shifted scenarios for Llama-3.1-70B; 0.99-1.00 on steganographic blackjack. |
| Failure attribution and oversight interfaces | Zhang et al. (2025) | A collaborative MAS fails and developers need the responsible agent and decisive step | Who&When: logs from 127 LLM multi-agent systems | Best method reaches 53.5% responsible-agent accuracy but only 14.2% decisive-step accuracy. |
| Multi-agent control and scalable oversight | Greenblatt et al. (2025) | An untrusted model may intentionally insert backdoors or subvert monitoring | Programming tasks with GPT-4 as untrusted model, GPT-3.5 as trusted model, and limited trusted labor | Trusted editing and untrusted monitoring improve the safety/usefulness tradeoff over simple baselines; suspiciousness thresholds determine escalation. |
| Multi-agent control and scalable oversight | Shah et al. (2025) | Catastrophic misuse, misalignment, mistakes, and structural risk | Safety-case framework synthesizing capability evaluations, monitoring, access control, robust training, and amplified oversight | Argues for layered model- and system-level defenses rather than a single benchmark or mitigation. |
| Multi-agent control and scalable oversight | Foerster et al. (2026) | Prompt injection and branch steering in computer-use agents | OSWorld | NOVA's precommitted branching plans retain up to 57% of frontier-model performance and improve smaller open models by up to 19%, while isolating untrusted observations from trusted planning. |
| Mechanism and information design | Riedl (2026) | Distinguishing a mere collection from performance-relevant higher-order coordination | A guessing game with no direct communication and three randomized prompt interventions | Time-delayed mutual information plus partial information decomposition separates temporal synergy, identity differentiation, and goal-directed complementarity. |

## Subcategories

### Collusion and covert-communication detection

**Bonjour, Aggarwal, and Bhargava - Information-Theoretic Approach to Detect Collusion.** The detector computes mutual information between players' actions: dependence beyond what ordinary play predicts becomes evidence of coordination. This is attractive because the score is continuous and domain-independent, but a high score is evidence of statistical dependence, not automatically malicious intent. Threshold selection therefore needs clean-play calibration and environment-specific false-positive analysis. [Source](https://openreview.net/forum?id=HCl41wIi9gc)

**Rose et al. - Detecting Multi-Agent Collusion Through Multi-Agent Interpretability.** NARCBENCH treats collusion as distributed anomaly detection. The authors train per-agent activation probes and combine their deception scores using five group aggregation rules; different rules match different signatures, such as one anomalous agent versus weak evidence distributed over a coalition. This is the closest item here to estimating a group-level probability-like risk signal before intervention, although its reported discrimination scores are not by themselves calibrated probabilities. [Source](https://arxiv.org/abs/2604.01151)

### Failure attribution and oversight interfaces

**Zhang et al. - Which Agent Causes Task Failures and When?** Who&When provides agent and step annotations over failure traces from 127 MAS configurations. The large gap between agent accuracy (53.5%) and step accuracy (14.2%) is a direct warning for intervention research: raising a system-level concern is much easier than locating the earliest actionable step. A threshold policy should therefore be evaluated for localization delay and whether it intervenes before the decisive error, not only for trajectory-level classification. [Source](https://openreview.net/forum?id=GazlTYxZss)

### Multi-agent control and scalable oversight

**Greenblatt et al. - AI Control.** A strong untrusted model writes candidate code while trusted or independently prompted monitors assign suspiciousness. In trusted editing, low-suspicion code is submitted and high-suspicion code is edited by the trusted model; in untrusted monitoring, another strong model inspects the output under anti-collusion measures. This is an exact example of score-threshold-action control, but the score comes from monitor judgment and the intervention is edit/audit rather than RL self-improvement. [Source](https://arxiv.org/abs/2312.06942)

**Shah et al. - An Approach to Technical AGI Safety and Security.** The paper organizes risk into misuse, misalignment, mistakes, and structural risks, then connects evaluations to access restrictions, monitoring, model safeguards, and safety cases. Its value for MAS research is architectural: a probabilistic warning should be one piece of a defense-in-depth argument with explicit assumptions and residual risks. It is an agenda and synthesis, not a new MAS benchmark. [Source](https://arxiv.org/abs/2504.01849)

**Foerster et al. - CaMeLs Can Use Computers Too.** NOVA separates a trusted planner from untrusted runtime observations. The planner emits an upfront branching program, and perception modules fill runtime values without gaining authority to rewrite control flow. This prevents direct instruction injection but reveals branch steering as a residual multi-component attack, showing why control guarantees must cover the interactions between planning, perception, and action modules. [Source](https://arxiv.org/abs/2601.09923)

### Mechanism and information design

**Riedl - Emergent Coordination in Multi-Agent Language Models.** The framework decomposes time-delayed mutual information to ask whether cross-agent information provides synergistic predictive power beyond individual histories. Persona prompts create stable differentiation, and adding an instruction to reason about other agents creates goal-directed complementarity. The metric can serve as an early-warning feature for coordination, but the experiment demonstrates benign task coordination; harmfulness requires a separate goal or outcome label. [Source](https://openreview.net/forum?id=SRn1MtMPRq)

## Implications for thresholded intervention

A defensible warning-and-intervention loop can combine these contributions:

1. Compute behavioral dependence (Bonjour) and/or aggregate internal probe scores (Rose).
2. Localize the likely responsible agent and step (Zhang), preserving uncertainty when localization is weak.
3. Compare a calibrated risk estimate with an intervention threshold (Greenblatt).
4. Restrict, edit, resample, retrain, or route to human review while preserving architectural control boundaries (Foerster; Shah).
5. Evaluate both safety and utility under distribution shift, covert channels, monitor collusion, and repeated adaptation.

None of the cited papers closes this loop with a general RL-based self-revision algorithm. That combination remains a research opportunity rather than an established result.
