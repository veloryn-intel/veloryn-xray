# CrewAI Execution Observer

This example shows a minimal CrewAI execution observer that records task outputs and replays them through X-Ray.

X-Ray captures CrewAI execution outputs and replays them through deterministic execution analysis.

This is a real CrewAI integration using `Agent`, `Task`, `Crew`, and `Process.sequential`. The observer uses manual capture calls after task execution. Each completed task output is captured in order to an execution trace:

```json
[
  {
    "steps": [
      {"output": "..."}
    ]
  }
]
```

## Minimal Integration

```python
from veloryn.xray.crewai import XRayCrewAIHandler

handler = XRayCrewAIHandler()

# Run your CrewAI workflow
crew.kickoff()

# Manual capture after execution
for task in tasks:
    handler.capture_output(task.output.raw)

result = handler.analyze()
print(result.to_dict())
handler.save_trace("callback_trace.json")
```

## Run

Install the optional CrewAI dependencies:

```bash
pip install -e ".[crewai]"
```

> The CrewAI extra currently supports local repository installs. PyPI packaging will be included in a future release.

Set `ANTHROPIC_API_KEY` before running the live capture. From the repository root:

```powershell
python examples\crewai_callback\callback_example.py
python -m json.tool examples\crewai_callback\callback_trace.json
python -m cli.main examples\crewai_callback\callback_trace.json
```

The example defaults to `claude-haiku-4-5-20251001`. Override the model with `XRAY_CREWAI_MODEL`:

```powershell
$env:XRAY_CREWAI_MODEL = "claude-haiku-4-5-20251001"
```

## Expected Output

Real execution artifacts are generated only through live provider-backed execution. Synthetic traces and mocked outputs are intentionally excluded.

The example prints an SDK result with this shape:

```text
{
  "is_valid": true,
  "verdict": {
    "peak_step": 2,
    "should_stop_at": 2,
    "waste_percentage": 33
  },
  "summary": {
    "reason": "Later steps mostly repeated earlier output."
  }
}
```

The CLI replay prints:

```text
[VERDICT]
Execution should have stopped at Step 2.

[WASTE]
33% of execution happened after that.

[WHY]
Later steps mostly repeated earlier output.

[TIMELINE]
Step 1 → Improving
Step 2 → Peak
Step 3 → Repeating
```

## Saved Trace

`callback_trace.json` is saved as CLI-compatible JSON:

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

The handler keeps the in-memory SDK trace as `{"steps": [{"output": "..."}]}` and writes the top-level list format for CLI replay.

## Scope

X-Ray analyzes execution trajectories from recorded outputs. It does not judge correctness, reasoning quality, or task success.

The handler is observational only. It captures outputs through explicit manual calls, stores them as an execution trace, and replays that trace through the existing SDK analysis path. X-Ray does not modify CrewAI execution.

Live provider runs may produce different outputs and therefore different traces. Once a trace is saved, replay remains deterministic for the same X-Ray algorithm versions.
