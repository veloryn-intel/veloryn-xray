# Execution Validity Contract

X-Ray validates whether a set of outputs forms one sequential execution trajectory before it performs trajectory analysis.

Execution validity is deterministic and lexical. It is not semantic reasoning.

## Structural Validity Versus Execution Validity

Structural validity concerns API input shape.

Execution validity concerns whether the step outputs form one evolving execution.

These are distinct:

- top-level non-list SDK input raises `ValueError`
- malformed task/step objects inside a list return fail-safe with `invalid_schema` or `insufficient_data`
- valid schema with non-evolving execution returns fail-safe with `low_continuity` or `context_shift`

Fail-safe is a terminal invalid execution state.

## Valid Execution

A valid execution:

- has at least two step outputs
- uses array order as the execution order
- passes deterministic lexical continuity checks
- is not an independent Q&A sequence
- is not a detected topic replacement or context shift
- produces full trajectory analysis

Explicit `step` fields are not required and are not used for ordering.

## Invalid Execution

An invalid execution returns fail-safe only:

```json
{
  "is_valid": false,
  "headline_verdict": "No clear execution pattern detected.",
  "core_insight": "This does not appear to be a single evolving task.",
  "failure_reason": "low_continuity"
}
```

The engine also includes `task_id` when available. UI display payloads omit `failure_reason`.

Fail-safe contains no:

- trajectory
- peak
- waste
- contribution array
- RF array
- debug data
- version fields
- plot

## Continuity Measurement

Validation uses lexical content overlap between consecutive outputs.

Conceptually:

```text
overlap(current, previous) =
number of current content tokens also present in previous content tokens
/ number of current content tokens
```

The implementation:

- lowercases text
- extracts lexical tokens with a regular expression
- removes stopwords
- removes structural continuity tokens such as `answer`, `question`, `response`, `solution`, and `capital`
- treats `q1`, `q2`, etc. as structural markers

This is not Jaccard similarity and not semantic similarity.

## Continuity Constants

Current constants in `pattern_extractor/validator.py`:

```python
LOW_OVERLAP_THRESHOLD = 0.25
MIN_DISCONTINUOUS_STEPS = 3
STRONG_CONTINUITY_THRESHOLD = 0.40
ABRUPT_DROP_LOW_THRESHOLD = 0.18
ABRUPT_DROP_DELTA = 0.25
LOW_CONTINUITY_AVERAGE_THRESHOLD = 0.30
MIN_TRANSITIONS = 3
```

These constants are deterministic. They are not learned or adaptive.

## Short-Run Boundary

Short runs require special boundary handling because a single shared generic token can otherwise create false continuity.

Must fail:

```json
[
  {"output": "capital of france"},
  {"output": "capital of germany"}
]
```

Runtime result:

- `is_valid: false`
- `failure_reason: low_continuity`

Reason:

- this is independent Q&A
- `capital` is structural QA vocabulary
- there is no operational execution dependency

Must pass:

```json
[
  {"output": "sort descending"},
  {"output": "use reverse=True"}
]
```

Runtime result:

- `is_valid: true`
- `peak_step: 2`
- `waste_ratio: 0.0`

Reason:

- this is a concise operational refinement
- operational markers such as `sort`, `descending`, `use`, and `reverse=True` preserve the refinement boundary

## Repetition Boundary

```json
[
  {"output": "a"},
  {"output": "a"}
]
```

Runtime result:

- `is_valid: true`
- `peak_step: 1`
- `waste_ratio: 0.5`
- timeline includes `Repeating`

Repetition is valid because it is continuous, even when it is unproductive.

## Context Shift

Context shift is detected lexically through trajectory patterns such as:

- strong continuity followed by abrupt low continuity
- strong continuity, abrupt collapse, then strong continuity in a replacement topic
- sustained low continuity after previously valid continuity

Example invalid shape:

```json
[
  {"output": "vector database embeddings index query recall"},
  {"output": "vector database embeddings index query recall hnsw metadata filters"},
  {"output": "blockchain consensus validators proof stake finality"},
  {"output": "blockchain consensus validators proof stake finality forks"}
]
```

Runtime result:

- `is_valid: false`
- `failure_reason: context_shift`

## Determinism

Validation has no randomness and no external model calls.

Same input plus same algorithm versions produces the same validity decision, failure reason, and valid-output metrics.

## Implementation Reference

- `pattern_extractor/validator.py::is_valid_execution_pattern`
- `pattern_extractor/validator.py::compute_content_overlaps`
- `pattern_extractor/validator.py::detect_context_shift`
- `pattern_extractor/extractor.py::_extract_task`

