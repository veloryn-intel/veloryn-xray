# SDK Examples

These examples demonstrate the packaged SDK only.

Public imports:

```python
from veloryn.xray import analyze_structured, analyze_raw
```

Scripts:

- [structured_sdk_example.py](./structured_sdk_example.py)
- [raw_sdk_example.py](./raw_sdk_example.py)
- [serialization_example.py](./serialization_example.py)

## Structured Example

```bash
python examples/sdk/structured_sdk_example.py
```

Expected:

- valid result
- `peak_step: 2`
- `should_stop_at: 2`
- `waste_percentage: 0`
- timeline labels `improving`, `peak`
- minimal analysis signals only

## Raw Example

```bash
python examples/sdk/raw_sdk_example.py
```

Expected:

- valid result
- same deterministic SDK shape as structured mode

## Serialization Example

```bash
python examples/sdk/serialization_example.py
```

Expected:

- `result.to_dict()` returns JSON-serializable data
- `json.dumps(...)` works without custom encoders
- internal engine arrays and version fields are omitted

## Fail-Safe Handling

```python
from veloryn.xray import analyze_structured

result = analyze_structured(
    {
        "steps": [
            {"output": "capital of france"},
            {"output": "capital of germany"},
        ]
    }
)

payload = result.to_dict()
assert payload["is_valid"] is False
assert "timeline" not in payload
assert "analysis" not in payload
```
