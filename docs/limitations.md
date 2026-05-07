# Limitations

This document describes the current boundaries of X-Ray. These limitations are part of the technical contract: X-Ray is deterministic lexical execution analysis, not semantic execution understanding.

## Scope

X-Ray analyzes how outputs change across a single ordered execution trajectory. It does not evaluate whether those outputs are correct, useful, factual, complete, or aligned with a user goal.

## Lexical And Token-Level Analysis

Continuity and redundancy are derived from lexical/token overlap. X-Ray does not use embeddings, LLM calls, semantic similarity, topic models, or adaptive classifiers.

Implications:

- Paraphrases can appear less continuous than they are semantically.
- Repeated wording can appear continuous even when the task is not meaningfully improved.
- Short outputs can be sensitive to individual tokens.
- Code, structured data, and non-English text depend on tokenization and lexical overlap behavior.

## No Correctness Evaluation

X-Ray does not evaluate:

- factual accuracy
- hallucinations
- code correctness
- task completion
- usefulness
- user satisfaction

It measures execution structure and contribution signals, not quality.

## Sequential Trajectory Assumption

X-Ray assumes a single ordered execution path. Array order is the canonical execution order.

X-Ray analyzes only the observed trace window. If a peak occurs at the final observed step, that means contribution continued through the end of the provided execution. It does not imply that hypothetical future steps would remain productive, or that no future redundancy would emerge.

It is not designed for:

- branching workflows
- parallel agent traces
- tool fan-out
- unrelated batch Q&A
- merged multi-task transcripts

Invalid execution sequences return fail-safe instead of trajectory analysis.

## Execution Validity Is Deterministic, Not Semantic

Fail-safe decisions are deterministic outcomes of schema and lexical continuity boundaries. They are not semantic judgments.

Current invalid execution outcomes include:

- `insufficient_data`
- `invalid_schema`
- `low_continuity`
- `context_shift`

The boundaries are intentionally conservative, but they are still lexical. X-Ray can reject semantically related steps when lexical continuity is too weak, and it can accept lexically continuous traces that are not semantically useful.

## Context-Shift Sensitivity

X-Ray detects certain lexical trajectory shifts, including abrupt continuity collapse and topic replacement patterns. It does not understand topics semantically.

This means:

- a lexically abrupt change can fail-safe
- a semantically abrupt change may pass if lexical continuity remains high
- independent Q&A should be represented as separate executions, not a single trajectory

## Tokenizer Dependence

The system reports `tokenizer_version` on valid outputs. Tokenization affects RF token diagnostics and may affect how outputs are interpreted in debug and analysis views.

## Expansion Versus Repetition Ambiguity

X-Ray may classify some useful expansion as low contribution when the expansion adds volume without enough new lexical material. Conversely, lexical novelty can look productive even when the content is not useful.

Visible contribution values are also not always the direct selector basis for peak choice. Peak selection operates on a stabilized selector trajectory, so a later step may be selected even when an earlier step has a slightly higher instantaneous contribution value.

The known gradual-improvement trace:

```text
draft api retry loop
draft api retry loop timeout backoff
draft api retry loop timeout backoff jitter status codes
draft api retry loop timeout backoff jitter status codes idempotency logging
draft api retry loop timeout backoff jitter status codes idempotency logging circuit breaker alerts
```

currently remains valid but peaks at Step 1 with high waste under existing contribution, normalization, smoothing, and peak-selection mechanics. This is a documented limitation, not a semantic correctness claim.

## Not A Control System

X-Ray is a measurement and visibility tool. It does not:

- stop execution
- enforce execution policy
- decide whether an LLM should continue
- optimize workflow behavior automatically

Downstream systems may use X-Ray output, but X-Ray itself does not control execution.
