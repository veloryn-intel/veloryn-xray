# Fail-Safe Example

This example demonstrates deterministic fail-safe enforcement on unrelated fragments.

Script:

```bash
python examples/fail_safe/unrelated_fragments.py
```

Trace:

- [unrelated_fragments.json](./unrelated_fragments.json)

## What It Shows

- shared wording is not enough to establish execution continuity
- invalid execution returns fail-safe
- fail-safe omits timeline and analysis entirely

## Expected X-Ray Behavior

Canonical output shape:

```python
{
    "is_valid": False,
    "verdict": {"message": "No clear execution pattern detected."},
    "summary": {"reason": "This does not appear to be a single evolving task."},
    "meta": {"version": "0.1.0"},
}
```

There is no timeline, no analysis block, and no graph-producing path for this invalid execution.
