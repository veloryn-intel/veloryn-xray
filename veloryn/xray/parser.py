from __future__ import annotations

import json
from typing import Any


def parse_raw_input(text: str) -> list[Any]:
    if not isinstance(text, str) or not text.strip():
        return []

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return [{"output": line} for line in lines]

    if isinstance(payload, dict):
        if "steps" in payload:
            return [payload]
        return []

    if isinstance(payload, list):
        return payload

    return []
