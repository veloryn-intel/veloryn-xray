# Research Writer Editor

This example demonstrates X-Ray analyzing execution trajectories produced by a multi-agent CrewAI workflow.

Workflow shape:

- Researcher gathers operational material
- Writer drafts a technical explainer
- Editor revises the draft for clarity and structure

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

Requirements:

```bash
pip install crewai openai
```

This example was verified in a Python 3.12 environment. Any equivalent environment with CrewAI and OpenAI installed should work.

Run:

```bash
python examples/crewai_official/research_writer_editor/crewai_example.py
```

This live generation path requires `OPENAI_API_KEY`.

Replay through the CLI:

```bash
python -m cli.main examples/crewai_official/research_writer_editor/captured_trace.json
```

Validate JSON:

```bash
python -m json.tool examples/crewai_official/research_writer_editor/captured_trace.json
```

What X-Ray demonstrates:

- how structural contribution evolves across sequential multi-agent stages
- whether a research -> draft -> edit crew keeps adding structure or begins to plateau
- deterministic replay once the committed trace is saved

Committed artifacts:

- [captured_trace.json](./captured_trace.json)
- [xray_analysis.txt](./xray_analysis.txt)
- [ui_example.png](./ui_example.png)

Current observed X-Ray output for the committed fixture:

- `peak_step = 2`
- `waste = 41%`
- the writer stage is the productive peak and the editor stage mostly refines phrasing

Note:

Live provider generation may vary over time. The committed replay trace remains deterministic once saved.
