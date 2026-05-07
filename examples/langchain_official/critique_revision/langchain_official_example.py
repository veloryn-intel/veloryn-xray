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
QUERY = "Write a concise operational guideline for rotating API keys in production systems."
REFERENCE_URL = "https://api.python.langchain.com/en/latest/langchain/chains/langchain.chains.constitutional_ai.base.ConstitutionalChain.html"
CRITIQUE_REQUESTS = [
    "Critique the response for missing rollback or access-control details.",
    "Critique the revised response for missing monitoring or incident-response details.",
]
REVISION_REQUESTS = [
    "Revise the response to address the critique while keeping it concise and operational.",
    "Revise the response again to address the critique while preserving structure.",
]


def run_workflow(model: str = MODEL) -> list[dict]:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    llm = ChatOpenAI(model=model, temperature=0)
    parser = StrOutputParser()

    draft_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You write concise infrastructure guidance. Respond in plain text."),
            ("human", "{query}"),
        ]
    )
    critique_prompt = ChatPromptTemplate.from_template(
        "Critique this response according to the critique request.\n\n"
        "Query: {query}\n\n"
        "Response: {response}\n\n"
        "Critique request: {critique_request}"
    )
    revision_prompt = ChatPromptTemplate.from_template(
        "Revise this response according to the critique and revision request.\n\n"
        "Query: {query}\n\n"
        "Response: {response}\n\n"
        "Critique request: {critique_request}\n\n"
        "Critique: {critique}\n\n"
        "Revision request: {revision_request}"
    )

    draft_chain = draft_prompt | llm | parser
    critique_chain = critique_prompt | llm | parser
    revision_chain = revision_prompt | llm | parser

    steps = []
    response = draft_chain.invoke({"query": QUERY}).strip()
    steps.append({"step": 1, "phase": "draft", "model": model, "output": response})

    for index, (critique_request, revision_request) in enumerate(zip(CRITIQUE_REQUESTS, REVISION_REQUESTS), start=1):
        critique = critique_chain.invoke(
            {
                "query": QUERY,
                "response": response,
                "critique_request": critique_request,
            }
        ).strip()
        steps.append(
            {
                "step": len(steps) + 1,
                "phase": f"critique_{index}",
                "model": model,
                "output": critique,
            }
        )

        response = revision_chain.invoke(
            {
                "query": QUERY,
                "response": response,
                "critique_request": critique_request,
                "critique": critique,
                "revision_request": revision_request,
            }
        ).strip()
        steps.append(
            {
                "step": len(steps) + 1,
                "phase": f"revision_{index}",
                "model": model,
                "output": response,
            }
        )

    return [
        {
            "example": "langchain_official_critique_revision",
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
