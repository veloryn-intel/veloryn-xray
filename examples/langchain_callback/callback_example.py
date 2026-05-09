from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
except ImportError as exc:
    raise SystemExit(
        "Install LangChain extras with: pip install 'veloryn-xray[langchain]'"
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray.langchain import XRayCallbackHandler


HERE = Path(__file__).resolve().parent
TRACE_PATH = HERE / "callback_trace.json"
ANALYSIS_PATH = HERE / "xray_analysis.txt"
MODEL = os.environ.get("XRAY_LANGCHAIN_MODEL", "gpt-4o-mini")
BASE_TASK = "Draft an internal engineering note describing a queue-based retry strategy for flaky API calls."
INSTRUCTIONS = [
    "Write the first version of the note.",
    "Refine it with clearer retry steps and limits.",
    "Expand it with backoff and dead-letter handling.",
    "Add monitoring details without changing the topic.",
    "Do one final refinement pass while preserving the structure.",
]


def build_chain(model: str = MODEL):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are generating a stable workflow output for a LangChain callback example. "
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
    return prompt | llm | parser


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
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    handler = XRayCallbackHandler()
    chain = build_chain()

    previous_output = "None"
    for instruction in INSTRUCTIONS:
        previous_output = chain.invoke(
            {
                "base_task": BASE_TASK,
                "previous_output": previous_output,
                "instruction": instruction,
            },
            config={"callbacks": [handler]},
        ).strip()

    handler.save_trace(TRACE_PATH)
    save_cli_analysis()

    result = handler.analyze()
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
