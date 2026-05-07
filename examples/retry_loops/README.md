# Retry Loop Example

This example replays a real retry workflow trace generated with `gpt-4o-mini`.

The current fixture can be regenerated through [generate_retry_loop_trace.py](./generate_retry_loop_trace.py) and stores its raw provider-backed lineage in:

- [retry_loop_trace.json](./retry_loop_trace.json)
- [retry_loop_live_raw.json](./retry_loop_live_raw.json)

Script:

```bash
python examples/retry_loops/retry_loop.py
```

Optional live-capture refresh:

```bash
python examples/retry_loops/generate_retry_loop_trace.py
```

Optional offline verification:

```bash
python examples/retry_loops/verify_retry_loop_example.py
```

## What It Shows

- repeated retries on the same failing task
- structural repetition after an early useful step
- waste accumulation after the peak

## Current Observed X-Ray Behavior

- `is_valid: true`
- `peak_step: 2`
- CLI waste output: `68%`
- timeline labels:
  - `improving`
  - `peak`
  - `repeating`
  - `repeating`
  - `declining`

Current verdict:

```text
Execution should have stopped at Step 2.
```

This is a strong collapse example: retries continue, but contribution no longer grows.
