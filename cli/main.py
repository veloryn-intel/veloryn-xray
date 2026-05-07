import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pattern_extractor.extractor import extract_patterns
from pattern_extractor.verdict import render_analysis, render_output


def print_cli_error(message: str) -> None:
    print(message, file=sys.stderr)


def selector_aligned_plot_values(contributions: list[float], peak_step: int | None) -> list[float]:
    values = list(contributions)
    if not values or peak_step is None:
        return values

    peak_index = peak_step - 1
    if peak_index < 0 or peak_index >= len(values):
        return values

    max_index = max(range(len(values)), key=lambda index: values[index])
    if max_index == peak_index:
        return values

    # Presentation-only alignment for the Step-1 stabilization override:
    # if Step 2 is selected because it is within 80% of Step 1, flatten the
    # displayed first point to the selected peak so the chart matches the final selector outcome.
    if (
        peak_index == 1
        and max_index == 0
        and len(values) > 1
        and values[1] >= 0.8 * values[0]
    ):
        values[0] = values[1]

    return values


def save_plot(result: dict) -> None:
    import matplotlib.pyplot as plt

    steps = result["steps"]
    contributions = selector_aligned_plot_values(result["contributions"], result["peak_step"])
    peak_step = result["peak_step"]
    peak_value = contributions[peak_step - 1]
    peak_index = peak_step - 1

    analysis_dir = Path("analysis")
    analysis_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    ax.plot(steps[: peak_index + 1], contributions[: peak_index + 1], marker="o", alpha=1.0)
    if peak_index < len(steps) - 1:
        ax.axvspan(peak_step + 1, steps[-1], color="0.92", alpha=0.18, linewidth=0)
        ax.plot(steps[peak_index:], contributions[peak_index:], marker="o", alpha=0.4, linewidth=1.2)
    ax.scatter([peak_step], [peak_value], s=160, color="0.15", zorder=4)
    ax.axvline(x=peak_step, linestyle="--", linewidth=2)
    ax.set_title(f"Peak at Step {peak_step}")
    ax.set_xlabel("Step")
    ax.set_ylabel("Improvement per step")
    ax.set_xticks(steps)
    ax.grid(alpha=0.05, linewidth=0.5)
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(analysis_dir / "plot.png", dpi=300)
    plt.close(fig)
    print("Plot saved at: analysis/plot.png")


def print_step_signals(result: dict) -> None:
    print("----- DEBUG: STEP SIGNALS (peak selection considers overall trajectory, not just the largest single step) -----")
    print()
    print(f"rf_version: {result.get('rf_version', 'unknown')}")
    print(f"rf_token_version: {result.get('rf_token_version', 'unknown')}")
    print(f"contribution_version: {result.get('contribution_version', 'unknown')}")
    print(f"validation_version: {result.get('validation_version', 'unknown')}")
    print(f"tokenizer_version: {result.get('tokenizer_version', 'unknown')}")
    validation_debug = result.get("validation_debug")
    if validation_debug:
        print(f"continuity_score: {validation_debug.get('continuity_score')}")
        print(f"discontinuous_transitions: {validation_debug.get('discontinuous_transitions')}")
        print(f"total_transitions: {validation_debug.get('total_transitions')}")
    print()
    for step_summary in result.get("step_summaries", []):
        rf_token_v1 = step_summary.get("rf_token_v1")
        rf_token_text = "null" if rf_token_v1 is None else f"{rf_token_v1:.2f}"
        rf_diff = step_summary.get("rf_diff")
        rf_diff_text = "null" if rf_diff is None else f"{rf_diff:.2f}"
        print(f"Step {step_summary['step']}:")
        print(f"  redundancy_factor: {step_summary['redundancy_factor']:.2f}")
        print(f"  rf_token_v1: {rf_token_text}")
        print(f"  rf_diff: {rf_diff_text}")
        print(f"  raw_contribution: {step_summary.get('raw_contribution', step_summary['contribution']):.2f}")
        print(f"  normalized_contribution: {step_summary.get('normalized_contribution', step_summary['contribution']):.2f}")
        print(f"  contribution: {step_summary['contribution']:.2f}")
        print()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = sys.argv[1:]
    plot_enabled = False
    analysis_enabled = False
    debug_enabled = False
    if "--plot" in args:
        args = [arg for arg in args if arg != "--plot"]
        plot_enabled = True
    if "--analysis" in args:
        args = [arg for arg in args if arg != "--analysis"]
        analysis_enabled = True
    if "--debug" in args:
        args = [arg for arg in args if arg != "--debug"]
        debug_enabled = True

    if len(args) < 1:
        print("Usage: python -m cli.main <path_to_logs.json>")
        sys.exit(1)

    path = args[0]

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print_cli_error(f"Error: Could not find input file: {path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print_cli_error("Error: Input file is not valid JSON.")
        sys.exit(1)
    except Exception:
        print_cli_error("Error: X-Ray could not read the input file.")
        sys.exit(1)

    results = extract_patterns(data)

    for index, result in enumerate(results, start=1):
        if len(results) > 1:
            print(f"--- Result {index} ---")
        if result.get("is_valid") is False:
            render_output(result)
        elif debug_enabled:
            print_step_signals(result)
        elif analysis_enabled:
            render_analysis(result)
        else:
            render_output(result)
        print()
        if plot_enabled and result.get("is_valid") is True:
            save_plot(result)


if __name__ == "__main__":
    main()
