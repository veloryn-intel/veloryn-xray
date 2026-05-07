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
                {"output": "a"},
                {"output": "a"},
            ]
        }
    )
    payload = result.to_dict()
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
