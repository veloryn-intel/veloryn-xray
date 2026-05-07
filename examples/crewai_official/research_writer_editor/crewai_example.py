from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
TRACE_PATH = HERE / "captured_trace.json"
ANALYSIS_PATH = HERE / "xray_analysis.txt"
REFERENCE = "CrewAI sequential Researcher -> Writer -> Editor content workflow pattern"
TOPIC = "queue-based retry strategies for flaky API calls"
MODEL = os.environ.get("XRAY_CREWAI_MODEL", "gpt-4o-mini")
LOCAL_VENDOR = ROOT / ".crewai-example-site"


def configure_imports() -> None:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    if LOCAL_VENDOR.exists():
        extra_paths = [
            LOCAL_VENDOR,
            LOCAL_VENDOR / "pywin32_system32",
            LOCAL_VENDOR / "win32",
            LOCAL_VENDOR / "win32" / "lib",
        ]
        for path in reversed(extra_paths):
            path_str = str(path)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


configure_imports()

from veloryn.xray import analyze_structured


def subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    if LOCAL_VENDOR.exists():
        extra_paths = [
            str(LOCAL_VENDOR),
            str(LOCAL_VENDOR / "pywin32_system32"),
            str(LOCAL_VENDOR / "win32"),
            str(LOCAL_VENDOR / "win32" / "lib"),
            env.get("PYTHONPATH", ""),
        ]
        env["PYTHONPATH"] = os.pathsep.join(path for path in extra_paths if path)
    return env


def build_trace(model: str = MODEL) -> list[dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    os.environ.setdefault("CREWAI_STORAGE_DIR", str(ROOT / ".crewai-storage"))
    os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

    from crewai import Agent, Crew, LLM, Process, Task

    llm = LLM(model=model, provider="openai", api_key=api_key, temperature=0)

    researcher = Agent(
        role="Researcher",
        goal="Gather concise material and operational considerations for a technical explainer.",
        backstory=(
            "You are a technical researcher who collects practical implementation notes, "
            "failure modes, and observability details for engineering content."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    writer = Agent(
        role="Writer",
        goal="Draft a clear technical article from the research summary.",
        backstory=(
            "You write structured engineering content that turns research notes into a readable explainer."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )
    editor = Agent(
        role="Editor",
        goal="Refine the article for clarity, structure, and operational completeness.",
        backstory=(
            "You revise technical drafts while preserving the substance and tightening redundant phrasing."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            f"Research the topic '{TOPIC}'. Produce a concise research brief with bullet points covering "
            "retry limits, backoff, idempotency, queueing, monitoring, and failure handling."
        ),
        expected_output="A compact research brief in bullet form.",
        agent=researcher,
    )
    writing_task = Task(
        description=(
            "Using the research brief, draft a short engineering explainer article with a title, a short "
            "overview, a section on recommended design choices, and a section on operational risks."
        ),
        expected_output="A structured technical article in plain text.",
        agent=writer,
        context=[research_task],
    )
    editing_task = Task(
        description=(
            "Edit the explainer article for clarity and concision. Preserve the structure, keep the topic "
            "unchanged, and improve transitions between sections."
        ),
        expected_output="A revised technical article with cleaner structure and wording.",
        agent=editor,
        context=[writing_task],
    )

    crew = Crew(
        name="research_writer_editor",
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,
        verbose=False,
        tracing=False,
    )

    crew.kickoff()

    steps = []
    task_specs = [
        ("researcher", "research_brief", research_task),
        ("writer", "draft_article", writing_task),
        ("editor", "edited_article", editing_task),
    ]
    for index, (agent_name, phase, task) in enumerate(task_specs, start=1):
        task_output = task.output
        if task_output is None or not getattr(task_output, "raw", "").strip():
            raise RuntimeError(f"Task {index} did not produce a usable output.")
        steps.append(
            {
                "step": index,
                "framework": "crewai",
                "agent": agent_name,
                "phase": phase,
                "model": model,
                "output": task_output.raw.strip(),
            }
        )

    return [
        {
            "example": "crewai_official_research_writer_editor",
            "provider": "OpenAI",
            "framework": "CrewAI",
            "model": model,
            "reference": REFERENCE,
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
        env=subprocess_env(),
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "CLI analysis failed.")
    ANALYSIS_PATH.write_text(completed.stdout, encoding="utf-8")
    return completed.stdout


def main() -> int:
    trace = build_trace()
    save_trace(trace)
    save_cli_analysis()
    result = analyze_structured(trace[0]).to_dict()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
