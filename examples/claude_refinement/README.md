# Claude Refinement Example

This example replays a real Claude refinement trace generated with `claude-sonnet-4-5`.

The current fixture was freshly captured through [generate_claude_example_trace.py](./generate_claude_example_trace.py) and saved from the live Anthropic API into:

- [claude_refinement_trace.json](./claude_refinement_trace.json)
- [claude_refinement_live_raw.json](./claude_refinement_live_raw.json)

Script:

```bash
python examples/claude_refinement/claude_refinement.py
```

Optional live-capture refresh:

```bash
python examples/claude_refinement/generate_claude_example_trace.py
```

Optional offline verification:

```bash
python examples/claude_refinement/verify_claude_example.py
```

## What It Shows

- an immediate high-value first response
- later expansion that adds detail but little new structure
- repeated continuation after the peak

## Current Observed X-Ray Behavior

- `is_valid: true`
- `peak_step: 2`
- CLI waste output: `63%`
- timeline labels:
  - `improving`
  - `peak`
  - `repeating`
  - `repeating`
  - `repeating`

Expected verdict:

```text
Execution should have stopped at Step 2.
```
