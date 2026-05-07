# Refinement Chain

This example demonstrates X-Ray analyzing a real LangChain refinement workflow built with runnable composition.

LangChain primitives used:

- `ChatPromptTemplate`
- `ChatOpenAI`
- `StrOutputParser`
- pipe composition (`prompt | llm | parser`)

Original inspiration:

- [ChatPromptTemplate pattern](./original_reference.md)

Model:

- default: `gpt-4o-mini`
- override with `XRAY_LANGCHAIN_MODEL`

Requirements:

```bash
pip install langchain langchain-openai openai
```

Run:

```bash
python examples/langchain_official/refinement_chain/langchain_official_example.py
```

This live generation path requires `OPENAI_API_KEY`.

Replay through the CLI:

```bash
python -m cli.main examples/langchain_official/refinement_chain/captured_trace.json
```

Validate JSON:

```bash
python -m json.tool examples/langchain_official/refinement_chain/captured_trace.json
```

What X-Ray demonstrates:

- how a real LangChain refinement loop evolves across steps
- where early improvement gives way to diminishing structural change
- how the committed trace replays deterministically once saved

Committed artifacts:

- [captured_trace.json](./captured_trace.json)
- [xray_analysis.txt](./xray_analysis.txt)
- [ui_example.png](./ui_example.png)

Current observed X-Ray output for the committed fixture:

- `peak_step = 1`
- `waste = 83%`
- timeline ends in repeated refinement
