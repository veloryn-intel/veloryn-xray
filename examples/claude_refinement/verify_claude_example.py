from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


EXAMPLE_PATH = Path(__file__).with_name("claude_refinement_trace.json")


def main() -> int:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise RuntimeError("Claude example fixture must be a single-item list.")

    trace = payload[0]
    if trace.get("provider") != "Anthropic":
        raise RuntimeError("Claude example fixture provider must be 'Anthropic'.")
    if trace.get("model") != "claude-sonnet-4-5":
        raise RuntimeError("Claude example fixture model must be 'claude-sonnet-4-5'.")
    if trace.get("source_fixture") != "examples/claude_refinement/claude_refinement_live_raw.json":
        raise RuntimeError("Claude example fixture source path is not self-contained.")

    result = analyze_structured(trace).to_dict()
    if not result["is_valid"]:
        raise RuntimeError("Claude example fixture should analyze as a valid execution.")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
