import unittest
from unittest.mock import patch

from modules.results_formatter import ResultsFormatter


class TestResultsFormatter(unittest.TestCase):
    def test_format_tutorial_results_contains_totals(self):
        text = ResultsFormatter.format_tutorial_results(
            counts_done={"up": 2, "down": 1, "space": 3},
            friendly_names={"up": "Up Arrow", "down": "Down Arrow", "space": "Space"},
        )
        self.assertIn("Keys Practiced:", text)
        self.assertIn("Up Arrow: 2 times", text)
        self.assertIn("Down Arrow: 1 times", text)
        self.assertIn("Space: 3 times", text)
        self.assertIn("Total: 6 keys pressed correctly!", text)

    def test_format_lesson_results_advance_action(self):
        text, action = ResultsFormatter.format_lesson_results(
            accuracy=95.0,
            wpm=30.0,
            gross_wpm=33.0,
            total_correct=100,
            total_errors=5,
            duration=60.0,
            unlocked_lesson={"name": "Next Lesson", "keys": ["a", "s"]},
            should_advance=True,
        )
        self.assertEqual(action, "advance")
        self.assertIn("Lesson Complete", text)
        self.assertIn("Corrected Words Per Minute: 30.0", text)
        self.assertIn("Total Words Per Minute: 33.0", text)
        self.assertIn("UNLOCKED: Next Lesson", text)
        self.assertIn("Press OK to start the next lesson.", text)

    def test_format_lesson_results_review_action_is_deterministic(self):
        with patch("modules.results_formatter.random.choice", return_value="Keep going"):
            text, action = ResultsFormatter.format_lesson_results(
                accuracy=70.0,
                wpm=10.0,
                gross_wpm=12.0,
                total_correct=50,
                total_errors=20,
                duration=60.0,
                should_review=True,
            )
        self.assertEqual(action, "review")
        self.assertIn("Keep going!", text)
        self.assertIn("Press OK to continue with focused review.", text)


if __name__ == "__main__":
    unittest.main()
