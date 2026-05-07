from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TimelineStep:
    step: int
    label: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "label": self.label,
        }


@dataclass(frozen=True)
class Verdict:
    peak_step: int | None = None
    should_stop_at: int | None = None
    waste_percentage: int | None = None
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.peak_step is not None:
            data["peak_step"] = self.peak_step
        if self.should_stop_at is not None:
            data["should_stop_at"] = self.should_stop_at
        if self.waste_percentage is not None:
            data["waste_percentage"] = self.waste_percentage
        if self.message is not None:
            data["message"] = self.message
        return data


@dataclass(frozen=True)
class Summary:
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AnalysisSignals:
    redundancy_trend: str
    contribution_trend: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "redundancy_trend": self.redundancy_trend,
            "contribution_trend": self.contribution_trend,
        }


@dataclass(frozen=True)
class Analysis:
    signals: AnalysisSignals

    def to_dict(self) -> dict[str, Any]:
        return {
            "signals": self.signals.to_dict(),
        }


@dataclass(frozen=True)
class Meta:
    version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
        }


@dataclass(frozen=True)
class XRayResult:
    is_valid: bool
    verdict: Verdict
    summary: Summary
    meta: Meta
    timeline: list[TimelineStep] | None = None
    analysis: Analysis | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "is_valid": self.is_valid,
            "verdict": self.verdict.to_dict(),
            "summary": self.summary.to_dict(),
            "meta": self.meta.to_dict(),
        }
        if self.timeline is not None:
            data["timeline"] = [step.to_dict() for step in self.timeline]
        if self.analysis is not None:
            data["analysis"] = self.analysis.to_dict()
        return data
