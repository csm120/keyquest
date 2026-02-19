import unittest

from modules import lesson_manager
from modules import lesson_mode


class DummyTracker:
    def get_struggling_keys(self):
        return []


class DummyLessonState:
    def __init__(self, stage: int):
        self.stage = stage
        self.tracker = DummyTracker()
        self.review_mode = False
        self.use_words = True
        self.batch_words = []
        self.batch_instructions = []
        self.index = -1
        self.typed = "not-empty"
        self.start_time = None


class DummyState:
    def __init__(self, lesson_state):
        self.lesson = lesson_state


class DummyApp:
    def __init__(self, lesson_state):
        self.state = DummyState(lesson_state)


class TestLessonMode(unittest.TestCase):
    def test_calculate_lesson_stars_early_lessons_accuracy_only(self):
        self.assertEqual(lesson_mode.calculate_lesson_stars(0, 96, 0), 3)
        self.assertEqual(lesson_mode.calculate_lesson_stars(0, 90, 0), 2)
        self.assertEqual(lesson_mode.calculate_lesson_stars(0, 72, 0), 1)
        self.assertEqual(lesson_mode.calculate_lesson_stars(0, 60, 0), 0)

    def test_calculate_lesson_stars_wpm_thresholds(self):
        lesson_num = max(lesson_manager.WPM_REQUIRED_FROM_LESSON, 6)
        self.assertEqual(lesson_mode.calculate_lesson_stars(lesson_num, 95, 30), 3)
        self.assertEqual(lesson_mode.calculate_lesson_stars(lesson_num, 85, 20), 2)
        self.assertEqual(lesson_mode.calculate_lesson_stars(lesson_num, 95, 10), 1)
        self.assertEqual(lesson_mode.calculate_lesson_stars(lesson_num, 60, 50), 0)

    def test_build_lesson_batch_special_key_stage_sets_instructions(self):
        stage = sorted(lesson_manager.SPECIAL_KEY_COMMANDS.keys())[0]
        lesson_state = DummyLessonState(stage)
        app = DummyApp(lesson_state)

        lesson_mode.build_lesson_batch(app)

        commands = lesson_manager.SPECIAL_KEY_COMMANDS[stage]
        expected_words = [cmd[1] for cmd in commands]
        expected_instructions = [cmd[0] for cmd in commands]

        self.assertEqual(lesson_state.batch_words, expected_words)
        self.assertEqual(lesson_state.batch_instructions, expected_instructions)
        self.assertEqual(lesson_state.index, 0)
        self.assertEqual(lesson_state.typed, "")
        self.assertIsInstance(lesson_state.start_time, float)

    def test_build_lesson_batch_early_stage_uses_three_to_four_key_sequences(self):
        lesson_state = DummyLessonState(stage=0)
        app = DummyApp(lesson_state)

        lesson_mode.build_lesson_batch(app)

        self.assertEqual(len(lesson_state.batch_words), lesson_manager.LESSON_BATCH)
        self.assertTrue(all(len(word) in (3, 4) for word in lesson_state.batch_words))


if __name__ == "__main__":
    unittest.main()
