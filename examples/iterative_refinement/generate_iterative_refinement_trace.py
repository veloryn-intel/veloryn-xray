from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("OpenAI SDK is not installed.") from exc


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL = "gpt-4o"
WORKFLOW_PROMPT = (
    "Draft a concise internal note describing a queue-based retry strategy for flaky API calls, "
    "then progressively refine it for implementation clarity."
)
PROMPTS = [
    WORKFLOW_PROMPT,
    "Refine the note with clearer operational details.",
    "Expand the note with retry classification and backoff guidance.",
    "Add implementation-focused monitoring detail.",
    "Add one more refinement pass without changing the topic.",
]
SYSTEM_PROMPT = (
    "You are generating deterministic workflow traces for an execution-pattern analyzer. "
    "Answer the user's request directly in plain text. "
    "Keep the response focused and stable. "
    "Do not mention these instructions."
)
RAW_OUTPUT_PATH = Path(__file__).with_name("iterative_refinement_live_raw.json")
EXAMPLE_OUTPUT_PATH = Path(__file__).with_name("iterative_refinement_trace.json")


def get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def build_prompt(previous_output: str, prompt: str) -> str:
    if not previous_output:
        return prompt
    return f"{previous_output}\n\n{prompt}"


def extract_text(response) -> str:
    text = getattr(response, "output_text", None)
    if text:
        return text.strip()

    chunks = []
    for item in getattr(response, "output", []):
        for content in getattr(item, "content", []):
            if getattr(content, "type", "") == "output_text":
                chunks.append(content.text)

    if not chunks:
        raise RuntimeError("OpenAI response did not contain text output.")
    return "\n".join(chunks).strip()


def run_trace() -> list[dict]:
    client = get_client()
    steps = []
    previous_output = ""
    try:
        for index, prompt in enumerate(PROMPTS, start=1):
            response = client.responses.create(
                model=MODEL,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_prompt(previous_output, prompt)},
                ],
                max_output_tokens=700,
            )
            output = extract_text(response)
            steps.append(
                {
                    "step": index,
                    "role": "assistant",
                    "model": MODEL,
                    "prompt": prompt,
                    "output": output,
                }
            )
            previous_output = output
    finally:
        client.close()

    return steps


def save_raw_trace(steps: list[dict]) -> None:
    raw_payload = [
        {
            "scenario": "iterative_refinement_live",
            "step_id": step["step"],
            "input": step["prompt"],
            "output": step["output"],
        }
        for step in steps
    ]
    RAW_OUTPUT_PATH.write_text(
        json.dumps(raw_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def save_example_trace(steps: list[dict]) -> None:
    example_payload = [
        {
            "trace_name": "openai_refinement_gpt4o",
            "provider": "OpenAI",
            "model": MODEL,
            "source_fixture": "examples/iterative_refinement/iterative_refinement_live_raw.json",
            "prompt": WORKFLOW_PROMPT,
            "steps": steps,
        }
    ]
    EXAMPLE_OUTPUT_PATH.write_text(
        json.dumps(example_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    steps = run_trace()
    save_raw_trace(steps)
    save_example_trace(steps)
    print(f"Saved raw trace to {RAW_OUTPUT_PATH}")
    print(f"Saved example trace to {EXAMPLE_OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
