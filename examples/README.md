# Examples

These examples show X-Ray on stored workflow traces.

They are intentionally:

- deterministic
- offline-reproducible
- dependency-light
- focused on execution structure rather than semantic correctness

Every example replays a saved trace through the packaged SDK:

```python
from veloryn.xray import analyze_structured, analyze_raw
```

Replay of committed fixtures does not require live API access. The real workflow traces were generated earlier and committed as JSON fixtures, so replay is local and deterministic.

Some provider-backed examples also include optional capture scripts that regenerate a fixture from a live provider call when credentials are available. Those generation scripts are explicitly marked in the per-example READMEs. Replay remains offline; regeneration is opt-in.

## What These Examples Demonstrate

- retry collapse and repeated reformulation
- refinement loops with visible peak behavior
- multi-agent redundancy after a productive peak
- fail-safe enforcement for unrelated fragments
- minimal SDK integration patterns

## Stored Real Traces

This examples tree includes replay fixtures generated from real API workflows already present in the repository:

- `gpt-4o`
- `gpt-4o-mini`
- `claude-sonnet-4-5`

The committed fixtures replay locally without providers. Some example scripts also include optional live-capture paths for regenerating those fixtures with real providers, but replay itself stays local and deterministic.

## Example Categories

- [retry_loops](./retry_loops/README.md)
- [iterative_refinement](./iterative_refinement/README.md)
- [langchain](./langchain/README.md)
- [langchain_official](./langchain_official/README.md)
- [crewai_official](./crewai_official/README.md)
- [claude_refinement](./claude_refinement/README.md)
- [multi_agent](./multi_agent/README.md)
- [fail_safe](./fail_safe/README.md)
- [sdk](./sdk/README.md)
- [langchain_callback](./langchain_callback/README.md)
- [crewai_callback](./crewai_callback/README.md)

## Provider Matrix

| Example | Provider | Real API fixture | Framework |
| --- | --- | --- | --- |
| `retry_loops` | OpenAI live-captured fixture | yes | none |
| `iterative_refinement` | OpenAI live-captured fixture | yes | none |
| `langchain` | OpenAI live-captured fixture | yes | LangChain |
| `langchain_official/refinement_chain` | OpenAI live-captured fixture | yes | LangChain |
| `langchain_official/critique_revision` | OpenAI live-captured fixture | yes | LangChain |
| `langchain_official/summarization_refinement` | OpenAI live-captured fixture | yes | LangChain |
| `crewai_official/research_writer_editor` | OpenAI live-captured fixture | yes | CrewAI |
| `claude_refinement` | Anthropic live-captured fixture | yes | none |
| `multi_agent` | stored workflow trace | no | none |
| `fail_safe` | canonical invalid fixture | no | none |

## Quick Commands

Replay a committed fixture through the CLI:

```bash
python -m cli.main examples/langchain_official/refinement_chain/captured_trace.json
```

Run a live provider-backed LangChain capture and refresh its committed artifacts:

```bash
python examples/langchain_official/refinement_chain/langchain_official_example.py
```

---
## Quick Start




## Execution Patterns Covered

These examples include replay analysis for:

- retry loops
- iterative reformulation
- multi-agent redundancy
- stagnation patterns
- trajectory collapse
- structural contribution decay
- execution continuation analysis
- fail-safe execution rejection
- execution validity enforcement


## Framework Integrations

Examples currently include:  

- LangChain callback replay
- CrewAI callback replay
- multi-agent execution analysis
- deterministic execution replay
- offline trace inspection

---

## Why The Examples Are Minimal

X-Ray analyzes execution continuity, contribution collapse, and invalid-state isolation.

It does not:

- judge answer correctness
- compare model intelligence
- perform semantic reasoning
- score final-answer quality

The examples keep prompts, outputs, and ordering visible so the execution structure is easy to inspect.

