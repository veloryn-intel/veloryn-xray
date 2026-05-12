from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from crewai import Agent, Task, Crew, Process, LLM
except ImportError as exc:
    raise SystemExit(
        "Install CrewAI extras with: pip install -e '.[crewai]'\n\n"
        "The CrewAI extra currently supports local repository installs. "
        "PyPI packaging will be included in a future release."
    ) from exc

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray.crewai import XRayCrewAIHandler


HERE = Path(__file__).resolve().parent
TRACE_PATH = HERE / "callback_trace.json"
ANALYSIS_PATH = HERE / "xray_analysis.txt"
MODEL = os.environ.get("XRAY_CREWAI_MODEL", "claude-haiku-4-5-20251001")
BASE_TASK = "queue-based retry strategy for flaky API calls"


def build_crew(model: str = MODEL):
    """Build CrewAI workflow with native LLM configuration."""
    llm = LLM(model=model, temperature=0)
    
    researcher = Agent(
        role="Reliability Systems Researcher",
        goal=f"Research technical approaches and failure semantics for {BASE_TASK}",
        backstory=(
            "Expert at analyzing distributed systems patterns, failure modes, "
            "and retry semantics for infrastructure reliability."
        ),
        llm=llm,
        verbose=True,
    )
    
    drafter = Agent(
        role="Infrastructure Policy Drafter",
        goal="Draft execution policies and retry configuration specifications",
        backstory=(
            "Experienced at translating reliability requirements into "
            "concrete execution policies and operational configurations."
        ),
        llm=llm,
        verbose=True,
    )
    
    reviewer = Agent(
        role="Execution Reviewer",
        goal="Review retry policies for timeout handling and failure escalation paths",
        backstory=(
            "Expert at reviewing infrastructure policies to include "
            "backoff strategies, dead-letter handling, and monitoring constraints."
        ),
        llm=llm,
        verbose=True,
    )
    
    research_task = Task(
        description=(
            f"Research and analyze best practices for {BASE_TASK}. "
            "Focus on: exponential backoff patterns, timeout semantics, "
            "failure classification, queue behavior under load, and retry limits."
        ),
        agent=researcher,
        expected_output=(
            "Technical summary of retry strategy patterns including: "
            "backoff algorithms, timeout constraints, failure categories, "
            "and queue-based execution semantics."
        ),
    )
    
    drafting_task = Task(
        description=(
            "Using the research, draft an infrastructure policy document for "
            f"{BASE_TASK}. Include: retry limits, backoff configuration, "
            "timeout thresholds, and queue semantics."
        ),
        agent=drafter,
        expected_output=(
            "Draft policy document with concrete retry parameters, "
            "timeout values, backoff intervals, and queue configuration."
        ),
    )
    
    review_task = Task(
        description=(
            "Review the draft policy to add: dead-letter queue handling, "
            "failure escalation paths, monitoring constraints, and operational limits. "
            "Preserve existing retry semantics while expanding failure handling."
        ),
        agent=reviewer,
        expected_output=(
            "Reviewed policy document with complete failure handling, "
            "dead-letter semantics, escalation paths, and monitoring configuration."
        ),
    )
    
    crew = Crew(
        agents=[researcher, drafter, reviewer],
        tasks=[research_task, drafting_task, review_task],
        process=Process.sequential,
        verbose=True,
    )
    
    return crew, [research_task, drafting_task, review_task]


def save_cli_analysis() -> str:
    """Run CLI analysis and save output."""
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
    """Run real CrewAI workflow with manual capture."""
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set ANTHROPIC_API_KEY or OPENAI_API_KEY.\n"
            "Default model: claude-haiku-4-5-20251001 (requires ANTHROPIC_API_KEY)\n"
            "Override with XRAY_CREWAI_MODEL for other providers."
        )

    handler = XRayCrewAIHandler()
    crew, tasks = build_crew()

    print("Running CrewAI workflow...")
    print(f"Model: {MODEL}")
    print("-" * 60)
    
    # Execute CrewAI workflow
    crew.kickoff()

    print("-" * 60)
    print("Capturing task outputs...")
    
    # Manual capture - explicit and transparent
    # Extract plain text from TaskOutput objects
    for task in tasks:
        # TaskOutput.raw contains the plain text output
        output_text = task.output.raw if hasattr(task.output, 'raw') else str(task.output)
        handler.capture_output(output_text)

    # Save trace and run analysis
    handler.save_trace(TRACE_PATH)
    print(f"Trace saved: {TRACE_PATH}")
    
    save_cli_analysis()
    print(f"CLI analysis saved: {ANALYSIS_PATH}")

    # SDK replay
    print("-" * 60)
    print("SDK Analysis Result:")
    result = handler.analyze()
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
