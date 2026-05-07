from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


EXAMPLE_PATH = Path(__file__).with_name("retry_loop_trace.json")


def main() -> int:
    payload = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or len(payload) != 1:
        raise RuntimeError("Retry loop fixture must be a single-item list.")

    trace = payload[0]
    if trace.get("provider") != "OpenAI":
        raise RuntimeError("Retry loop provider must be 'OpenAI'.")
    if trace.get("model") != "gpt-4o-mini":
        raise RuntimeError("Retry loop model must be 'gpt-4o-mini'.")
    if trace.get("source_fixture") != "examples/retry_loops/retry_loop_live_raw.json":
        raise RuntimeError("Retry loop fixture source path is not self-contained.")

    result = analyze_structured(trace).to_dict()
    if not result["is_valid"]:
        raise RuntimeError("Retry loop fixture should analyze as a valid execution.")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
