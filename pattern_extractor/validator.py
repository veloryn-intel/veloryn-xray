from __future__ import annotations

import re

VALIDATION_CONFIG = {
    "LOW_OVERLAP_THRESHOLD": 0.25,
    "MIN_DISCONTINUOUS_STEPS": 3,
    "STRONG_CONTINUITY_THRESHOLD": 0.40,
    "ABRUPT_DROP_LOW_THRESHOLD": 0.18,
    "ABRUPT_DROP_DELTA": 0.25,
    "LOW_CONTINUITY_AVERAGE_THRESHOLD": 0.30,
    "MIN_TRANSITIONS": 3,
}

CONTENT_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "being",
    "but",
    "by",
    "can",
    "common",
    "commonly",
    "components",
    "could",
    "did",
    "do",
    "does",
    "done",
    "each",
    "else",
    "example",
    "examples",
    "for",
    "from",
    "high",
    "how",
    "if",
    "in",
    "include",
    "includes",
    "including",
    "into",
    "is",
    "it",
    "its",
    "key",
    "level",
    "many",
    "may",
    "might",
    "more",
    "most",
    "no",
    "not",
    "of",
    "on",
    "or",
    "other",
    "our",
    "output",
    "outputs",
    "over",
    "points",
    "same",
    "she",
    "should",
    "short",
    "so",
    "some",
    "step",
    "steps",
    "such",
    "than",
    "that",
    "the",
    "their",
    "them",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "to",
    "under",
    "use",
    "used",
    "using",
    "very",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "why",
    "will",
    "with",
    "work",
    "works",
    "would",
    "you",
    "your",
}

STRUCTURAL_CONTINUITY_TOKENS = {
    "answer",
    "answers",
    "capital",
    "question",
    "questions",
    "response",
    "responses",
    "result",
    "results",
    "solution",
    "solutions",
}

OPERATIONAL_REFINEMENT_TOKENS = {
    "add",
    "apply",
    "change",
    "descending",
    "fix",
    "optimize",
    "refactor",
    "remove",
    "reverse",
    "reverse=true",
    "sort",
    "update",
    "use",
    "using",
}


def _raw_tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_+-]+", text.lower())


def _content_tokens(text: str) -> list[str]:
    return [
        token
        for token in _raw_tokens(text)
        if (
            len(token) > 2
            and token not in CONTENT_STOPWORDS
            and token not in STRUCTURAL_CONTINUITY_TOKENS
        )
    ]


def _has_structural_marker(text: str) -> bool:
    return any(
        token in STRUCTURAL_CONTINUITY_TOKENS or re.fullmatch(r"q\d+", token)
        for token in _raw_tokens(text)
    )


def _has_meaningful_content(step_outputs: list[str]) -> bool:
    return any(_content_tokens(output_text) for output_text in step_outputs)


def _is_concise_two_step_refinement(step_outputs: list[str]) -> bool:
    if len(step_outputs) != 2:
        return False
    if any(_has_structural_marker(output_text) for output_text in step_outputs):
        return False
    has_operational_marker = any(
        token in OPERATIONAL_REFINEMENT_TOKENS
        for output_text in step_outputs
        for token in _raw_tokens(output_text)
    )
    return has_operational_marker and all(
        len(_content_tokens(output_text)) <= 2 for output_text in step_outputs
    )


def _content_overlap_ratio(current_text: str, previous_text: str) -> float:
    current_tokens = _content_tokens(current_text)
    if not current_tokens:
        return 0.0

    previous_vocabulary = set(_content_tokens(previous_text))
    overlap_count = sum(1 for token in current_tokens if token in previous_vocabulary)
    return overlap_count / len(current_tokens)


def compute_content_overlaps(step_outputs):
    overlaps = []
    previous_output = ""

    for output_text in step_outputs:
        if previous_output:
            overlaps.append(_content_overlap_ratio(output_text, previous_output))
        else:
            overlaps.append(0.0)
        previous_output = output_text

    return overlaps


def detect_context_shift(content_overlaps):
    transitions = content_overlaps[1:]
    if len(transitions) < VALIDATION_CONFIG["MIN_TRANSITIONS"]:
        return False

    for index in range(1, len(transitions)):
        previous_overlap = transitions[index - 1]
        current_overlap = transitions[index]
        remaining = transitions[index:]

        abrupt_drop = (
            previous_overlap >= VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"]
            and current_overlap <= VALIDATION_CONFIG["ABRUPT_DROP_LOW_THRESHOLD"]
            and (previous_overlap - current_overlap) >= VALIDATION_CONFIG["ABRUPT_DROP_DELTA"]
        )
        sustained_low_overlap = (
            len(remaining) >= 2
            and sum(
                value < VALIDATION_CONFIG["LOW_OVERLAP_THRESHOLD"] for value in remaining
            ) >= len(remaining) - 1
            and max(remaining) < VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"]
        )

        if abrupt_drop and sustained_low_overlap:
            return True

        topic_replacement = (
            previous_overlap >= VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"]
            and current_overlap <= VALIDATION_CONFIG["ABRUPT_DROP_LOW_THRESHOLD"]
            and (previous_overlap - current_overlap) >= VALIDATION_CONFIG["ABRUPT_DROP_DELTA"]
            and index + 1 < len(transitions)
            and transitions[index + 1] >= VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"]
        )

        if topic_replacement:
            return True

    for index in range(1, len(transitions)):
        prior = transitions[:index]
        remaining = transitions[index:]
        had_valid_continuity = any(
            value >= VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"] for value in prior
        )
        sustained_collapse = (
            len(remaining) >= 2
            and all(value < VALIDATION_CONFIG["LOW_OVERLAP_THRESHOLD"] for value in remaining)
        )
        if had_valid_continuity and sustained_collapse:
            return True

    return False


def _print_validation_debug(
    *,
    avg_content_overlap,
    content_overlaps,
    discontinuous_transitions,
    majority_discontinuous,
    strong_continuity_anchor,
    context_shift,
):
    return None


def _print_failsafe(reason):
    return None


def is_valid_execution_pattern(rf_per_step, contributions, step_outputs=None):
    """
    Determines whether this looks like a single evolving execution.
    Returns (is_valid: bool, reason: str)
    """

    if not rf_per_step or not contributions or not step_outputs:
        total_transitions = 0
        continuity_score = 1.0
        debug_payload = {
            "continuity_score": continuity_score,
            "discontinuous_transitions": 0,
            "total_transitions": total_transitions,
        }
        _print_validation_debug(
            avg_content_overlap=0.0,
            content_overlaps=[],
            discontinuous_transitions=0,
            majority_discontinuous=False,
            strong_continuity_anchor=False,
            context_shift=False,
        )
        _print_failsafe("insufficient_data")
        return False, "insufficient_data", debug_payload

    content_overlaps = compute_content_overlaps(step_outputs)
    transitions = content_overlaps[1:]
    total_transitions = len(transitions)
    avg_content_overlap = sum(transitions) / len(transitions) if transitions else 0.0
    discontinuous_transitions = sum(
        value <= VALIDATION_CONFIG["LOW_OVERLAP_THRESHOLD"] for value in transitions
    )
    continuity_score = 1 - (discontinuous_transitions / total_transitions) if total_transitions else 1.0
    majority_discontinuous = (
        discontinuous_transitions >= VALIDATION_CONFIG["MIN_DISCONTINUOUS_STEPS"]
        and discontinuous_transitions > (len(transitions) / 2)
    )
    strong_continuity_anchor = any(
        value >= VALIDATION_CONFIG["STRONG_CONTINUITY_THRESHOLD"] for value in transitions
    )
    context_shift = detect_context_shift(content_overlaps)
    debug_payload = {
        "continuity_score": round(continuity_score, 4),
        "discontinuous_transitions": discontinuous_transitions,
        "total_transitions": total_transitions,
        "validation_config": VALIDATION_CONFIG,
    }

    fully_discontinuous = (
        total_transitions > 0
        and discontinuous_transitions == total_transitions
        and _has_meaningful_content(step_outputs)
        and not _is_concise_two_step_refinement(step_outputs)
    )
    structural_only_continuity = (
        any(_has_structural_marker(output_text) for output_text in step_outputs)
        and not _has_meaningful_content(step_outputs)
    )

    if fully_discontinuous or structural_only_continuity:
        _print_validation_debug(
            avg_content_overlap=round(avg_content_overlap, 4),
            content_overlaps=[round(value, 4) for value in content_overlaps],
            discontinuous_transitions=discontinuous_transitions,
            majority_discontinuous=majority_discontinuous,
            strong_continuity_anchor=strong_continuity_anchor,
            context_shift=context_shift,
        )
        _print_failsafe("low_continuity")
        return False, "low_continuity", debug_payload

    if (
        majority_discontinuous
        and avg_content_overlap < VALIDATION_CONFIG["LOW_CONTINUITY_AVERAGE_THRESHOLD"]
        and not strong_continuity_anchor
    ):
        _print_validation_debug(
            avg_content_overlap=round(avg_content_overlap, 4),
            content_overlaps=[round(value, 4) for value in content_overlaps],
            discontinuous_transitions=discontinuous_transitions,
            majority_discontinuous=majority_discontinuous,
            strong_continuity_anchor=strong_continuity_anchor,
            context_shift=context_shift,
        )
        _print_failsafe("low_continuity")
        return False, "low_continuity", debug_payload

    if context_shift:
        _print_validation_debug(
            avg_content_overlap=round(avg_content_overlap, 4),
            content_overlaps=[round(value, 4) for value in content_overlaps],
            discontinuous_transitions=discontinuous_transitions,
            majority_discontinuous=majority_discontinuous,
            strong_continuity_anchor=strong_continuity_anchor,
            context_shift=context_shift,
        )
        _print_failsafe("context_shift")
        return False, "context_shift", debug_payload

    return True, "valid", debug_payload
