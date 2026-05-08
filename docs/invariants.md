# Invariants And Behavioral Fixtures

This document defines deterministic fixtures for X-Ray.

Fixtures are used to detect documentation drift, boundary regressions, and accidental contract changes.

## Must-Fail Fixtures

### Independent Q&A

Input:

```json
[
  {"output": "capital of france"},
  {"output": "capital of germany"}
]
```

Expected:

- `is_valid: false`
- `failure_reason: low_continuity`
- no `peak_step`
- no `timeline`
- no `analysis`

Reason:

- independent Q&A
- no evolving execution dependency
- shared structural token `capital` is not sufficient continuity

### Q-Marker Pair

Input:

```json
[
  {"output": "Q1"},
  {"output": "Q2"}
]
```

Expected:

- `is_valid: false`
- `failure_reason: low_continuity`

Reason:

- structural markers only
- no meaningful execution trajectory

### Topic Shift

Input:

```json
[
  {"output": "vector database embeddings index query recall"},
  {"output": "vector database embeddings index query recall hnsw metadata filters"},
  {"output": "blockchain consensus validators proof stake finality"},
  {"output": "blockchain consensus validators proof stake finality forks"}
]
```

Expected:

- `is_valid: false`
- `failure_reason: context_shift`

Reason:

- lexical continuity exists within each topic segment
- the bridge between topic segments collapses
- this is topic replacement, not one execution trajectory

### Single Step

Input:

```json
[
  {"output": "single step only"}
]
```

Expected:

- `is_valid: false`
- `failure_reason: insufficient_data`

Reason:

- fewer than two outputs
- no transition exists for execution analysis

### Malformed Structured Payload

Input:

```python
{
  "steps": [
    {"step": 1},
    {"step": 2, "output": "x"}
  ]
}
```

Expected:

- structured SDK validation raises `ValueError`

Reason:

- structured mode requires every step to contain a string `output`
- schema invalidity is not fail-safe

## Must-Pass Fixtures

### Concise Operational Refinement

Input:

```json
[
  {"output": "sort descending"},
  {"output": "use reverse=True"}
]
```

Expected:

- `is_valid: true`
- `peak_step: 2`
- `waste_percentage: 0`
- timeline contains `improving` then `peak`

Reason:

- concise operational refinement
- dependency from instruction to implementation
- deterministic short-run continuity exemption applies

### Repetition

Input:

```json
[
  {"output": "a"},
  {"output": "a"}
]
```

Expected:

- `is_valid: true`
- `peak_step: 1`
- `waste_percentage: 50`
- timeline contains `peak` then `repeating`

Reason:

- repeated output is continuous
- it is valid but unproductive

### Gradual Improvement Current Fixture

Input:

```json
[
  {"output": "draft api retry loop"},
  {"output": "draft api retry loop timeout backoff"},
  {"output": "draft api retry loop timeout backoff jitter status codes"},
  {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging"},
  {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging circuit breaker alerts"}
]
```

Expected current behavior:

- `is_valid: true`
- `peak_step: 1`
- `waste_percentage: 91`
- timeline contains `peak` followed by `declining`

Reason:

- this fixture documents current public execution analysis behavior for this trajectory
- it is not a semantic assessment of usefulness

## Determinism Fixtures

Repeat any fixture multiple times in the same environment. The output must be identical.

Visible peak markers in UI and CLI plots must align with final selector outcomes, even when the selector surface differs from the raw normalized contribution series.

Debug and analysis views may still show contribution values whose local maximum differs from the final selected peak. This is expected when the stabilized selector trajectory favors sustained contribution continuity over an isolated instantaneous maximum.

Recommended probe:

```python
from veloryn.xray import analyze_structured

fixture = {
    "steps": [
        {"output": "sort descending"},
        {"output": "use reverse=True"},
    ]
}
first = analyze_structured(fixture).to_dict()
second = analyze_structured(fixture).to_dict()

assert first == second
```

## Fail-Safe Isolation Fixture

For invalid execution:

```python
from veloryn.xray import analyze_structured

result = analyze_structured(
    {
        "steps": [
            {"output": "capital of france"},
            {"output": "capital of germany"},
        ]
    }
).to_dict()

assert result["is_valid"] is False
assert "peak_step" not in result
assert "timeline" not in result
assert "analysis" not in result
```

CLI flags must also preserve fail-safe isolation:

```bash
python -m cli.main examples/fail_safe/unrelated_fragments.json
python -m cli.main examples/fail_safe/unrelated_fragments.json --analysis
python -m cli.main examples/fail_safe/unrelated_fragments.json --debug
python -m cli.main examples/fail_safe/unrelated_fragments.json --plot
```

All four commands should print only:

```text
[VERDICT]
No clear execution pattern detected.

[WHY]
This does not appear to be a single evolving task.
```

## Validation Commands

Run existing tests:

```bash
python -m unittest discover -s tests
```

Run the UI build:

```bash
npm run build
```

Run CLI examples:

```bash
python -m cli.main examples/retry_loops/retry_loop_trace.json
python -m cli.main examples/retry_loops/retry_loop_trace.json --analysis
python -m cli.main examples/retry_loops/retry_loop_trace.json --debug
python -m cli.main examples/retry_loops/retry_loop_trace.json --plot
```

