# LangChain Callback Handler

`XRayCallbackHandler` is a lightweight execution observer for LangChain LLM calls.

X-Ray captures LangChain execution outputs and replays them through deterministic execution analysis.

Install the optional LangChain dependencies.

### Local repository development

```bash
pip install -e ".[langchain]"
```

PyPI install

```bash
pip install "veloryn-xray[langchain]"
```
The optional LangChain extra will be available in the next PyPI release.

```python
from veloryn.xray.langchain import XRayCallbackHandler

callbacks = [XRayCallbackHandler()]
```

Drop-in chain usage:

```python
from veloryn.xray.langchain import XRayCallbackHandler

handler = XRayCallbackHandler()

chain.invoke(
    {"topic": "Transformers"},
    config={"callbacks": [handler]},
)

result = handler.analyze()
print(result.to_dict())
```

## What It Does

The callback captures assistant outputs from LangChain's `on_llm_end` lifecycle hook and stores them in sequential order.   
It does not capture prompts, tool inputs, memory state, credentials, or provider metadata.

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
LangChain runtime
-> callback capture
-> replay trace
-> X-Ray analysis
```

The callback is a replay adapter. It observes completed LLM outputs and normalizes them into `{"steps": [{"output": "..."}]}` without modifying LangChain execution.

## API

```python
handler.get_trace()
handler.save_trace("callback_trace.json")
handler.analyze()
```

`analyze()` replays the captured trace through `veloryn.xray.analyze_structured()`.

## Boundaries

The callback handler is observational only. It does not infer semantics, reinterpret execution, modify outputs, change ordering, perform continuity analysis, mutate X-Ray signals, or control the LangChain runtime.

X-Ray analyzes execution trajectories. It does not evaluate correctness or reasoning quality.

## Example

See `examples/langchain_callback`.

```powershell
python examples\langchain_callback\callback_example.py
python -m json.tool examples\langchain_callback\callback_trace.json
python -m cli.main examples\langchain_callback\callback_trace.json
```
