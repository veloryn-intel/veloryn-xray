from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


def main() -> None:
    trace_path = Path(__file__).with_name("retry_loop_trace.json")
    trace = json.loads(trace_path.read_text(encoding="utf-8-sig"))
    payload = trace[0] if isinstance(trace, list) else trace
    result = analyze_structured(payload)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
