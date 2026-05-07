# SDK Contract

This document describes the current packaged Python SDK contract for X-Ray.

## Public Entry Points

```python
from veloryn.xray import analyze_structured, analyze_raw
```

These are the only public SDK entry points.

Implementation:

- `veloryn/xray/sdk.py`
- `veloryn/xray/models.py`
- `veloryn/xray/parser.py`

## Installation

Package install command:

```bash
pip install veloryn-xray
```

Editable local install:

```bash
pip install -e .
```

## Structured Input Contract

`analyze_structured(data: dict) -> XRayResult`

Required shape:

```python
{
    "steps": [
        {"output": "step 1 text"},
        {"output": "step 2 text"},
    ]
}
```

Rules:

- top-level input must be a `dict`
- `steps` must exist
- `steps` must be a `list`
- every step must contain string `output`

Invalid schema raises `ValueError`.

Schema invalidity is not fail-safe.

## Raw Input Contract

`analyze_raw(text: str) -> XRayResult`

Accepted raw forms:

- newline-separated text, one step per line
- JSON text representing a structured payload
- JSON text representing a list payload that the engine already accepts

If raw parsing yields no execution, the SDK returns fail-safe.

## Structural Validity And Execution Validity

X-Ray separates two concepts.

Structural validity:

- concerns whether input can be accepted by the SDK boundary
- invalid structured schema raises `ValueError`

Execution validity:

- concerns whether provided outputs form one evolving execution trajectory
- invalid execution returns fail-safe
- fail-safe is terminal and contains no trajectory analysis

## Result Models

The SDK uses dataclasses only.

Stable model names:

- `TimelineStep`
- `Verdict`
- `Summary`
- `AnalysisSignals`
- `Analysis`
- `Meta`
- `XRayResult`

## Valid SDK Result Shape

Valid execution serializes to:

```python
{
    "is_valid": True,
    "verdict": {
        "peak_step": 2,
        "should_stop_at": 2,
        "waste_percentage": 0,
    },
    "summary": {"reason": "Most value was captured early."},
    "meta": {"version": "0.1.0"},
    "timeline": [
        {"step": 1, "label": "improving"},
        {"step": 2, "label": "peak"},
    ],
    "analysis": {
        "signals": {
            "redundancy_trend": "stable",
            "contribution_trend": "stable",
        }
    }
}
```

Timeline labels at the SDK boundary are normalized to:

- `improving`
- `peak`
- `declining`
- `repeating`

## Invalid SDK Result Shape

Fail-safe serializes to:

```python
{
    "is_valid": False,
    "verdict": {"message": "No clear execution pattern detected."},
    "summary": {"reason": "This does not appear to be a single evolving task."},
    "meta": {"version": "0.1.0"},
}
```

Fail-safe does not contain:

- `timeline`
- `analysis`
- internal signals
- numeric engine metrics
- narrative engine prose

## Fail-Safe Strings

These SDK strings are fixed:

- `verdict.message == "No clear execution pattern detected."`
- `summary.reason == "This does not appear to be a single evolving task."`

## Serialization Contract

All SDK result models implement `to_dict()`.

Guarantees:

- deterministic field ordering
- JSON-serializable output
- no custom encoder required
- no dataclass internals exposed directly
- invalid results omit absent sections instead of exposing `null`

Example:

```python
import json

from veloryn.xray import analyze_structured

result = analyze_structured(
    {
        "steps": [
            {"output": "a"},
            {"output": "a"},
        ]
    }
)

payload = result.to_dict()
json.dumps(payload)
```

## CLI Packaging

The packaged console entry point is:

```bash
xray
```

It delegates to the existing CLI behavior through `veloryn.xray.cli:main`.

## Determinism

For identical input and identical algorithm versions, the SDK returns identical serialized output.

The SDK layer is a mapper only. It does not change continuity, peak logic, waste calculation, RF logic, or contribution values. It exposes only a reduced public presentation of those frozen engine results.
