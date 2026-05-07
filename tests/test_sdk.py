from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veloryn.xray import analyze_raw, analyze_structured


class SDKTests(TestCase):
    def test_france_germany_failsafe(self):
        result = analyze_structured(
            {
                "steps": [
                    {"output": "capital of france"},
                    {"output": "capital of germany"},
                ]
            }
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(
            result.to_dict(),
            {
                "is_valid": False,
                "verdict": {"message": "No clear execution pattern detected."},
                "summary": {"reason": "This does not appear to be a single evolving task."},
                "meta": {"version": "0.1.0"},
            },
        )

    def test_reverse_true_refinement_is_valid(self):
        result = analyze_structured(
            {
                "steps": [
                    {"output": "sort descending"},
                    {"output": "use reverse=True"},
                ]
            }
        )

        data = result.to_dict()
        self.assertTrue(result.is_valid)
        self.assertEqual(data["verdict"]["peak_step"], 2)
        self.assertEqual(data["verdict"]["should_stop_at"], 2)
        self.assertEqual(
            [step["label"] for step in data["timeline"]],
            ["improving", "peak"],
        )
        self.assertEqual(
            data["analysis"]["signals"],
            {
                "redundancy_trend": "stable",
                "contribution_trend": "stable",
            },
        )

    def test_repetition_is_valid_and_repeating(self):
        result = analyze_structured(
            {
                "steps": [
                    {"output": "a"},
                    {"output": "a"},
                ]
            }
        )

        data = result.to_dict()
        self.assertTrue(result.is_valid)
        self.assertEqual(data["verdict"]["peak_step"], 1)
        self.assertEqual(data["verdict"]["waste_percentage"], 50)
        self.assertEqual([step["label"] for step in data["timeline"]], ["peak", "repeating"])

    def test_topic_shift_failsafe(self):
        result = analyze_structured(
            {
                "steps": [
                    {"output": "Explain vector databases"},
                    {"output": "Add examples"},
                    {"output": "Now explain blockchain consensus"},
                    {"output": "Expand"},
                ]
            }
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(
            result.to_dict()["summary"]["reason"],
            "This does not appear to be a single evolving task.",
        )

    def test_malformed_structured_schema_raises_value_error(self):
        with self.assertRaises(ValueError):
            analyze_structured({"steps": [{"output": None}]})

        with self.assertRaises(ValueError):
            analyze_structured({"steps": "bad"})

    def test_raw_text_and_structured_are_deterministic(self):
        structured_input = {
            "steps": [
                {"output": "sort descending"},
                {"output": "use reverse=True"},
            ]
        }
        raw_input = "sort descending\nuse reverse=True"

        structured_first = analyze_structured(structured_input).to_dict()
        structured_second = analyze_structured(structured_input).to_dict()
        raw_first = analyze_raw(raw_input).to_dict()
        raw_second = analyze_raw(raw_input).to_dict()

        self.assertEqual(structured_first, structured_second)
        self.assertEqual(raw_first, raw_second)
        self.assertEqual(json.dumps(structured_first), json.dumps(structured_second))

    def test_raw_invalid_input_returns_failsafe(self):
        result = analyze_raw("")
        self.assertFalse(result.is_valid)
        self.assertNotIn("timeline", result.to_dict())
        self.assertNotIn("analysis", result.to_dict())

    def test_sdk_surface_omits_engine_debug_fields(self):
        result = analyze_structured(
            {
                "steps": [
                    {"output": "sort descending"},
                    {"output": "use reverse=True"},
                ]
            }
        ).to_dict()

        forbidden_top_level = {
            "contributions",
            "rf_per_step",
            "rf_growth_rate",
            "avg_drop_after_peak",
            "core_insight",
            "counterfactual",
            "bridge_line",
        }
        for field in forbidden_top_level:
            self.assertNotIn(field, result)

        forbidden_analysis_fields = {
            "total_steps",
            "peak_value",
            "smoothed_peak_value",
            "collapse_start",
            "efficiency_stop",
            "waste_tokens",
            "waste_ratio",
            "extra_steps",
            "pattern_type",
            "contributions",
            "rf_per_step",
            "rf_growth_rate",
            "avg_drop_after_peak",
            "continuity_score",
            "discontinuous_transitions",
            "total_transitions",
            "rf_version",
            "rf_token_version",
            "contribution_version",
            "validation_version",
            "tokenizer_version",
        }
        for field in forbidden_analysis_fields:
            self.assertNotIn(field, result["analysis"]["signals"])
