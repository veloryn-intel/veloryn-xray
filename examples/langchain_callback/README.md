# LangChain Callback Handler

X-Ray captures LangChain execution outputs and replays them through deterministic execution analysis.
The integration does not modify LangChain execution or orchestration behavior.

This example uses:
- `ChatPromptTemplate`
- `ChatOpenAI`
- `StrOutputParser`
- runnable pipe composition
- callback attachment through `chain.invoke(..., config={"callbacks": [handler]})`

The handler uses LangChain's `BaseCallbackHandler` and the stable `on_llm_end` lifecycle hook. 

Each completed assistant output is appended to an execution trace in execution order.

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
from veloryn.xray.langchain import XRayCallbackHandler

handler = XRayCallbackHandler()

chain.invoke(
    {"topic": "Transformers"},
    config={"callbacks": [handler]},
)

result = handler.analyze()
print(result.to_dict())
handler.save_trace("callback_trace.json")
```

## Run

### Local repository development

The LangChain integration is optional and installed through the `langchain` extra.

```bash
pip install -e ".[langchain]"
```

### PyPI install

```bash
pip install "veloryn-xray[langchain]"
```

PyPI optional extras will be available in the next release

Set `OPENAI_API_KEY` before running the live capture. From the repository root:

```powershell
python examples\langchain_callback\callback_example.py
python -m json.tool examples\langchain_callback\callback_trace.json
python -m cli.main examples\langchain_callback\callback_trace.json
```

The example defaults to `gpt-4o-mini`. Override the model with `XRAY_LANGCHAIN_MODEL`:

```powershell
$env:XRAY_LANGCHAIN_MODEL = "gpt-4o-mini"
```

## Expected Output

The example prints an SDK result with this shape:

```text
{
  "is_valid": true,
  "verdict": {
    "peak_step": 1,
    "should_stop_at": 1,
    "waste_percentage": 85
  },
  "summary": {
    "reason": "Later steps mostly repeated earlier output."
  }
}
```

The CLI replay prints:

```text
[VERDICT]
Execution should have stopped at Step 1.

[WASTE]
85% of execution happened after that.

[WHY]
Later steps mostly repeated earlier output.

[TIMELINE]
Step 1 → Peak
Step 2 → Repeating
Step 3 → Repeating
Step 4 → Repeating
Step 5 → Repeating
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

The callback keeps the in-memory SDK trace as `{"steps": [{"output": "..."}]}` and writes the top-level list format for CLI replay.

## Scope

X-Ray analyzes execution trajectories from recorded outputs. It does not judge correctness, reasoning quality, or task success.

The callback handler is passive and observational only. It captures outputs, stores them as an execution trace, and replays that trace through the existing SDK analysis path. X-Ray does not modify LangChain execution.

Live provider runs may produce different outputs and therefore different traces. Once a trace is saved, replay remains deterministic for the same X-Ray algorithm versions.
