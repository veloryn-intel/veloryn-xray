from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


MODEL = os.environ.get("XRAY_LANGCHAIN_MODEL", "gpt-4o-mini")
TRACE_PATH = Path(__file__).with_name("langchain_trace.json")
PROMPTS = [
    "Draft a concise internal note describing a queue-based retry strategy for flaky API calls.",
    "Refine the note with clearer operational steps for retries and limits.",
    "Expand it with backoff, retry classification, and dead-letter handling.",
    "Add monitoring and alerting details without changing the topic.",
    "Perform one more refinement pass, keeping the same structure and intent.",
]


def build_chain(model: str) -> tuple[ChatPromptTemplate, ChatOpenAI, StrOutputParser]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are generating stable workflow outputs for an execution-trace example. "
                "Answer directly in plain text. Keep the response focused and do not mention these instructions.",
            ),
            (
                "human",
                "Base task:\n{base_task}\n\n"
                "Previous output:\n{previous_output}\n\n"
                "Current refinement instruction:\n{instruction}",
            ),
        ]
    )
    llm = ChatOpenAI(model=model, temperature=0)
    parser = StrOutputParser()
    return prompt, llm, parser


def run_langchain_trace(model: str = MODEL) -> dict:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    prompt, llm, parser = build_chain(model)
    chain = prompt | llm | parser

    previous_output = "None"
    base_task = PROMPTS[0]
    steps = []

    for index, instruction in enumerate(PROMPTS, start=1):
        output = chain.invoke(
            {
                "base_task": base_task,
                "previous_output": previous_output,
                "instruction": instruction,
            }
        ).strip()
        steps.append(
            {
                "step": index,
                "framework": "langchain",
                "model": model,
                "instruction": instruction,
                "output": output,
            }
        )
        previous_output = output

    return [
        {
            "example": "langchain_real_integration",
            "provider": "OpenAI",
            "framework": "LangChain",
            "model": model,
            "source": "live_langchain_execution",
            "steps": steps,
        }
    ]


def save_trace(trace: dict) -> None:
    TRACE_PATH.write_text(
        json.dumps(trace, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    trace = run_langchain_trace()
    save_trace(trace)
    result = analyze_structured(trace[0]).to_dict()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
