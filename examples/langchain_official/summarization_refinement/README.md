# Summarization Refinement

This example demonstrates X-Ray analyzing a real LangChain refine-style summarization workflow.

LangChain primitives used:

- `Document`
- `ChatPromptTemplate`
- `ChatOpenAI`
- `StrOutputParser`
- runnable composition for initial summary and refinement steps

Original inspiration:

- [RefineDocumentsChain pattern](./original_reference.md)

Model:

- default: `gpt-4o-mini`
- override with `XRAY_LANGCHAIN_MODEL`

Requirements:

```bash
pip install langchain langchain-openai openai
```

Run:

```bash
python examples/langchain_official/summarization_refinement/langchain_official_example.py
```

This live generation path requires `OPENAI_API_KEY`.

Replay through the CLI:

```bash
python -m cli.main examples/langchain_official/summarization_refinement/captured_trace.json
```

Validate JSON:

```bash
python -m json.tool examples/langchain_official/summarization_refinement/captured_trace.json
```

What X-Ray demonstrates:

- how a refine-style document workflow evolves summary structure over multiple passes
- whether later document passes add meaningful structure or mostly detail
- deterministic replay once the captured trace is committed

Committed artifacts:

- [captured_trace.json](./captured_trace.json)
- [xray_analysis.txt](./xray_analysis.txt)
- [ui_example.png](./ui_example.png)

Current observed X-Ray output for the committed fixture:

- `peak_step = 1`
- `waste = 83%`
- later passes become structurally smaller and eventually repetitive
