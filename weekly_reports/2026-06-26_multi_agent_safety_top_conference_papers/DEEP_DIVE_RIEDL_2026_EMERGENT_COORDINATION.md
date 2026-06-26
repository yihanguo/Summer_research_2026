# Deep Dive: Emergent Coordination in Multi-Agent Language Models

Paper: [Emergent Coordination in Multi-Agent Language Models](https://openreview.net/forum?id=SRn1MtMPRq)  
Author: Christoph Riedl  
Venue: ICLR 2026 Poster  
Local PDF: `scaling-ai-safety-multi-agent-world/04_multi_agent_oversight_control/papers/2026_Riedl_Emergent_Coordination.pdf`

## 1. Core Question

The paper asks a deceptively simple question:

> When is a multi-agent LLM system just several independent agents, and when does it become an integrated collective with higher-order structure?

This is important because many multi-agent LLM papers claim "greater-than-the-sum-of-its-parts" benefits, but often measure only final task accuracy. Riedl argues that accuracy alone cannot tell us whether agents actually coordinated, specialized, or produced synergistic information. A group could improve simply because it samples more answers, averages noise, or uses a better prompt. The paper therefore proposes an information-theoretic way to measure whether a multi-agent system has emergent coordination.

中文概括：这篇论文关注的是，多智能体 LLM 系统什么时候只是多个独立模型的集合，什么时候真正形成了具有高阶结构的“集体”。作者认为，仅看最终准确率不足以说明系统是否真的产生了协同、分工或涌现结构，因此提出用信息论方法来检测多智能体之间是否存在真正的协同信息。

## 2. Experimental Setup

The experiment uses a minimalist "group binary search" guessing game.

- Each agent proposes an integer from 0 to 50.
- The agents' guesses are summed.
- The group succeeds if the sum matches a hidden target number.
- Agents do not directly communicate with each other.
- Agents receive only group-level feedback: the group sum was "too high" or "too low."
- The task is hard because if all agents use the same binary-search strategy, they tend to move together and oscillate.
- Success requires differentiated, complementary behavior: some agents need to contribute higher guesses while others contribute lower guesses.

This task is deliberately simple. Its purpose is not to show that teams beat solo agents on a realistic benchmark. Its purpose is to isolate whether cross-agent complementarity can emerge under limited feedback.

中文说明：实验任务是一个群体猜数游戏。每个智能体给出 0 到 50 之间的整数，所有智能体的数字相加后与隐藏目标比较。系统只告诉每个智能体总和是太高还是太低。因为智能体不能看到彼此的猜测，如果大家都使用相同策略，就容易一起上下震荡。要成功，智能体必须形成互补的角色。

## 3. Prompt Interventions

The paper compares three conditions:

| Condition | What changes | Intended effect |
|---|---|---|
| Plain | Basic task prompt with binary-search instruction | Baseline group behavior |
| Persona | Each agent receives a distinct persona | Stable identity-linked differentiation |
| Persona + ToM | Persona plus instruction to think about what other agents might do | Mutual modeling and complementary adaptation |

The Theory-of-Mind (ToM) instruction is not a psychological claim that the agents truly understand minds. It is a prompt intervention that encourages agents to reason about other agents' likely actions and adapt their own guesses accordingly.

中文说明：论文比较普通提示、角色提示、以及角色加 Theory-of-Mind 提示。ToM 提示要求智能体思考其他智能体可能会怎么做，并调整自己的行为。这里的 ToM 不是说模型真的具有人类心智理论，而是一种促使模型进行互相建模的提示干预。

## 4. Key Measurement Idea

The paper measures emergence using information decomposition. The intuition is:

- **Redundancy**: agents provide overlapping information.
- **Unique information**: one agent contributes information not available from another.
- **Synergy**: information appears only when agents are considered jointly.

For multi-agent safety, synergy is the most interesting part. If the group jointly predicts future behavior or task outcomes in a way no individual agent can, then the system has higher-order structure.

中文说明：作者将群体信息分解为冗余信息、独有信息和协同信息。协同信息最关键，因为它表示只有把多个智能体放在一起观察时才出现的信息。如果群体整体能预测未来状态，而单个智能体无法做到，就说明系统中存在高阶结构。

## 5. Three Tests in the Paper

### 5.1 Emergence Capacity

This test asks whether two agents' current states jointly predict their future joint state in a way neither agent can alone.

For agents `i` and `j`, the paper defines the future target as:

```text
T_ij,t+l = (X_i,t+l, X_j,t+l)
```

Then it decomposes:

```text
I({X_i,t, X_j,t}; T_ij,t+l)
  = UI_i + UI_j + Red_ij + Syn_ij
```

`Syn_ij > 0` means the pair has predictive information about the future that is available only from the pair jointly.

### 5.2 Practical Emergence Criterion

This test asks whether the macro-level group signal predicts its own future better than the sum of individual agents does.

The macro signal is the group error:

```text
V_t = sum(agent guesses) - target
```

The practical criterion is:

```text
S_macro(l) = I(V_t; V_t+l) - sum_k I(X_k,t; V_t+l)
```

If this value is positive, the collective macro-state contains predictive structure beyond the individual microstates.

### 5.3 Coalition Test

This test asks whether a triplet of agents provides information about the future macro signal beyond the best pair.

```text
I_3 = I((X_i,t, X_j,t, X_k,t); V_t+l)
G_3 = I_3 - max(I_2{1,2}, I_2{1,3}, I_2{2,3})
```

`I_3` measures total triplet-level information about the future macro state. `G_3` measures whether the full triplet adds information beyond the strongest pair.

中文说明：论文有三个核心检测。第一个检测成对智能体是否存在动态协同。第二个检测群体宏观状态是否比个体状态更能预测未来。第三个检测三人小组是否比最强的二人组合提供更多信息。这些指标共同判断系统是否出现了高阶结构、这种结构在哪里，以及是否与任务目标有关。

### 5.4 Metric Cheat Sheet / 指标速查

The paper's metrics are built from the agents' guesses over time. The basic micro-level variable is each agent's **equal-share deviation**:

```text
dev_i,t = raw_guess_i,t - target / N
```

This removes the trivial target-size effect and asks whether agent `i` contributed above or below the equal-share amount needed for the group to hit the target. The macro-level group variable is:

```text
V_t = sum_i raw_guess_i,t - target
```

Equivalently, `V_t` is the sum of all agents' equal-share deviations. Positive `V_t` means the group guessed too high; negative `V_t` means the group guessed too low.

| Metric | Formula or construction | What it measures | Interpretation |
|---|---|---|---|
| **Emergence capacity / dynamical synergy** | `Syn_ij` from PID of `I({X_i,t, X_j,t}; T_ij,t+l)` | Whether a pair's future joint state is predictable only from the pair jointly, not from either agent alone | Positive `Syn_ij` means pairwise cross-agent synergy exists. The paper aggregates this over unordered agent pairs, usually by the median. |
| **Practical emergence criterion** | `S_macro(l) = I(V_t; V_t+l) - sum_k I(X_k,t; V_t+l)` | Whether the macro group state predicts its future better than the summed individual parts do | Positive values indicate macro-level predictive structure beyond individual agents. This is the closest metric to "the group has become more than its parts." |
| **Coalition information** | `I_3 = I((X_i,t, X_j,t, X_k,t); V_t+l)` | How much a triplet of agents jointly predicts the future group error | High `I_3` means a coalition carries strong information about the future macro outcome. |
| **Triadic information gain** | `G_3 = I_3 - max(I_2{1,2}, I_2{1,3}, I_2{2,3})` | Whether a full triplet adds information beyond the best pair | Positive `G_3` means the triplet has irreducible beyond-pair structure. Near-zero `G_3` means pairwise alignment explains most of the structure. |
| **Total Stability** | `I_3 / H(V)` | Stability of the collective macro-state, normalized by macro-signal entropy | Higher values mean the group behavior collapses into a more predictable collective state. The ToM condition sharply increases this metric. |
| **Agent differentiation** | Hierarchical mixed-model comparisons with random intercepts/slopes | Whether agents develop stable role-like differences in contribution level or learning trajectory | Significant model comparisons suggest persistent identity-linked differentiation rather than interchangeable agents. |
| **Success rate / rounds to success** | Whether the group exactly hits the hidden target, and how fast | Task performance | Used as an outcome, but the paper emphasizes that performance alone does not prove emergence. |
| **Synergy x redundancy interaction** | Regression interaction term between early synergy and redundancy | Whether useful performance requires both complementarity and shared alignment | The paper reports a significant interaction (`beta = 0.24`, `p = 0.014`), suggesting synergy helps most when paired with redundancy. |

The paper also reports **permutation/null-test p-values**, combines p-values across independent groups using **Fisher's method**, and checks whether bias-corrected estimates are above zero using **Wilcoxon signed-rank tests**. These are not the emergence metrics themselves; they are statistical tests used to decide whether the observed metrics are stronger than null baselines.

中文说明：论文的核心指标都来自智能体在时间序列中的猜测。微观变量是每个智能体相对于平均应贡献值的偏差 `dev_i,t`，宏观变量是群体总误差 `V_t`。主要指标包括成对动态协同 `Syn_ij`、实际涌现指标 `S_macro`、三人组信息量 `I_3`、三元信息增益 `G_3`、总稳定性 `I_3 / H(V)`、智能体分化指标以及任务成功率。其中，`S_macro` 最接近“群体是否超过个体之和”这个问题；`Syn_ij` 衡量成对协同；`G_3` 检测是否存在超越任意二人组合的三人结构；Total Stability 衡量群体是否进入稳定可预测的集体状态。Fisher 检验和 Wilcoxon 检验则是用来判断这些指标是否显著高于零模型。

## 6. Falsification and Robustness Tests

The paper is careful about false positives. It uses surrogate null tests:

- **Row-wise shuffling** breaks identity-linked structure.
- **Column-wise or block time shuffling** preserves some individual dynamics while disrupting cross-agent temporal alignment.
- Bias corrections and alternative entropy estimators address small-sample information-estimation problems.
- The paper also residualizes time trends and compares against functional null models.

This matters because multi-agent traces can look coordinated simply because agents follow similar time trends. The paper tries to distinguish real cross-agent structure from shared temporal drift.

中文说明：作者很重视排除伪协同。例如，行打乱用于破坏智能体身份结构，列打乱或时间块打乱用于破坏跨智能体的时间对齐。同时，论文还使用偏差校正、不同熵估计方法和功能性零模型，避免把共同时间趋势误判为协同。

## 7. Main Results

### 7.1 Multi-agent LLM systems show emergence capacity

Across the practical criterion and emergence-capacity criterion, the paper finds evidence that multi-agent LLM systems can exhibit dynamic emergence. This answers the first research question: yes, these systems can host higher-order structure.

### 7.2 Persona and ToM change the type of coordination

The conditions differ in their coordination regime:

- **Plain** groups can show temporal synergy, but much of it looks unstable or incidental.
- **Persona** prompts introduce stable identity-linked differentiation.
- **Persona + ToM** produces both differentiation and stronger goal-directed alignment.

The ToM condition is the clearest case of a group becoming an integrated, stable collective rather than just several agents moving around independently.

### 7.3 ToM acts like a control parameter

The paper reports that the ToM prompt sharply increases total stability. In the author's dynamical-systems framing, the ToM instruction moves the group from a disordered, "gaseous" state into a more stable basin of attraction. Put plainly: asking agents to reason about one another changes the collective dynamics of the system.

### 7.4 Pairwise alignment matters more than irreducible triplets

In the ToM condition, stability is largely supported by pairwise alignment rather than irreducible three-agent complexity. This suggests that in this task, agents mostly coordinate through the shared aggregate feedback signal instead of forming rich local coalitions.

### 7.5 Performance improves when synergy and redundancy coexist

Neither synergy alone nor redundancy alone predicts success. Their interaction does. The reported regression shows a significant synergy-redundancy interaction (`beta = 0.24`, `p = 0.014`). The interpretation is important:

- redundancy helps agents align on the shared goal;
- synergy helps agents make complementary contributions;
- good multi-agent performance needs both.

中文说明：主要结果是，多智能体 LLM 确实可以表现出涌现协同能力。普通提示下可能有一些时间上的协同，但不够稳定；角色提示带来身份相关的分化；角色加 ToM 提示最明显地产生目标导向的互补和稳定群体状态。论文还发现，单独的协同或冗余都不足以预测成功，真正有帮助的是二者共同存在：冗余带来共同目标对齐，协同带来互补贡献。

## 8. Generalization Across Models

The main experiments use GPT-4.1 with 10 agents, temperature 1.0, and 200 replications per condition. The paper also tests:

- Llama-3.1-8B
- Llama-3.1-70B-Instruct
- Gemini 2.0 Flash
- Qwen3 235B A22B Instruct

High-capability models show stronger evidence of emergence. Llama-3.1-8B struggles with the task and often fails to escape oscillation. Qwen3 shows a special failure mode called **paralysis under coordination ambiguity**: the model recognizes the ambiguity caused by other agents but can loop in reasoning instead of choosing a stable action.

中文说明：作者还在 Llama、Gemini 和 Qwen 上做了验证。能力较强的模型更容易表现出涌现结构；较小的 Llama 8B 经常陷入上下震荡；Qwen3 作为推理模型会出现“协同模糊下的瘫痪”，即模型意识到其他智能体造成了不确定性，却在推理中循环而无法稳定行动。

## 9. Why This Paper Matters for Multi-Agent AI Safety

This paper is useful for the Schmidt Sciences proposal paragraph because it operationalizes several vague but important concepts:

| Proposal concept | How this paper helps |
|---|---|
| Emergent collective capabilities | Gives information-theoretic metrics for higher-order group structure |
| Communication and coordination | Shows coordination can emerge even without direct communication |
| Interaction topology | Provides tools that could be extended to compare communication graphs |
| Phase transitions | Shows prompt interventions can shift a group from unstable to stable collective dynamics |
| Safety-relevant properties | Separates incidental coupling from goal-directed complementarity |
| Oversight | Suggests measurable signals for detecting when a MAS becomes more integrated |

For AI Forge, the paper is relevant to operational interpretability and predictive evaluation. It provides a way to monitor the internal coordination regime of an agent population rather than only scoring final outcomes.

中文说明：这篇论文对 Schmidt Sciences 的研究方向很有价值，因为它把“涌现能力”“协同”“相变”“群体结构”等概念变成了可以测量的指标。对 AI Forge 而言，它提供了一种系统级解释和评测工具：不仅看最终结果，还看智能体群体内部是否形成了稳定、互补、目标导向的结构。

## 10. Important Limitations

The paper is strong methodologically, but the scope is narrow.

- It studies one minimalist guessing task.
- The main setting uses 10 agents, not very large populations.
- Agents do not have direct communication, persistent tools, external resources, or long-term memory.
- The paper does not claim team-over-solo superiority.
- Synergy is a structural property, not evidence of consciousness, intention, or human-like cognition.
- Entropy and PID estimation are difficult in small data settings.
- The emergence-capacity test is pairwise, so it can miss higher-order synergy involving more than two agents.
- The study measures benign task coordination, not harmful collusion.

中文说明：论文的局限也很清楚：任务很简化，主要实验是 10 个智能体，没有真实工具、长期记忆或直接通信；论文不证明团队一定优于单智能体；协同信息只是结构性指标，不代表意识或真正意图；而且当前实验测的是良性协同，不是恶意合谋。

## 11. How to Explain It in One Minute

This paper asks whether multi-agent LLM systems are truly coordinating or merely producing several parallel answers. It uses information theory to decompose group behavior into redundancy, unique information, and synergy. In a group guessing game, agents receive only aggregate feedback, so identical strategies tend to fail. The paper shows that personas create stable agent differentiation, and personas plus a Theory-of-Mind prompt create more stable, goal-directed complementarity. The key takeaway is that prompt design can steer a multi-agent LLM system from a loose aggregate toward a more integrated collective, and this transition can be measured with formal information-theoretic tools.

中文一分钟解释：这篇论文研究多智能体 LLM 到底是在真正协同，还是只是多个模型并行作答。作者用信息论把群体行为分解成冗余、独有信息和协同信息。在群体猜数任务中，如果所有智能体策略相同就会失败；角色提示可以让智能体产生稳定分工，而角色加 ToM 提示可以进一步形成目标导向的互补协同。核心结论是：提示设计可以改变多智能体系统的集体动力学，并且这种变化可以被形式化测量。

## 12. Possible Research Extension

A natural next project is to turn this framework into a safety diagnostic:

1. Vary population size, heterogeneity, topology, tool access, and communication bandwidth.
2. Measure emergence capacity, practical emergence, stability, and goal alignment.
3. Add adversarial or faulty agents.
4. Test whether the same metrics detect transitions from benign coordination to collusion, cascading failure, or unsafe collective capability.
5. Evaluate whether interventions such as topology pruning, message filtering, or role randomization reduce risky emergence without destroying useful cooperation.

中文后续方向：可以把这篇论文的方法扩展成多智能体安全诊断框架。下一步可以系统改变智能体数量、异质性、拓扑、工具权限和通信带宽，并加入故障或恶意智能体，测试这些信息论指标是否能提前发现从良性协同转向合谋、级联失败或危险集体能力的过程。
