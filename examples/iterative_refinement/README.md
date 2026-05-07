# Iterative Refinement Example

This example replays a real OpenAI refinement trace generated with `gpt-4o`.

It demonstrates a multi-step refinement workflow where each step expands or modifies the previous output.

The current fixture can be regenerated through [generate_iterative_refinement_trace.py](./generate_iterative_refinement_trace.py) and stores its raw provider-backed lineage in:

- [iterative_refinement_trace.json](./iterative_refinement_trace.json)
- [iterative_refinement_live_raw.json](./iterative_refinement_live_raw.json)

Script:

```bash
python examples/iterative_refinement/iterative_refinement.py
```

Optional live-capture refresh:

```bash
python examples/iterative_refinement/generate_iterative_refinement_trace.py
```

Optional offline verification:

```bash
python examples/iterative_refinement/verify_iterative_refinement_example.py
```

## What It Shows

- iterative refinement on one evolving topic
- a productive build-up before the peak
- later expansion that adds detail more than new structure

## Current Observed X-Ray Behavior

- `is_valid: true`
- `peak_step: 1`
- CLI waste output: `70%`
- timeline labels:
  - `peak`
  - `declining`
  - `declining`
  - `declining`
  - `declining`

Current verdict:

```text
Execution should have stopped at Step 1.
```
