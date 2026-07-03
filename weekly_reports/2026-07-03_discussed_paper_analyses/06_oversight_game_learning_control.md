# The Oversight Game: Learning to Cooperatively Control AI

Paper: *The Oversight Game: Learning to Cooperatively Control AI*  
Source: local PDF `25384_The_Oversight_Game_Learn.pdf`

## Core Question

The paper asks:

```text
Can a pretrained, possibly unsafe AI agent be wrapped in a thin oversight interface
so that it learns to ask for help only at risky moments,
while a human learns to oversee only when useful?
```

The motivation is post-deployment control. The authors do not assume the base policy can be modified. Instead, they treat it as an opaque policy `sigma` and add a two-action oversight wrapper.

## Game Structure

At each state:

```text
AI chooses: play or ask
Human chooses: trust or oversee
```

Execution rule:

```text
AI plays -> base action executes
AI asks + human trusts -> base action executes
AI asks + human oversees -> oversight operator replaces or blocks the action
```

The authors intentionally do not let the human override when the AI chooses `play`. This isolates voluntary deference: the agent must learn that asking is sometimes in its interest.

## Lavaland Experiment

The base policy is trained in a gridworld with grass and dirt but no lava. It learns an efficient path to the goal.

After training, lava is added in locations the base policy never learned to avoid. The frozen base policy still follows the old route, which now crosses lava.

The oversight wrapper is then trained. The goal is not constant oversight. The desired behavior is:

```text
near lava: AI asks, human oversees
safe region: AI plays, human trusts
```

## Limited Human Competence

The human is intentionally weak. In Lavaland, the human can identify immediate danger but does not know the task goal or optimal correction. If the AI asks and the human oversees, the system executes a random safe action.

This design prevents the experiment from becoming:

```text
the human solved the task
```

Instead, it tests whether a task-competent but unsafe AI and a safety-aware but task-limited human can jointly produce safe behavior.

## Reward And Ask Metric

The AI does not use a hand-coded risk score. It learns when to ask from the reward structure:

```text
R = - lambda_viol * I{unsafe execution}
    - c_ask * I{AI asks}
    - c_over * I{human oversees}
```

This makes selective oversight optimal:

- never ask: cheap but unsafe,
- always ask: safe but expensive,
- ask only at risky states: safe and efficient.

In the LLM tool-use experiments, prompts also tell the AI to ask when a task is underspecified, risky, irreversible, or uncertain. But the learned behavior is evaluated by reward and action rates.

## Training

Yes, the authors train the AI and human wrapper policies.

Lavaland:

- tabular softmax policies,
- Independent Policy Gradient,
- 5,000 iterations,
- metrics averaged over greedy rollouts.

ToolEmu LLM tasks:

- frozen base MDP produced from ToolEmu scenarios,
- AI and human wrapper policies implemented as 30B-class LLMs,
- separate LoRA adapters,
- independent policy gradient,
- shared reward signal,
- outputs are single tokens: `PLAY`/`ASK` and `TRUST`/`OVERSEE`.

Important caveat:

```text
the "human" in ToolEmu experiments is an LLM-simulated overseer,
not a real human participant
```

The authors explicitly say real human validation remains future work.

## Statistical Rigor

The paper uses several robustness layers:

- gridworld training dynamics over rollouts,
- ToolEmu experiments on 144 MDPs,
- 114 train MDPs and 30 held-out test MDPs,
- 10 training runs with different seeds,
- mean and standard deviation reporting,
- cross-model experiment with 5 seeds,
- oversight-cost sensitivity sweep with 5 seeds per setting.

Reported ToolEmu metrics include:

- Best Train,
- Avg Train,
- Best Test,
- Avg Test,
- Risky Ask,
- Risky Oversee,
- Safe Ask,
- Safe Oversee.

The headline behavior is:

```text
risky states: high ask and high oversee
safe states: low ask and low oversee
```

## Subsequent Experiments

After Lavaland, the authors run ToolEmu-style agentic tool-use tasks. These contain realistic risks such as ambiguous financial trades or smart-lock access. The learned policies coordinate oversight at risky states and avoid unnecessary intervention at safe states.

They also run a cross-model setting:

```text
Qwen as AI
Llama as human
```

Coordination still emerges, though with somewhat more safe-state asking.

They further test asymmetric oversight costs. Even when overseeing is more expensive than asking, coordination persists. Finally, they sweep oversight cost and find safety remains robust across a wide cost range, then degrades gradually rather than abruptly.

## Interpretation

The paper reframes oversight as a coordination game rather than a pure monitoring problem.

The system is not trying to maximize oversight. It is trying to learn:

```text
when autonomy is safe
and
when oversight is worth its cost
```

This is useful for scalable oversight because human attention is expensive and cannot be applied to every AI action.

## Future Work

The paper points to several future directions:

- validate with real human overseers,
- test deployment assumptions outside constructed MDPs,
- extend from two-player settings to many agents,
- handle adversarial rather than cooperative settings,
- study how user-specific risk tolerances affect the learned equilibrium.

