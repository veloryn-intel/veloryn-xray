from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_structured


def main() -> None:
    result = analyze_structured(
        {
            "steps": [
                {"output": "sort descending"},
                {"output": "use reverse=True"},
            ]
        }
    )
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
