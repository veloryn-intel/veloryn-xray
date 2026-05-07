# X-Ray Philosophy

## Purpose

X-Ray is designed to analyze execution behavior in multi-step LLM workflows.

It measures how outputs evolve across steps and identifies where structural contribution declines under continued execution.

X-Ray is not a reasoning engine, correctness evaluator, or semantic judge.

Its purpose is narrower:

- detect execution continuity
- detect diminishing structural contribution
- identify execution collapse and repetition
- enforce deterministic execution-validity boundaries

---

## Why X-Ray Is Lexical Instead of Semantic

X-Ray intentionally uses deterministic lexical analysis instead of embeddings, semantic similarity, or probabilistic models.

This choice was made to preserve:

- determinism
- reproducibility
- explainability
- auditability
- stable SDK contracts

Given identical input, X-Ray should always produce identical output.

Semantic systems often introduce:

- nondeterministic behavior
- opaque scoring
- model drift
- version instability
- hidden dependency changes

X-Ray avoids these properties intentionally.

---

## Execution Continuity vs Topic Similarity

X-Ray does not attempt to determine whether two steps are semantically related.

Instead, it asks a narrower question:

> Does the later step operationally continue the earlier execution?

This distinction matters.

These should fail continuity:

```json
[
  {"output": "capital of france"},
  {"output": "capital of germany"}
]
```

These should pass continuity:

```json
[
  {"output": "sort descending"},
  {"output": "use reverse=True"}
]
```

The first pair contains topical adjacency but no evolving execution structure.

The second pair contains operational refinement.

X-Ray is designed to distinguish between these cases using deterministic lexical continuity rules.

---

## Why Fail-Safe Exists

Not every sequence of outputs represents a valid execution trajectory.

Without explicit validity boundaries, execution analysis systems can produce confident interpretations of unrelated or malformed inputs.

X-Ray uses fail-safe behavior to prevent invalid execution analysis.

Invalid executions terminate early and do not expose:

- trajectory analysis
- plots
- internal signals
- contribution arrays
- continuity diagnostics

Fail-safe is a terminal invalid state.

---

## Structural Validity vs Execution Validity

X-Ray separates two different concepts:

### Structural Validity

Questions like:

- Is the schema valid?
- Are required fields present?
- Is the input parseable?

These are interface-level concerns.

Invalid structure should raise explicit errors.

---

### Execution Validity

Questions like:

- Do the steps form a continuous trajectory?
- Is there evidence of evolving execution?
- Does the sequence represent a single task?

These are execution-analysis concerns.

Invalid execution produces fail-safe.

This distinction is foundational to the system architecture.

---

## Why Determinism Matters

X-Ray is intended for:

- infrastructure analysis
- execution visibility
- reproducible auditing
- workflow instrumentation
- SDK integration

These use cases require stable outputs.

A deterministic system allows:

- invariant testing
- reproducible debugging
- regression tracking
- stable integrations
- version comparability

This is prioritized over maximizing semantic interpretation quality.

---

## Stabilized Peak Selection

Peak selection uses a stabilized selector trajectory rather than raw normalized contributions directly.

This keeps the engine from overcommitting to pathological Step-1 dominance in short or front-loaded runs.

Visible contribution values are therefore not always the direct selector basis. As a result, a later step may be selected even when an earlier step has a slightly higher instantaneous contribution value.

CLI and UI visualizations are selector-aligned so the visible peak matches the final selected outcome, while debug mode continues to expose raw and normalized contribution values intentionally.

---

## Why X-Ray Does Not Evaluate Correctness

X-Ray measures execution behavior, not answer quality.

It does not determine:

- factual accuracy
- usefulness
- correctness
- hallucination rate
- task success

A highly accurate answer and a completely incorrect answer may produce similar execution trajectories.

That limitation is intentional.

Correctness evaluation belongs to a different system layer.

---

## Why Some Interpretation Imperfections Remain

X-Ray intentionally avoids aggressive semantic heuristics and adaptive tuning.

This means some interpretation edge cases may remain imperfect, especially around:

- gradual refinement
- concise technical edits
- expansion vs repetition ambiguity
- short trajectory interpretation

These are treated as interpretation-quality limitations, not integrity failures.

The system prioritizes:

- deterministic boundaries
- stable contracts
- explainable behavior

over aggressive semantic inference.

---

## Architectural Direction

X-Ray is designed as:

- deterministic execution-analysis infrastructure
- not autonomous reasoning infrastructure

Its core responsibilities are:

- execution validity enforcement
- trajectory analysis
- redundancy measurement
- execution collapse visibility

Future layers may build on top of X-Ray, but the core engine intentionally remains:

- lexical
- bounded
- deterministic
- auditable
- infrastructure-oriented
