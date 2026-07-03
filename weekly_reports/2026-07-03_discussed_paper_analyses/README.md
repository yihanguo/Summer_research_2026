# Discussed Paper Analyses - July 3, 2026

This folder collects analytical notes for the papers explicitly discussed in the thread leading up to July 3, 2026. The goal is to preserve the reasoning-oriented explanations: experimental design, methods, metrics, interpretation, limitations, and how each paper relates to multi-agent safety, oversight, cooperation, or model editing.

## Included Papers

| File | Paper |
|---|---|
| `01_dataless_weight_disentanglement_task_arithmetic.md` | *Dataless Weight Disentanglement in Task Arithmetic via Kronecker-Factored Approximation* |
| `02_locating_editing_factual_associations_gpt.md` | *Locating and Editing Factual Associations in GPT* |
| `03_emergent_coordination_multi_agent_language_models.md` | *Emergent Coordination in Multi-Agent Language Models* |
| `04_coopeval_social_dilemmas.md` | *CoopEval: Benchmarking Cooperation-Sustaining Mechanisms and LLM Agents in Social Dilemmas* |
| `05_shapley_coop_credit_assignment.md` | *Shapley-Coop Credit Assignment* |
| `06_oversight_game_learning_control.md` | *The Oversight Game: Learning to Cooperatively Control AI* |

## Cross-Paper Themes

- **Cooperation under incentive conflict:** CoopEval, Shapley-Coop, and The Oversight Game all ask how rational or self-interested agents can be induced to cooperate without assuming moral benevolence.
- **Emergent collective structure:** Riedl's paper focuses on whether collective behavior contains information that is not reducible to individual agents alone.
- **Oversight and control as games:** The Oversight Game models human-AI control as a two-player Markov game, while CoopEval and Shapley-Coop use game-theoretic mechanisms to reshape incentives.
- **Mechanistic locality:** The ROME and TAK/KFAC papers both use structure in model weights or curvature to make interventions more targeted.
- **Evaluation beyond raw task success:** The papers repeatedly separate "solves the task" from more diagnostic criteria: fair credit, contribution-sensitive reward, safe minimum oversight, specificity, robustness, localization, and null-distribution tests.

