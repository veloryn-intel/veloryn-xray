# LangChain Official-Pattern Examples

These examples show X-Ray analyzing execution trajectories produced by real LangChain workflows.

Each workflow:

- uses real LangChain primitives
- uses a real OpenAI API call path when regenerated
- commits a deterministic replay fixture
- replays cleanly through the SDK, CLI, and UI

Provider:

- OpenAI
- default model: `gpt-4o-mini`
- override with `XRAY_LANGCHAIN_MODEL`

Workflows:

- [refinement_chain](./refinement_chain/README.md)
- [critique_revision](./critique_revision/README.md)
- [summarization_refinement](./summarization_refinement/README.md)

Common commands:

```bash
python examples/langchain_official/refinement_chain/langchain_official_example.py
python -m cli.main examples/langchain_official/refinement_chain/captured_trace.json
python -m json.tool examples/langchain_official/refinement_chain/captured_trace.json
```

Each workflow directory also includes:

- `captured_trace.json` for deterministic replay
- `xray_analysis.txt` with the committed CLI verdict
- `ui_example.png` showing the trace in the UI
- `original_reference.md` documenting the LangChain source inspiration

Interpretation boundary:

X-Ray analyzes observed execution trajectories only. A peak at the final observed step does not imply that the workflow would remain optimal indefinitely, or that future redundancy would not emerge. It means that, within the captured execution window, structural contribution continued through the final observed step.

Note:

Some LangChain versions emit a Pydantic compatibility warning on Python 3.14+. That warning originates from LangChain internals and does not affect X-Ray trace capture or replay.

Once `captured_trace.json` is committed, replay remains offline and deterministic. Live provider generation may vary slightly over time.
