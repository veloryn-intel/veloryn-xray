from __future__ import annotations

from typing import Iterable, List, Sequence


def tokenize(text: str) -> List[str]:
    return text.lower().split()


def overlap_ratio(current_tokens: Sequence[str], previous_tokens: Sequence[str]) -> float:
    if not current_tokens:
        return 0.0
    previous_vocabulary = set(previous_tokens)
    overlap_count = sum(1 for token in current_tokens if token in previous_vocabulary)
    return overlap_count / len(current_tokens)


def contribution(token_count: int, redundancy_factor: float) -> float:
    return token_count * (1 - redundancy_factor)


def normalize_contributions(contributions: Sequence[float]) -> list[float]:
    if not contributions:
        return []

    normalized = list(contributions)
    if len(normalized) == 1:
        return normalized

    first_contribution = normalized[0]
    later_contributions = normalized[1:]
    later_average = sum(later_contributions) / len(later_contributions)
    normalization_factor = later_average / first_contribution if first_contribution else 1.0
    normalization_factor = min(1.0, max(0.65, normalization_factor))
    normalized[0] = first_contribution * normalization_factor

    average_contribution = sum(normalized) / len(normalized)
    epsilon = average_contribution * 0.05
    for index in range(1, len(normalized)):
        normalized[index] = max(normalized[index], epsilon)

    return normalized


def build_contribution_debug(raw_contributions: Sequence[float], normalized_contributions: Sequence[float]) -> list[dict]:
    return [
        {
            "raw_contribution": raw_value,
            "normalized_contribution": normalized_value,
        }
        for raw_value, normalized_value in zip(raw_contributions, normalized_contributions)
    ]


def moving_average(values: Sequence[float], window: int = 2) -> list[float]:
    if not values or window <= 1:
        return list(values)

    averaged = []
    for index in range(len(values)):
        start = max(0, index - window + 1)
        segment = values[start : index + 1]
        averaged.append(sum(segment) / len(segment))
    return averaged


def smoothed_contributions(contributions: Sequence[float]) -> list[float]:
    return moving_average(contributions, window=2)


def peak_step_index(smoothed_values: Sequence[float], contributions: Sequence[float]) -> int:
    if not smoothed_values:
        return 0

    peak_index = max(range(len(smoothed_values)), key=lambda index: smoothed_values[index])
    if peak_index == 0 and len(contributions) > 1 and contributions[1] >= 0.8 * contributions[0]:
        return 1
    return peak_index


def optimal_stop_index(contributions: Sequence[float], threshold: float = 0.85) -> int | None:
    if not contributions:
        return None

    total_contribution = sum(contributions)
    if total_contribution <= 0:
        return None

    target = threshold * total_contribution
    cumulative = 0.0
    for index, value in enumerate(contributions):
        cumulative += value
        if cumulative >= target:
            return index
    return None


def find_collapse_start_index(contributions: Sequence[float], peak_index: int, peak_value: float) -> int | None:
    if peak_value <= 0 or len(contributions) < 2 or peak_index >= len(contributions) - 1:
        return None

    threshold = 0.5 * peak_value
    for index in range(peak_index + 1, len(contributions)):
        if contributions[index] < threshold and contributions[index] < contributions[index - 1]:
            return index
    return None


def linear_slope(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0

    x_values = list(range(1, len(values) + 1))
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(values) / len(values)

    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
    denominator = sum((x - x_mean) ** 2 for x in x_values)
    if denominator == 0:
        return 0.0
    return numerator / denominator


def average_drop_after_peak(contributions: Sequence[float], peak_index: int) -> float:
    post_peak = contributions[peak_index:]
    if len(post_peak) < 2:
        return 0.0

    drops = [post_peak[index - 1] - post_peak[index] for index in range(1, len(post_peak))]
    return sum(drops) / len(drops)


def is_monotonic_decline(values: Sequence[float]) -> bool:
    if len(values) < 2:
        return False
    return all(values[index] <= values[index - 1] for index in range(1, len(values)))


def variance(values: Sequence[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
