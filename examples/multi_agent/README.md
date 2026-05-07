# Multi-Agent Redundancy Example

This example replays a real multi-agent-style workflow trace generated with `gpt-4o-mini`.

Script:

```bash
python examples/multi_agent/multi_agent_redundancy.py
```

Trace:

- [multi_agent_trace.json](./multi_agent_trace.json)

## What It Shows

- planner / executor / reviewer role cycling
- a productive climb before the peak
- later steps that continue the loop without matching earlier contribution

## Expected X-Ray Behavior

- `is_valid: true`
- `peak_step: 3`
- `waste_ratio: 0.4988`
- timeline labels:
  - `improving`
  - `improving`
  - `peak`
  - `declining`
  - `declining`
  - `declining`

Expected verdict:

```text
Execution should have stopped at Step 3.
```

This example demonstrates the core point: more agents does not automatically mean more contribution.
