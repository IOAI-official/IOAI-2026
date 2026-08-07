"""Regression tests for the submission-output contract in check.py."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("NOTEBOOK_IMAGE", "test-runtime")

import check  # noqa: E402


class ScoreSubmissionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        check.HIDDEN_OBS = root / "observations.json"
        check.HIDDEN_ANSWERS = root / "answers.json"
        check.SUBMISSION_PATH = root / "predictions.json"
        check.REPORT_PATH = root / "report.json"
        check._RUN_MS = 123

        observations = [{"robot_id": robot_id} for robot_id in range(check.NUM_ROBOTS)]
        check.HIDDEN_OBS.write_text(json.dumps(observations))

    def tearDown(self):
        self.temporary.cleanup()

    def write_case(self, predictions, answers):
        check.SUBMISSION_PATH.write_text(json.dumps(predictions))
        check.HIDDEN_ANSWERS.write_text(json.dumps(answers))

    def report(self):
        return json.loads(check.REPORT_PATH.read_text())["report"]

    def assert_presentation_error(self, predictions, answers):
        self.write_case(predictions, answers)
        with self.assertRaises(SystemExit) as raised:
            check.score_submission()
        self.assertEqual(raised.exception.code, 0)
        test = self.report()["tests"][0]
        self.assertEqual(test["verdict"], "PresentationError")
        self.assertEqual(test["score"], 0.0)

    def test_accepts_all_six_actions_including_pickup_and_drop(self):
        actions = [0, 1, 2, 3, 4, 5]
        self.write_case(actions, actions)

        check.score_submission()

        report = self.report()
        self.assertNotIn("score", report["result"])
        self.assertEqual(
            json.loads(report["result"]["message"]),
            {check.GRADE_SPLIT[-1]: 100.0},
        )
        self.assertEqual(report["tests"][0]["verdict"], "OK")
        self.assertEqual(report["tests"][0]["runningTime"], 123)

    def test_monitor_key_follows_the_graded_round(self):
        """Round B must report under "b", not into round A's column."""
        actions = [0, 1, 2, 3, 4, 5]
        self.write_case(actions, actions)
        original = check.GRADE_SPLIT
        self.addCleanup(setattr, check, "GRADE_SPLIT", original)

        for split, key in (("test_leaderboard_a", "a"), ("test_leaderboard_b", "b")):
            with self.subTest(split=split):
                check.GRADE_SPLIT = split
                check.score_submission()
                self.assertEqual(
                    json.loads(self.report()["result"]["message"]),
                    {key: 100.0},
                )

    def test_rejects_action_six(self):
        self.assert_presentation_error([0, 1, 2, 3, 4, 6], [0, 1, 2, 3, 4, 5])

    def test_rejects_non_integer_and_bool_actions(self):
        for invalid in (4.0, "4", True):
            with self.subTest(invalid=invalid):
                self.assert_presentation_error(
                    [0, 1, 2, 3, invalid, 5], [0, 1, 2, 3, 4, 5]
                )

    def test_rejects_wrong_prediction_count(self):
        self.assert_presentation_error([0, 1, 2, 3, 4], [0, 1, 2, 3, 4, 5])

    def test_invalid_hidden_action_is_an_internal_failure(self):
        self.write_case([0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 6])

        with self.assertRaises(SystemExit) as raised:
            check.score_submission()

        self.assertEqual(raised.exception.code, 1)
        self.assertFalse(check.REPORT_PATH.exists())


if __name__ == "__main__":
    unittest.main()
