# Dataless Weight Disentanglement in Task Arithmetic via Kronecker-Factored Approximation

Paper: *Dataless Weight Disentanglement in Task Arithmetic via Kronecker-Factored Approximation*  
Source: arXiv 2602.17385, https://arxiv.org/abs/2602.17385

## Core Question

The paper studies **task arithmetic**, where one represents a task by a weight-space update:

```text
task vector = fine-tuned model weights - base model weights
```

These task vectors can then be added or negated to compose model behavior. The problem is that ordinary task vectors are often **entangled**: a direction meant to add one task can interfere with other capabilities or other task vectors.

The paper asks whether one can improve task arithmetic without external data by regularizing fine-tuning so that task vectors become more localized and less interfering.

## Highlighted Sentence Explained

The highlighted sentence was:

```text
linking the weight disentanglement objective to curvature-aware optimization
```

In simpler terms, the authors are saying:

```text
Do not treat all weight directions as equally important.
Use curvature information to identify which directions are sensitive for model behavior,
then discourage task vectors from moving in ways that cause unnecessary interference.
```

Curvature-aware optimization uses local second-order information about the loss landscape. If a weight direction has high curvature, small movement there can strongly affect model output. If a direction has low curvature, movement is less behaviorally disruptive. The paper uses this idea to make task arithmetic more stable.

## Method

The key technical bridge is the **Jacobian Gram matrix**, which the paper connects to the generalized Gauss-Newton matrix. The full curvature matrix is too large to store or compute, so the paper adopts **KFAC**, the Kronecker-Factored Approximate Curvature method.

KFAC approximates each layer's curvature block as a Kronecker product of two smaller matrices:

```text
layer curvature block ≈ A ⊗ B
```

This preserves useful within-layer correlation structure while being much cheaper than a full curvature matrix.

The paper then adapts KFAC to task arithmetic:

- Build a curvature-aware regularizer for each task.
- Encourage task vectors to move in low-interference directions.
- Aggregate per-task curvature factors into a single surrogate so complexity does not grow linearly with the number of tasks.

The method is called **TAK**, Task Arithmetic with KFAC regularization.

## Why The Design Matters

The main design choice is to make the method **dataless** at composition time. This matters because task arithmetic is often attractive precisely when one does not want to gather validation data for every new task combination.

The paper tries to preserve three desirable properties:

- **Task addition:** adding task vectors should improve multiple target skills at once.
- **Task negation:** subtracting a task vector should remove a behavior without broadly damaging the model.
- **Robust rescaling:** performance should be less sensitive to the exact scaling coefficient placed on a task vector.

## Metrics And Evaluation Logic

The paper evaluates whether task vectors become less entangled by checking:

- task addition performance,
- task negation performance,
- disentanglement error in task-vector planes,
- localization of task effects in function space,
- robustness to task-vector scaling.

The key qualitative point from the figure we discussed is that KFAC/Jacobian-Gram regularization reshapes the task-vector landscape: the regularized version has lower disentanglement error and cleaner task-vector directions.

## Interpretation

This paper is not about multi-agent systems directly, but it matters for the broader safety agenda because it studies **modular intervention in learned systems**. If model behaviors can be localized and composed with less interference, then higher-level agent systems may become easier to modify, constrain, or audit.

The conceptual analogy to the multi-agent papers is:

```text
task-vector disentanglement in weights
is like
role / contribution disentanglement in agent systems
```

Both try to avoid hidden interference between components.

## Limitations

- Curvature approximations are still approximations; KFAC does not capture full cross-layer structure.
- Dataless composition is useful, but it cannot replace evaluation on real downstream behavior.
- The method depends on whether the chosen curvature surrogate tracks the behavior one actually wants to preserve.

