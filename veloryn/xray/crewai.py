from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import XRayResult
from .sdk import analyze_structured


class XRayCrewAIHandler:
    """Minimal CrewAI execution observer for X-Ray replay."""

    def __init__(self) -> None:
        self._steps: list[dict[str, str]] = []

    def capture_output(self, output: str) -> None:
        """Manually capture a task output.
        
        Call this after each CrewAI task execution to record the output.
        """
        self._steps.append({"output": output})

    def get_trace(self) -> dict[str, list[dict[str, str]]]:
        """Return SDK-compatible trace."""
        return {"steps": list(self._steps)}

    def save_trace(self, path: str | Path) -> None:
        """Save CLI-compatible trace."""
        Path(path).write_text(
            json.dumps([self.get_trace()], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def analyze(self) -> XRayResult:
        """Replay trace through X-Ray analysis."""
        return analyze_structured(self.get_trace())


__all__ = ["XRayCrewAIHandler"]
