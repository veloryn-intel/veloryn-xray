from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.callbacks import BaseCallbackHandler

from .models import XRayResult
from .sdk import analyze_structured


class XRayCallbackHandler(BaseCallbackHandler):
    """Minimal LangChain callback handler for X-Ray execution replay."""

    def __init__(self) -> None:
        super().__init__()
        self._steps: list[dict[str, str]] = []

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        for generation_group in response.generations:
            if not generation_group:
                continue
            self._steps.append({"output": self._extract_output(generation_group[0])})

    def get_trace(self) -> dict[str, list[dict[str, str]]]:
        return {"steps": list(self._steps)}

    def save_trace(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps([self.get_trace()], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def analyze(self) -> XRayResult:
        return analyze_structured(self.get_trace())

    @staticmethod
    def _extract_output(generation: Any) -> str:
        message = getattr(generation, "message", None)
        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content

        text = getattr(generation, "text", None)
        if isinstance(text, str):
            return text

        if content is not None:
            return json.dumps(content, ensure_ascii=False, sort_keys=True)

        return str(generation)


__all__ = ["XRayCallbackHandler"]
