from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from langchain_core.documents import Document
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
REFERENCE_URL = "https://api.python.langchain.com/en/latest/langchain/chains/langchain.chains.combine_documents.refine.RefineDocumentsChain.html"
DOCUMENTS = [
    Document(
        page_content=(
            "Incident summary: the payments API experienced intermittent upstream timeouts during peak traffic. "
            "Retry logic reduced user-visible failures but increased queue depth."
        )
    ),
    Document(
        page_content=(
            "Operational detail: workers retried transient 5xx and timeout responses with exponential backoff. "
            "Permanent 4xx responses were logged without retry."
        )
    ),
    Document(
        page_content=(
            "Reliability detail: dead-letter handling captured requests that exceeded retry limits. "
            "Dashboards tracked queue depth, retry counts, and final failure rates."
        )
    ),
    Document(
        page_content=(
            "Follow-up detail: the team added alerts for queue growth and documented rollback procedures "
            "for disabling retries when upstream instability persisted."
        )
    ),
]


def run_workflow(model: str = MODEL) -> list[dict]:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    llm = ChatOpenAI(model=model, temperature=0)
    parser = StrOutputParser()

    initial_prompt = ChatPromptTemplate.from_template(
        "Summarize this content for an incident review note:\n\n{context}"
    )
    refine_prompt = ChatPromptTemplate.from_template(
        "Here is the current summary:\n{previous_summary}\n\n"
        "Refine it using the additional context below while keeping it concise and operational:\n\n{context}"
    )

    initial_chain = initial_prompt | llm | parser
    refine_chain = refine_prompt | llm | parser

    steps = []
    summary = initial_chain.invoke({"context": DOCUMENTS[0].page_content}).strip()
    steps.append({"step": 1, "phase": "initial_summary", "model": model, "output": summary})

    for document in DOCUMENTS[1:]:
        summary = refine_chain.invoke(
            {
                "previous_summary": summary,
                "context": document.page_content,
            }
        ).strip()
        steps.append(
            {
                "step": len(steps) + 1,
                "phase": "refine_summary",
                "model": model,
                "output": summary,
            }
        )

    return [
        {
            "example": "langchain_official_summarization_refinement",
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
