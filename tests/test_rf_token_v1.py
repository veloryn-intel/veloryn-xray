from __future__ import annotations

import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pattern_extractor.extractor import extract_patterns
from pattern_extractor.rf_token import RF_TOKEN_VERSION, compute_rf_token_v1, safe_compute_rf_token_v1


class FakeEncoding:
    def __init__(self, mapping=None, error_texts=None):
        self.mapping = mapping or {}
        self.error_texts = set(error_texts or [])

    def encode(self, text):
        if text in self.error_texts:
            raise ValueError("tokenization failed")
        return list(self.mapping.get(text, []))


class RFTokenV1Tests(TestCase):
    def test_identical_inputs(self):
        encoding = FakeEncoding({"same": [1, 2, 2, 3]})
        self.assertEqual(compute_rf_token_v1("same", "same", encoding), 1.0)

    def test_no_overlap(self):
        encoding = FakeEncoding({"curr": [1, 2], "prev": [3, 4]})
        self.assertEqual(compute_rf_token_v1("curr", "prev", encoding), 0.0)

    def test_partial_overlap(self):
        encoding = FakeEncoding({"curr": [1, 1, 2, 3], "prev": [1, 2, 2, 4]})
        self.assertEqual(compute_rf_token_v1("curr", "prev", encoding), 0.5)

    def test_duplicates_are_counted(self):
        encoding = FakeEncoding({"curr": [1, 1, 1, 1], "prev": [1, 1]})
        self.assertEqual(compute_rf_token_v1("curr", "prev", encoding), 0.5)

    def test_empty_inputs(self):
        encoding = FakeEncoding({"curr": [], "prev": [1, 2], "prev_empty": []})
        self.assertEqual(compute_rf_token_v1("curr", "prev", encoding), 0.0)
        self.assertEqual(compute_rf_token_v1("prev", "prev_empty", encoding), 0.0)

    def test_determinism(self):
        encoding = FakeEncoding({"curr": [1, 2, 2, 3], "prev": [2, 2, 3]})
        first = compute_rf_token_v1("curr", "prev", encoding)
        second = compute_rf_token_v1("curr", "prev", encoding)
        self.assertEqual(first, second)

    def test_failure_returns_none_and_flag(self):
        encoding = FakeEncoding(error_texts={"curr"})
        rf, error_flag = safe_compute_rf_token_v1("curr", "prev", encoding)
        self.assertIsNone(rf)
        self.assertTrue(error_flag)

    def test_integration_adds_token_rf_fields(self):
        result = extract_patterns(
            [
                {
                    "task_id": "integration",
                    "steps": [
                        {"step": 1, "output": "hello world"},
                        {"step": 2, "output": "hello world"},
                    ],
                }
            ]
        )[0]

        self.assertEqual(result["rf_token_version"], RF_TOKEN_VERSION)
        self.assertIn("rf_token_v1", result["step_summaries"][0])
        self.assertIn("rf_token_v1", result["step_summaries"][1])
        self.assertEqual(result["step_summaries"][0]["rf_token_v1"], 0.0)
        self.assertEqual(result["step_summaries"][1]["rf_token_v1"], 1.0)

    def test_tokenization_failure_sets_step_flag(self):
        task = {
            "task_id": "failure",
            "steps": [
                {"step": 1, "output": "hello world"},
                {"step": 2, "output": "hello world again"},
            ],
        }

        with patch(
            "pattern_extractor.extractor.token_encoding",
            FakeEncoding(error_texts={"hello world again"}),
        ):
            result = extract_patterns([task])[0]

        self.assertEqual(result["step_summaries"][0]["rf_token_v1"], 0.0)
        self.assertIn("rf_token_error", result["step_summaries"][1])
        self.assertTrue(result["step_summaries"][1]["rf_token_error"])
        self.assertIsNone(result["step_summaries"][1]["rf_token_v1"])
