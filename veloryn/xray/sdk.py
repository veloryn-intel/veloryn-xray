from __future__ import annotations

import re
from typing import Any

from pattern_extractor.extractor import extract_patterns
from pattern_extractor.verdict import generate_output

from .models import Analysis, AnalysisSignals, Meta, Summary, TimelineStep, Verdict, XRayResult
from .parser import parse_raw_input
from .version import __version__

FAILSAFE_MESSAGE = "No clear execution pattern detected."
FAILSAFE_REASON = "This does not appear to be a single evolving task."
_TIMELINE_PATTERN = re.compile(r"^Step\s+(?P<step>\d+)\s+.*?\s+(?P<label>[A-Za-z]+)$")
_CANONICAL_LABELS = {
    "improving",
    "peak",
    "declining",
    "repeating",
}


def _validate_structured_schema(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise ValueError("Structured input must be a dict.")
    if "steps" not in data:
        raise ValueError("Structured input must contain 'steps'.")
    steps = data["steps"]
    if not isinstance(steps, list):
        raise ValueError("'steps' must be a list.")

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            raise ValueError(f"Step {index} must be a dict.")
        if "output" not in step:
            raise ValueError(f"Step {index} must contain 'output'.")
        if not isinstance(step["output"], str):
            raise ValueError(f"Step {index} 'output' must be a string.")


def _failsafe_result() -> XRayResult:
    return XRayResult(
        is_valid=False,
        verdict=Verdict(message=FAILSAFE_MESSAGE),
        summary=Summary(reason=FAILSAFE_REASON),
        meta=Meta(version=__version__),
    )


def _normalize_timeline_step(timeline_entry: str) -> TimelineStep:
    match = _TIMELINE_PATTERN.match(timeline_entry.strip())
    if match is None:
        raise ValueError(f"Unsupported timeline entry: {timeline_entry!r}")

    step = int(match.group("step"))
    label = match.group("label").lower()
    if label not in _CANONICAL_LABELS:
        raise ValueError(f"Unsupported timeline label: {label!r}")
    return TimelineStep(step=step, label=label)


def _trend_from_growth(value: float, *, positive: str, negative: str, stable: str = "stable") -> str:
    if value > 0.0001:
        return positive
    if value < -0.0001:
        return negative
    return stable


def _contribution_trend(engine_result: dict[str, Any]) -> str:
    avg_drop = float(engine_result.get("avg_drop_after_peak", 0.0))
    return _trend_from_growth(avg_drop, positive="decreasing", negative="increasing")


def _redundancy_trend(engine_result: dict[str, Any]) -> str:
    rf_growth = float(engine_result.get("rf_growth_rate", 0.0))
    return _trend_from_growth(rf_growth, positive="increasing", negative="decreasing")


def _map_result(engine_result: dict[str, Any]) -> XRayResult:
    if engine_result.get("is_valid") is False:
        return _failsafe_result()

    output = generate_output(engine_result)
    timeline = [
        _normalize_timeline_step(entry)
        for entry in engine_result.get("timeline", [])
    ]

    analysis = Analysis(
        signals=AnalysisSignals(
            redundancy_trend=_redundancy_trend(engine_result),
            contribution_trend=_contribution_trend(engine_result),
        ),
    )

    return XRayResult(
        is_valid=True,
        verdict=Verdict(
            peak_step=int(engine_result["peak_step"]),
            should_stop_at=int(engine_result["peak_step"]),
            waste_percentage=round(float(engine_result["waste_ratio"]) * 100),
        ),
        summary=Summary(reason=output["why"]),
        timeline=timeline,
        analysis=analysis,
        meta=Meta(version=__version__),
    )


def analyze_structured(data: dict) -> XRayResult:
    _validate_structured_schema(data)
    engine_result = extract_patterns([data])[0]
    return _map_result(engine_result)


def analyze_raw(text: str) -> XRayResult:
    logs = parse_raw_input(text)
    if not logs:
        return _failsafe_result()

    try:
        results = extract_patterns(logs)
    except ValueError:
        return _failsafe_result()

    if not results:
        return _failsafe_result()

    return _map_result(results[0])
