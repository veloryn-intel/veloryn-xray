# Determinism

X-Ray is deterministic infrastructure.

Given identical input and identical algorithm versions, X-Ray produces identical output values.

## Guarantees

X-Ray uses:

- no randomness
- no sampling
- no LLM calls
- no embeddings
- no semantic model
- no time-dependent logic
- no network-dependent inference

## Deterministic Scope

The determinism guarantee applies to:

- validity decision
- failure reason
- contribution values
- smoothed peak value
- peak step
- waste ratio
- timeline labels
- pattern type
- fail-safe output
- selector-aligned peak markers in CLI/UI plots

## Lexical-Only Continuity

Continuity is based on deterministic lexical processing:

- lowercase text
- regex token extraction
- stopword filtering
- structural-token filtering
- overlap ratio between consecutive outputs

No semantic inference is used.

## Peak Selection Determinism

Peak selection uses a stabilized selector trajectory rather than raw normalized contributions directly.

The early-step stabilization rule is deterministic. Identical inputs therefore produce identical peak-selection outcomes, and selector-aligned visualizations reproduce the same visible peak every time.

An earlier step can still have a higher instantaneous contribution value than the final selected peak step. That is expected under the selector model and does not indicate nondeterminism or divergence across layers.

## Version Tracking

Valid outputs include version fields:

- `rf_version`
- `rf_token_version`
- `contribution_version`
- `validation_version`
- `tokenizer_version`

These fields support auditability and help compare outputs across releases.

Invalid fail-safe outputs intentionally omit these internal version fields to preserve invalid-state isolation.

## Invariant Fixtures

Permanent fixtures include:

Must fail:

```json
[
  {"output": "capital of france"},
  {"output": "capital of germany"}
]
```

Must pass:

```json
[
  {"output": "sort descending"},
  {"output": "use reverse=True"}
]
```

Repetition:

```json
[
  {"output": "a"},
  {"output": "a"}
]
```

Current gradual-improvement behavior:

```json
[
  {"output": "draft api retry loop"},
  {"output": "draft api retry loop timeout backoff"},
  {"output": "draft api retry loop timeout backoff jitter status codes"},
  {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging"},
  {"output": "draft api retry loop timeout backoff jitter status codes idempotency logging circuit breaker alerts"}
]
```

Expected current values:

- `is_valid: true`
- `peak_step: 1`
- `waste_ratio: 0.9091`
- `contributions: [2.6, 2.0, 3.0, 2.0, 3.0]`

## Verification Probe

```python
from veloryn.xray import analyze_structured

fixture = {
    "steps": [
        {"output": "sort descending"},
        {"output": "use reverse=True"},
    ]
}

outputs = [analyze_structured(fixture).to_dict() for _ in range(10)]

assert all(output == outputs[0] for output in outputs)
```
