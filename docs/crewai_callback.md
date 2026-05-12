# CrewAI Execution Observer

`XRayCrewAIHandler` is a lightweight execution observer for CrewAI task outputs.

X-Ray captures CrewAI execution outputs and replays them through deterministic execution analysis.

Install the optional CrewAI dependencies:

```bash
pip install -e ".[crewai]"
```

> The CrewAI extra currently supports local repository installs. PyPI packaging will be included in a future release.

```python
from veloryn.xray.crewai import XRayCrewAIHandler

handler = XRayCrewAIHandler()
```

Drop-in usage:

```python
from veloryn.xray.crewai import XRayCrewAIHandler

handler = XRayCrewAIHandler()

crew.kickoff()

for task in tasks:
    handler.capture_output(task.output.raw)

result = handler.analyze()
print(result.to_dict())
```

## What It Does

The handler captures task outputs through explicit manual calls after CrewAI execution completes. It does not capture prompts, tool inputs, memory state, credentials, or provider metadata.

```json
{
  "steps": [
    {"output": "..."},
    {"output": "..."}
  ]
}
```

This is the SDK replay shape used by `handler.analyze()`.

`save_trace(path)` writes the CLI-compatible top-level list format:

```json
[
  {
    "steps": [
      {"output": "..."},
      {"output": "..."}
    ]
  }
]
```

Saved traces are plain JSON. Once a trace is saved, replay remains deterministic for the same X-Ray algorithm versions.

## Architecture

```text
CrewAI runtime
→ manual output capture
→ replay trace
→ X-Ray analysis
```

The handler is a replay adapter. It observes completed task outputs through explicit capture calls and normalizes them into `{"steps": [{"output": "..."}]}` without modifying CrewAI execution.

## API

```python
handler.capture_output(output: str)
handler.get_trace()
handler.save_trace("callback_trace.json")
handler.analyze()
```

`analyze()` replays the captured trace through `veloryn.xray.analyze_structured()`.

## Boundaries

The handler is observational only. It does not infer semantics, reinterpret execution, modify outputs, change ordering, perform continuity analysis, mutate X-Ray signals, or control the CrewAI runtime.

X-Ray analyzes execution trajectories. It does not evaluate correctness or reasoning quality.

This is an execution observer and replay adapter, not a monitoring platform or orchestration framework.

## Integration Pattern

CrewAI currently uses explicit manual capture rather than framework lifecycle callbacks. This preserves transparency and keeps the integration layer thin.

```python
# Explicit capture after task execution
for task in tasks:
    handler.capture_output(task.output.raw)
```

CrewAI tasks return `TaskOutput` objects with multiple attributes (`raw`, `pydantic`, `json_dict`). The handler captures only the `raw` attribute, which contains the plain text output. This ensures:

* JSON serialization compatibility
* Deterministic replay behavior
* No semantic transformation

This pattern:

* maintains observational boundaries
* avoids orchestration takeover
* keeps adapter layer minimal
* preserves framework independence

## Example

See `examples/crewai_callback`.

Real execution artifacts are generated only through live provider-backed execution. Synthetic traces and mocked outputs are intentionally excluded.

```powershell
python examples\crewai_callback\callback_example.py
python -m json.tool examples\crewai_callback\callback_trace.json
python -m cli.main examples\crewai_callback\callback_trace.json
```
