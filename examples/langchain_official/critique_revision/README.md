# Critique Revision

This example demonstrates X-Ray analyzing a real LangChain critique and revision workflow.

LangChain primitives used:

- `ChatPromptTemplate`
- `ChatOpenAI`
- `StrOutputParser`
- runnable composition for draft, critique, and revision steps

Original inspiration:

- [ConstitutionalChain pattern](./original_reference.md)

Model:

- default: `gpt-4o-mini`
- override with `XRAY_LANGCHAIN_MODEL`

Requirements:

```bash
pip install langchain langchain-openai openai
```

Run:

```bash
python examples/langchain_official/critique_revision/langchain_official_example.py
```

This live generation path requires `OPENAI_API_KEY`.

Replay through the CLI:

```bash
python -m cli.main examples/langchain_official/critique_revision/captured_trace.json
```

Validate JSON:

```bash
python -m json.tool examples/langchain_official/critique_revision/captured_trace.json
```

What X-Ray demonstrates:

- how critique and revision loops evolve over multiple passes
- whether later critique/revision steps keep adding structure or begin to plateau
- deterministic replay once the live trace is committed

Committed artifacts:

- [captured_trace.json](./captured_trace.json)
- [xray_analysis.txt](./xray_analysis.txt)
- [ui_example.png](./ui_example.png)

Current observed X-Ray output for the committed fixture:

- `peak_step = 5`
- `waste = 0%`
- the workflow keeps improving through the final revision pass

Interpretation note:

This final-step peak is bounded to the captured trace. X-Ray does not infer hypothetical future execution behavior beyond the provided trace. In this example it means structural contribution continued through Step 5 within the observed window, not that additional critique and revision steps would stay productive indefinitely.
