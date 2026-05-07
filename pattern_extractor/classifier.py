from __future__ import annotations

from typing import Sequence

from .features import average, is_monotonic_decline, variance


def classify_pattern(
    peak_step: int,
    waste_ratio: float,
    contributions_after_peak: Sequence[float],
    rf_values: Sequence[float],
) -> str:
    if peak_step <= 3 and waste_ratio > 0.4:
        return "early_collapse"

    if is_monotonic_decline(contributions_after_peak):
        return "slow_decay"

    if len(contributions_after_peak) >= 2 and variance(contributions_after_peak) > 0:
        mean = average(contributions_after_peak)
        if mean > 0 and variance(contributions_after_peak) > 0.25 * mean:
            return "unstable"

    if average(rf_values[:3]) > 0.5:
        return "redundant_expansion"

    return "steady"
