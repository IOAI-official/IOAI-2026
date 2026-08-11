import json
import math
import tempfile
import unittest
from contextlib import chdir
from pathlib import Path
from unittest import mock

import check


class ReportContractTests(unittest.TestCase):
    def write_report(self, *, split, score, verdict="OK", message=""):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report_path = root / "report.json"
            error_path = root / "artifacts" / "field_score-error.txt"
            with chdir(root):
                with (
                    mock.patch.object(check, "GRADE_SPLIT", split),
                    mock.patch.object(check, "REPORT_PATH", Path("report.json")),
                    mock.patch.object(
                        check,
                        "ERROR_TRACE_PATH",
                        Path("artifacts/field_score-error.txt"),
                    ),
                    mock.patch.object(check, "_RUN_MS", 1234),
                ):
                    check.write_report(score=score, verdict=verdict, message=message)
            report = json.loads(report_path.read_text())
            error = error_path.read_text() if error_path.exists() else None
        return report, error

    def assert_calculator_score(self, report, *, key, score):
        result = report["report"]["result"]
        self.assertEqual(set(result), {"message"})
        self.assertEqual(json.loads(result["message"]), {key: score})
        self.assertEqual(report["report"]["tests"][0]["score"], score)

    def test_leaderboard_a_success(self):
        report, error = self.write_report(
            split="leaderboard_a_config",
            score=85.6357,
        )
        self.assert_calculator_score(report, key="a", score=85.6357)
        self.assertEqual(report["report"]["tests"][0]["verdict"], "OK")
        self.assertIsNone(error)

    def test_leaderboard_b_success(self):
        report, error = self.write_report(
            split="leaderboard_b_config",
            score=73.1257,
        )
        self.assert_calculator_score(report, key="b", score=73.1257)
        self.assertIsNone(error)

    def test_participant_failure_publishes_zero_for_active_component(self):
        report, error = self.write_report(
            split="leaderboard_a_config",
            score=0.0,
            verdict="RuntimeError",
            message="student traceback",
        )
        self.assert_calculator_score(report, key="a", score=0.0)
        self.assertEqual(
            report["artifacts"],
            [
                {
                    "testName": "field_score",
                    "testDataType": "ERROR",
                    "path": "artifacts/field_score-error.txt",
                }
            ],
        )
        self.assertEqual(error, "student traceback\n")

    def test_unknown_split_is_rejected(self):
        with mock.patch.object(check, "GRADE_SPLIT", "train_config"):
            with self.assertRaisesRegex(ValueError, "no CALCULATOR component key"):
                check.calculator_result(10.0)

    def test_non_finite_scores_are_rejected(self):
        with mock.patch.object(check, "GRADE_SPLIT", "leaderboard_a_config"):
            for score in (math.nan, math.inf, -math.inf):
                with self.subTest(score=score):
                    with self.assertRaisesRegex(ValueError, "score must be finite"):
                        check.calculator_result(score)


if __name__ == "__main__":
    unittest.main()
