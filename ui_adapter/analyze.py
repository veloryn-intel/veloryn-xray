from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pattern_extractor.extractor import extract_patterns
from pattern_extractor.verdict import generate_analysis_lines, generate_output


def parse_logs(raw_text: str):
    if not isinstance(raw_text, str) or not raw_text.strip():
        return []

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        return [
            {
                "task_id": "pasted-input",
                "steps": [{"step": index + 1, "output": line} for index, line in enumerate(lines)],
            }
        ]

    if isinstance(payload, dict):
        if "steps" in payload:
            return [payload]
        raise ValueError("Expected an object with a 'steps' field or a list of tasks.")

    if isinstance(payload, list):
        return payload

    raise ValueError("Unsupported input format.")

def build_ui_payload(result: dict) -> dict[str, object]:
    if result.get("is_valid") is False:
        return {
            "is_valid": False,
            "headline_verdict": result.get("headline_verdict", "No clear execution pattern detected."),
            "core_insight": result.get(
                "core_insight",
                "This does not appear to be a single evolving task.",
            ),
        }

    analysis_lines = generate_analysis_lines(result)
    output = generate_output(result)
    return {
        "verdict": output["verdict"],
        "waste": output["waste"],
        "why": output["why"],
        "timeline": result.get("timeline", []),
        "peak_step": result.get("peak_step"),
        "contributions": result.get("contributions", []),
        "rf_version": result.get("rf_version"),
        "rf_token_version": result.get("rf_token_version"),
        "contribution_version": result.get("contribution_version"),
        "validation_version": result.get("validation_version"),
        "tokenizer_version": result.get("tokenizer_version"),
        "validation_debug": result.get("validation_debug"),
        "step_summaries": result.get("step_summaries", []),
        "analysis_lines": analysis_lines,
    }


def build_response_payload(results: list[dict]) -> dict[str, object]:
    if len(results) == 1:
        return build_ui_payload(results[0])

    return {
        "results": [build_ui_payload(result) for result in results],
    }


def main() -> None:
    try:
        raw_request = json.loads(sys.stdin.read() or "{}")
        if isinstance(raw_request, dict) and "input" in raw_request:
            raw_input = raw_request.get("input", "")
            if isinstance(raw_input, dict) and "value" in raw_input:
                raw_input = raw_input["value"]
            raw_text = json.dumps(raw_input) if isinstance(raw_input, (dict, list)) else raw_input
        else:
            raw_text = json.dumps(raw_request)

        logs = parse_logs(raw_text)
        if not logs:
            sys.stdout.write(
                json.dumps(
                    {
                        "is_valid": False,
                        "headline_verdict": "No clear execution pattern detected.",
                        "core_insight": "This does not appear to be a single evolving task.",
                    }
                )
            )
            return

        results = extract_patterns(logs)
        if not results:
            sys.stdout.write(
                json.dumps(
                    {
                        "is_valid": False,
                        "headline_verdict": "No clear execution pattern detected.",
                        "core_insight": "This does not appear to be a single evolving task.",
                    }
                )
            )
            return

        sys.stdout.write(json.dumps(build_response_payload(results)))
    except Exception as error:
        sys.stdout.write(
            json.dumps(
                {
                    "error": True,
                    "message": "Analysis failed.",
                }
            )
        )


if __name__ == "__main__":
    main()
