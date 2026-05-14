# Research Writer Editor

Replay a sequential multi-agent CrewAI workflow through X-Ray.  

This example analyzes execution trajectories produced by a provider-backed CrewAI orchestration workflow captured from a real execution.

## Execution Structure

The workflow replays a sequential coordination pattern consisting of:

- research expansion
- drafting synthesis
- editorial refinement

The trace captures how structural contribution evolves across later coordination phases.

CrewAI primitives used:

- `Agent`
- `Task`
- `Crew`
- `Process.sequential`

Original inspiration:

- [official/community pattern notes](./original_reference.md)

Model:

- default: `gpt-4o-mini`
- override with `XRAY_CREWAI_MODEL`

## Requirements

```bash
pip install crewai openai
```

This example was verified in a Python 3.12 environment.   
Any equivalent environment with CrewAI and OpenAI installed should work.


## Replay

Run the workflow:

```bash
python examples/crewai_official/research_writer_editor/crewai_example.py
```

This live generation path requires `OPENAI_API_KEY`.

Replay through the CLI:

```bash
python -m cli.main examples/crewai_official/research_writer_editor/captured_trace.json
```

Optional JSON validation:

```bash
python -m json.tool examples/crewai_official/research_writer_editor/captured_trace.json
```

## Execution Pattern

The replay demonstrates:

- structural contribution progression across sequential agent coordination
- refinement after peak contribution
- coordination continuity despite declining marginal contribution
- deterministic replay once the trace is committed

Committed artifacts:

- [captured_trace.json](./captured_trace.json)
- [xray_analysis.txt](./xray_analysis.txt)
- [ui_example.png](./ui_example.png)

Replay characteristics for the committed fixture:

- `peak_step = 2`
- `waste = 41%`
- the drafting stage is the productive peak
- the editor stage primarily expands existing material

Note:

Live provider generation may vary over time.   
The committed replay trace remains deterministic once saved.
