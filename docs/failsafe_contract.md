# Fail-Safe Contract

Fail-safe is the terminal invalid-execution state in X-Ray.

It exists to prevent trajectory analysis from being produced for inputs that do not represent one evolving execution.

## Invalid Execution Contract

Engine fail-safe result:

```python
{
    "is_valid": False,
    "headline_verdict": "No clear execution pattern detected.",
    "core_insight": "This does not appear to be a single evolving task.",
    "failure_reason": "<reason>",
    "task_id": None
}
```

Possible runtime reasons:

- `invalid_schema`
- `insufficient_data`
- `low_continuity`
- `context_shift`

## Terminal Behavior

When fail-safe is returned:

- no peak is selected
- no waste is calculated
- no timeline is generated
- no contribution array is exposed
- no RF array is exposed
- no validation debug is exposed
- no algorithm version fields are exposed
- no graph is rendered
- no plot is saved

## CLI Behavior

For invalid executions, all CLI modes render only:

```text
[VERDICT]
No clear execution pattern detected.

[WHY]
This does not appear to be a single evolving task.
```

This applies to:

```bash
python -m cli.main invalid.json
python -m cli.main invalid.json --analysis
python -m cli.main invalid.json --debug
python -m cli.main invalid.json --plot
```

`--plot` does not save a plot for invalid executions.

## UI Adapter Behavior

Invalid UI display payload:

```json
{
  "is_valid": false,
  "headline_verdict": "No clear execution pattern detected.",
  "core_insight": "This does not appear to be a single evolving task."
}
```

The UI adapter omits `failure_reason` in invalid display payloads.

## SDK Boundary Behavior

Top-level schema errors are not fail-safe:

```python
from veloryn.xray import analyze_structured

analyze_structured({"steps": [{"output": None}, {"output": "b"}]})
```

raises `ValueError`.

Malformed task/step objects inside a list can return fail-safe with `invalid_schema`.

Execution invalidity returns fail-safe.

## Isolation Test

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
assert "timeline" not in result
assert "analysis" not in result
```
