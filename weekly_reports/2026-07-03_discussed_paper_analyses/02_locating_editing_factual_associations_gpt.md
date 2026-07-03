# Locating and Editing Factual Associations in GPT

Paper: *Locating and Editing Factual Associations in GPT*  
Authors: Kevin Meng, David Bau, Alex Andonian, Yonatan Belinkov  
Venue: NeurIPS 2022  
Source: local PDF `Locating_and_Editing_Facts.pdf`

## Core Question

The paper asks:

```text
Where does a GPT-style language model store factual associations,
and can we directly edit those associations?
```

Example fact:

```text
The Space Needle is located in Seattle.
```

The authors want to know whether this fact is distributed everywhere in the model or whether there are localized computations that can be identified and modified.

## Causal Tracing

The paper develops a causal tracing procedure based on causal mediation analysis.

For a factual prompt, it runs the model in three ways:

1. **Clean run:** the normal prompt produces the correct object.
2. **Corrupted run:** the subject token embedding is corrupted, damaging the prediction.
3. **Corrupted-with-restoration run:** the subject remains corrupted, but one internal activation is patched back to its clean value.

If restoring one activation recovers the correct answer, that activation is causally important for the factual prediction.

The paper measures:

```text
total effect = P_clean(object) - P_corrupted(object)
indirect effect = P_restored(object) - P_corrupted(object)
```

Then it averages these effects across many factual statements.

## Main Finding

The surprising finding is an **early site**:

```text
middle-layer MLP modules at the last subject token
```

These mid-layer feed-forward modules have strong causal effects on factual recall. The paper also finds a later site near the final token, but that late site is less surprising because final layers directly feed the output prediction.

The interpretation is:

```text
MLPs act like key-value memories.
The subject representation provides a key.
The MLP output recalls property information about the subject.
Later attention moves that information to the final prediction position.
```

## ROME

ROME stands for **Rank-One Model Editing**. It tests the causal tracing hypothesis by editing a model weight matrix at the proposed factual-storage site.

The simplified idea:

```text
Given subject key k*
and desired new value v*,
apply a rank-one update so the MLP maps k* to v*
while minimally interfering with other stored associations.
```

This makes the paper stronger than a pure interpretability study. It does not only locate a circuit; it edits the model at that location and checks whether the edit behaves as expected.

## Evaluation

The paper evaluates ROME on:

- zsRE, a standard zero-shot relation extraction model-editing benchmark,
- COUNTERFACT, a harder dataset of counterfactual assertions,
- comparisons against fine-tuning, Knowledge Editor, MEND, and Knowledge Neurons,
- generalization to paraphrases,
- specificity on unrelated facts,
- human evaluation of generated text.

The important result is not merely high edit success. The important result is the combination:

```text
high efficacy + generalization + specificity
```

Other methods often either generalize poorly or cause bleedover to neighboring facts. ROME is presented as better at preserving specificity while changing the targeted association.

## Why We Discussed It

This paper provides a concrete example of **mechanistic localization**:

```text
identify where a capability is computed
then intervene directly at that site
```

This connects to later multi-agent safety discussions because many proposals require localizing where behavior, credit, risk, or information resides. ROME is a single-model example of the same general principle: interventions are safer when they are targeted to the right mechanism.

## Limitations

- ROME edits one fact at a time; it is not meant as a large-scale retraining method.
- Edited associations are directional; inverse facts may require separate edits.
- The work focuses on factual associations, not logical, numerical, social, or multi-step beliefs.
- Direct model editing can be useful for correction but also dangerous if used to insert misinformation.

