# Real LangChain Integration Example

This example demonstrates X-Ray analyzing a real LangChain iterative refinement workflow using OpenAI models.

It uses actual LangChain primitives:

- `ChatPromptTemplate`
- `ChatOpenAI`
- runnable pipe composition

The script performs a live LangChain execution, stores the resulting trace in [langchain_trace.json](./langchain_trace.json), then runs the X-Ray SDK on the structured trace and prints the deterministic SDK result.

Requirements:

```bash
pip install langchain langchain-openai openai
```

Environment:

```bash
set OPENAI_API_KEY=...
```

Run:

```bash
python examples/langchain/langchain_real_example.py
```

## Note

Some LangChain versions currently emit a Pydantic compatibility warning on Python 3.14+.

This warning originates from LangChain internals and does not affect X-Ray analysis or trace generation.

Replay the stored trace through the CLI:

```bash
python -m cli.main examples/langchain/langchain_trace.json
```

Validate the stored trace JSON:

```bash
python -m json.tool examples/langchain/langchain_trace.json
```

Notes:

- This is a real LangChain integration, not a simulated trace.
- The committed trace file was generated through LangChain execution.
- The stored trace then replays offline through X-Ray deterministically.
