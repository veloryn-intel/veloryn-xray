# Testing

This document describes the deterministic fixture strategy for X-Ray.

## Test Goals

Tests should verify:

- valid execution remains valid
- invalid execution returns fail-safe
- fail-safe isolation is preserved
- deterministic outputs remain stable
- contribution and smoothing arrays do not drift unintentionally
- CLI invalid modes do not leak debug, analysis, or plots

## Existing Test Commands

Run Python tests:

```bash
python -m unittest discover -s tests
```

Verify editable install:

```bash
pip install -e .
```

Build UI:

```bash
npm run build
```

## Invariant Fixtures

Must fail:

```python
[
    {"output": "capital of france"},
    {"output": "capital of germany"}
]
```

Expected:

- `is_valid is False`
- `failure_reason == "low_continuity"`

Must pass:

```python
[
    {"output": "sort descending"},
    {"output": "use reverse=True"}
]
```

Expected:

- `is_valid is True`
- `peak_step == 2`
- `waste_ratio == 0.0`

Repetition:

```python
[
    {"output": "a"},
    {"output": "a"}
]
```

Expected:

- `is_valid is True`
- `peak_step == 1`
- `waste_ratio == 0.5`
- timeline includes `Repeating`

Topic shift:

```python
[
    {"output": "vector database embeddings index query recall"},
    {"output": "vector database embeddings index query recall hnsw metadata filters"},
    {"output": "blockchain consensus validators proof stake finality"},
    {"output": "blockchain consensus validators proof stake finality forks"}
]
```

Expected:

- `is_valid is False`
- `failure_reason == "context_shift"`

Gradual current behavior:

```python
[
    {"output": "draft api retry loop"},
    {"output": "draft api retry loop timeout backoff"},
    {"output": "draft api retry loop timeout backoff jitter status codes"},
    {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging"},
    {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging circuit breaker alerts"}
]
```

Expected:

- `is_valid is True`
- `peak_step == 1`
- `waste_ratio == 0.9091`
- `contributions == [2.6, 2.0, 3.0, 2.0, 3.0]`

## Determinism Check

```python
import json

from veloryn.xray import analyze_structured

fixture = {
    "steps": [
        {"output": "sort descending"},
        {"output": "use reverse=True"},
    ]
}

outputs = [
    json.dumps(analyze_structured(fixture).to_dict(), sort_keys=True)
    for _ in range(10)
]

assert len(set(outputs)) == 1
```

## Fail-Safe Isolation Check

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

for field in [
    "timeline",
    "analysis",
]:
    assert field not in result
```

## CLI Invalid Checks

For an invalid JSON file:

```bash
python -m cli.main invalid.json
python -m cli.main --analysis invalid.json
python -m cli.main --debug invalid.json
python -m cli.main --plot invalid.json
```

Expected for all commands:

```text
[VERDICT]
No clear execution pattern detected.

[WHY]
This does not appear to be a single evolving task.
```

No plot should be saved for invalid execution.
