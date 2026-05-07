from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Anthropic SDK is not installed.") from exc


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL = "claude-sonnet-4-5"
PROMPTS = [
    "Explain transformers simply",
    "Expand explanation",
    "Expand further",
    "Add more detail",
    "Continue expanding",
]
RAW_OUTPUT_PATH = Path(__file__).with_name("claude_refinement_live_raw.json")
EXAMPLE_OUTPUT_PATH = Path(__file__).with_name("claude_refinement_trace.json")


def call_claude(prompt: str, model: str = MODEL) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set.")

    client = Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    finally:
        client.close()


def run_trace() -> list[dict]:
    steps = []
    previous_output = ""

    for index, prompt in enumerate(PROMPTS, start=1):
        full_prompt = f"{previous_output}\n\n{prompt}" if previous_output else prompt
        output = call_claude(full_prompt, model=MODEL)
        steps.append(
            {
                "step": index,
                "prompt": prompt,
                "output": output,
            }
        )
        previous_output = output

    return steps


def save_raw_trace(steps: list[dict]) -> None:
    raw_payload = [
        {
            "scenario": "claude_refinement_live",
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
            "example": "claude_refinement",
            "provider": "Anthropic",
            "model": MODEL,
            "source_fixture": "examples/claude_refinement/claude_refinement_live_raw.json",
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
