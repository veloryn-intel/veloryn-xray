from __future__ import annotations

from typing import Any

from .classifier import classify_pattern
from .features import (
    average_drop_after_peak,
    build_contribution_debug,
    contribution,
    find_collapse_start_index,
    linear_slope,
    normalize_contributions,
    optimal_stop_index,
    overlap_ratio,
    peak_step_index,
    smoothed_contributions,
    tokenize,
)
from .rf_token import (
    RF_TOKEN_VERSION,
    TOKENIZER_VERSION,
    encoding as token_encoding,
    safe_compute_rf_token_v1,
)
from .validator import is_valid_execution_pattern
from .verdict import (
    build_bridge_line,
    build_core_insight,
    build_counterfactual,
    build_headline,
    build_timeline,
    build_waste_line,
    generate_failsafe_output,
)

RF_VERSION = "v1_heuristic"
CONTRIBUTION_VERSION = "v2_softnorm_floor"
VALIDATION_VERSION = "v2_continuity"


def _is_flat_step_list(logs: list[Any]) -> bool:
    if not isinstance(logs, list) or not logs:
        return False

    for item in logs:
        if not isinstance(item, dict):
            return False
        if "steps" in item or "output" not in item:
            return False

    return True


def _build_failsafe_result(
    task: dict[str, Any],
    reason: str,
) -> dict[str, Any]:
    result = generate_failsafe_output(reason)
    result["task_id"] = task.get("task_id")
    return result


def _extract_task(task: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(task, dict):
        return _build_failsafe_result({}, "invalid_schema")

    raw_steps = task.get("steps", [])
    if not isinstance(raw_steps, list):
        return _build_failsafe_result(task, "invalid_schema")

    step_summaries: list[dict[str, Any]] = []
    rf_values: list[float] = []
    contributions: list[float] = []
    token_counts: list[int] = []
    previous_tokens: list[str] = []
    previous_output_text = ""
    extracted_steps: list[dict[str, Any]] = []

    for raw_step in raw_steps:
        if not isinstance(raw_step, dict):
            return _build_failsafe_result(task, "invalid_schema")

        output_text = raw_step.get("output", "")
        if not isinstance(output_text, str) or not output_text.strip():
            return _build_failsafe_result(task, "invalid_schema")

        step_number = len(extracted_steps) + 1
        tokens = tokenize(output_text)
        token_count = len(tokens)
        similarity = overlap_ratio(tokens, previous_tokens) if previous_tokens else 0.0
        is_new_segment = bool(previous_tokens) and similarity < 0.2
        redundancy_factor = 0.0 if is_new_segment else similarity
        contribution_value = contribution(token_count, redundancy_factor)
        rf_token_v1, rf_token_error = safe_compute_rf_token_v1(
            output_text,
            previous_output_text,
            token_encoding,
        )

        token_counts.append(token_count)
        rf_values.append(redundancy_factor)
        contributions.append(contribution_value)
        step_summary = {
            "step": step_number,
            "token_count": token_count,
            "redundancy_factor": redundancy_factor,
            "contribution": contribution_value,
            "new_segment": is_new_segment,
            "rf_token_v1": rf_token_v1,
        }
        if "step" in raw_step:
            step_summary["original_step"] = raw_step["step"]
        if rf_token_v1 is not None:
            step_summary["rf_diff"] = round(rf_token_v1 - redundancy_factor, 6)
        if rf_token_error:
            step_summary["rf_token_error"] = True
        step_summaries.append(step_summary)
        extracted_steps.append(raw_step)
        previous_tokens = tokens
        previous_output_text = output_text

    if len(extracted_steps) < 2:
        return _build_failsafe_result(
            task,
            "insufficient_data",
        )

    total_transitions = len(extracted_steps) - 1
    if total_transitions == 0:
        return _build_failsafe_result(
            task,
            "insufficient_data",
        )

    raw_contributions = list(contributions)
    contributions = normalize_contributions(contributions)
    contribution_debug = build_contribution_debug(raw_contributions, contributions)
    for step_summary, contribution_value, contribution_meta in zip(step_summaries, contributions, contribution_debug):
        step_summary["contribution"] = contribution_value
        step_summary["raw_contribution"] = contribution_meta["raw_contribution"]
        step_summary["normalized_contribution"] = contribution_meta["normalized_contribution"]

    is_valid, reason, validation_debug = is_valid_execution_pattern(
        rf_values,
        contributions,
        [raw_step.get("output", "") for raw_step in extracted_steps],
    )
    if not is_valid:
        return _build_failsafe_result(
            task,
            reason,
        )

    smoothed_values = smoothed_contributions(contributions)
    peak_index = peak_step_index(smoothed_values, contributions)
    peak_step = peak_index + 1
    if peak_step is None:
        return _build_failsafe_result(
            task,
            "insufficient_data",
        )

    peak_value = contributions[peak_index]
    collapse_index = find_collapse_start_index(contributions, peak_index, peak_value)
    collapse_start = collapse_index + 1 if collapse_index is not None else None
    efficiency_index = optimal_stop_index(contributions)
    if efficiency_index is None:
        efficiency_index = peak_index
    efficiency_stop = efficiency_index + 1
    waste_tokens = sum(token_counts[peak_index + 1 :])
    total_tokens = sum(token_counts)
    waste_ratio = waste_tokens / total_tokens if total_tokens else 0.0
    extra_steps = max(len(extracted_steps) - peak_step, 0)
    rf_growth_rate = linear_slope(rf_values)
    avg_drop = average_drop_after_peak(contributions, peak_index)
    post_peak_contributions = contributions[peak_index:]

    pattern_type = classify_pattern(peak_step, waste_ratio, post_peak_contributions, rf_values)
    headline = build_headline(peak_step, waste_ratio)
    core_insight = build_core_insight(peak_step, extra_steps)
    counterfactual = build_counterfactual(efficiency_stop)
    bridge_line = build_bridge_line()
    waste_statement = build_waste_line(waste_ratio)
    timeline = build_timeline(step_summaries, peak_step)

    result = {
        "task_id": task.get("task_id"),
        "total_steps": len(extracted_steps),
        "steps": [summary["step"] for summary in step_summaries],
        "contributions": [round(value, 4) for value in contributions],
        "peak_step": peak_step,
        "peak_value": round(peak_value, 4),
        "smoothed_peak_value": round(smoothed_values[peak_index], 4),
        "collapse_start": collapse_start,
        "efficiency_stop": efficiency_stop,
        "waste_tokens": waste_tokens,
        "waste_ratio": round(waste_ratio, 4),
        "extra_steps": extra_steps,
        "rf_per_step": [round(value, 4) for value in rf_values],
        "rf_growth_rate": round(rf_growth_rate, 4),
        "avg_drop_after_peak": round(avg_drop, 4),
        "pattern_type": pattern_type,
        "is_valid": True,
        "headline_verdict": headline,
        "core_insight": core_insight,
        "counterfactual": counterfactual,
        "bridge_line": bridge_line,
        "waste_statement": waste_statement,
        "timeline": timeline,
        "step_summaries": step_summaries,
        "validation_debug": validation_debug,
        "rf_version": RF_VERSION,
        "rf_token_version": RF_TOKEN_VERSION,
        "contribution_version": CONTRIBUTION_VERSION,
        "validation_version": VALIDATION_VERSION,
        "tokenizer_version": TOKENIZER_VERSION,
    }
    return result


def extract_patterns(logs: list) -> list:
    if isinstance(logs, dict):
        raise ValueError("Expected a list of tasks or a flat list of step outputs.")
    if not isinstance(logs, list):
        raise ValueError("Expected a list of tasks or a flat list of step outputs.")

    if _is_flat_step_list(logs):
        logs = [
            {
                "task_id": None,
                "steps": [
                    {
                        "step": index,
                        "output": step["output"],
                    }
                    for index, step in enumerate(logs, start=1)
                ],
            }
        ]

    return [_extract_task(task) for task in logs]


analyze_task = _extract_task
analyze_tasks = extract_patterns
