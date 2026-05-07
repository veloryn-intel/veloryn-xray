from __future__ import annotations

import sys

HIGH_WASTE = 0.6
MEDIUM_WASTE = 0.35


def build_headline(peak_step: int, waste_ratio: float) -> str:
    if waste_ratio >= HIGH_WASTE:
        return f"Execution stopped improving after Step {peak_step}. The rest was unnecessary."
    if waste_ratio >= MEDIUM_WASTE:
        return f"Execution peaked at Step {peak_step}. Additional steps didn't materially improve the output."
    return "Execution remained productive through most steps."


def build_core_insight(peak_step: int, extra_steps: int) -> str:
    return (
        f"Execution peaked at Step {peak_step}.\n"
        f"You ran {extra_steps} additional steps.\n"
        "They didn't materially improve the output."
    )


def build_counterfactual(efficiency_stop: int) -> str:
    return f"Most of the value was already captured by Step {efficiency_stop}."


def build_bridge_line() -> str:
    return "Later steps added volume, not new information."


def build_waste_line(waste_ratio: float) -> str:
    waste_percent = round(waste_ratio * 100)
    return f"~{waste_percent}% of this run happened after it stopped improving."


def build_timeline_label(
    step: int,
    peak_step: int,
    redundancy_factor: float,
    contribution_value: float,
    max_contribution: float,
) -> str:
    if step == peak_step:
        return "Peak"
    if step < peak_step:
        return "Improving"
    if redundancy_factor > 0.85:
        return "Repeating"
    return "Declining"


def build_timeline(
    step_summaries: list[dict],
    peak_step: int,
) -> list[str]:
    timeline = []
    max_contribution = max((summary["contribution"] for summary in step_summaries), default=0.0)
    for summary in step_summaries:
        label = build_timeline_label(
            step=summary["step"],
            peak_step=peak_step,
            redundancy_factor=summary["redundancy_factor"],
            contribution_value=summary["contribution"],
            max_contribution=max_contribution,
        )
        timeline.append(f"Step {summary['step']} → {label}")
    return timeline


def build_why_line(result: dict) -> str:
    waste_ratio = result["waste_ratio"]
    if waste_ratio >= HIGH_WASTE:
        return "Later steps mostly repeated earlier output."
    if waste_ratio >= MEDIUM_WASTE:
        return "Later steps added detail, not new information."
    return "Most value was captured early."


def generate_output(result: dict) -> dict[str, str]:
    peak = result["peak_step"]
    waste_ratio = result["waste_ratio"]

    verdict = f"Execution should have stopped at Step {peak}."
    waste = f"{round(waste_ratio * 100)}% of execution happened after that."
    why = build_why_line(result)

    return {
        "verdict": verdict,
        "waste": waste,
        "why": why,
    }


def generate_failsafe_output(reason) -> dict:
    return {
        "is_valid": False,
        "headline_verdict": "No clear execution pattern detected.",
        "core_insight": "This does not appear to be a single evolving task.",
        "failure_reason": reason,
    }


def generate_failsafe_lines(result: dict) -> list[str]:
    return [
        "[VERDICT]",
        result.get("headline_verdict", "No clear execution pattern detected."),
        "",
        "[WHY]",
        result.get("core_insight", "This does not appear to be a single evolving task."),
    ]


def generate_analysis_lines(result: dict) -> list[str]:
    if result.get("is_valid") is False:
        return generate_failsafe_lines(result)

    lines = []
    lines.append("[ANALYSIS]")

    peak = result.get("peak_step")
    waste_ratio = result.get("waste_ratio")

    validation_debug = result.get("validation_debug")
    if validation_debug is None:
        validation_debug = {}
    continuity_score = validation_debug.get("continuity_score", 0)
    discontinuous_transitions = validation_debug.get("discontinuous_transitions")
    total_transitions = validation_debug.get("total_transitions")

    if peak:
        lines.append("")
        lines.append(f"Peak at Step {peak}.")

    if waste_ratio is not None:
        lines.append("")
        lines.append(f"Post-peak waste: {round(waste_ratio * 100)}%.")

    lines.append("")
    lines.append(f"Continuity score: {continuity_score:.2f}")

    contributions = result.get("contributions", [])
    if contributions and peak and peak < len(contributions):
        post_peak = contributions[peak:]
        lines.append("")
        if post_peak:
            if max(post_peak) < contributions[peak - 1]:
                lines.append("Contribution trend: declining after peak")
            else:
                lines.append("Contribution trend: mixed after peak")

    lines.append("")
    lines.append("Signals:")
    lines.append(f"rf_version: {result.get('rf_version')}")
    lines.append(f"rf_token_version: {result.get('rf_token_version')}")
    lines.append(f"contribution_version: {result.get('contribution_version')}")
    lines.append(f"validation_version: {result.get('validation_version')}")
    lines.append(f"tokenizer_version: {result.get('tokenizer_version')}")
    lines.append(f"discontinuous_transitions: {discontinuous_transitions} / {total_transitions}")
    return lines


def render_analysis(result: dict) -> None:
    sys.stdout.write("\n".join(generate_analysis_lines(result)))


def render_output(result: dict, analysis: bool = False) -> None:
    if analysis:
        lines = generate_analysis_lines(result)
        print("\n".join(lines))
        return

    if result.get("is_valid") is False:
        sys.stdout.write("\n".join(generate_failsafe_lines(result)))
        return

    output = generate_output(result)
    lines = [
        "[VERDICT]",
        output["verdict"],
        "",
        "[WASTE]",
        output["waste"],
        "",
        "[WHY]",
        output["why"],
        "",
        "[TIMELINE]",
        *result["timeline"],
        "",
    ]
    sys.stdout.write("\n".join(lines))
