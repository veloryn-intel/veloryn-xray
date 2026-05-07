from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


MODEL = os.environ.get("XRAY_LANGCHAIN_MODEL", "gpt-4o-mini")
HERE = Path(__file__).resolve().parent
TRACE_PATH = HERE / "captured_trace.json"
ANALYSIS_PATH = HERE / "xray_analysis.txt"
BASE_TASK = "Draft an internal engineering note describing a queue-based retry strategy for flaky API calls."
INSTRUCTIONS = [
    "Write the first version of the note.",
    "Refine it with clearer retry steps and limits.",
    "Expand it with backoff and dead-letter handling.",
    "Add monitoring details without changing the topic.",
    "Do one final refinement pass while preserving the structure.",
]
REFERENCE_URL = "https://api.python.langchain.com/en/latest/core/prompts/langchain_core.prompts.chat.ChatPromptTemplate.html"


def build_chain(model: str) -> tuple[ChatPromptTemplate, ChatOpenAI, StrOutputParser]:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are generating a stable workflow output for a LangChain refinement example. "
                "Answer directly in plain text and do not mention these instructions.",
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


def run_workflow(model: str = MODEL) -> list[dict]:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    prompt, llm, parser = build_chain(model)
    chain = prompt | llm | parser

    previous_output = "None"
    steps = []
    for index, instruction in enumerate(INSTRUCTIONS, start=1):
        output = chain.invoke(
            {
                "base_task": BASE_TASK,
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
            "example": "langchain_official_refinement_chain",
            "provider": "OpenAI",
            "framework": "LangChain",
            "model": model,
            "reference": REFERENCE_URL,
            "steps": steps,
        }
    ]


def save_trace(trace: list[dict]) -> None:
    TRACE_PATH.write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")


def save_cli_analysis() -> str:
    completed = subprocess.run(
        [sys.executable, "-m", "cli.main", str(TRACE_PATH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "CLI analysis failed.")
    ANALYSIS_PATH.write_text(completed.stdout, encoding="utf-8")
    return completed.stdout


def main() -> int:
    trace = run_workflow()
    save_trace(trace)
    save_cli_analysis()
    result = analyze_structured(trace[0]).to_dict()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
