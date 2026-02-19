import json
import os
import tempfile
import unittest

from modules.state_manager import AppState, ProgressManager, PROGRESS_SCHEMA_VERSION


class TestProgressManager(unittest.TestCase):
    def test_load_sets_current_and_unlocks(self):
        state = AppState()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "progress.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "schema_version": PROGRESS_SCHEMA_VERSION,
                        "current_lesson": 3,
                        "unlocked_lessons": [1, 2],
                        "speech_mode": "tts",
                        "typing_sound_intensity": "strong",
                        "visual_theme": "dark",
                        "sentence_language": "Spanish",
                        "lesson_stars": {"1": 2},
                        "lesson_best_wpm": {"1": 25.5},
                        "lesson_best_accuracy": {"1": 92.0},
                        "earned_badges": ["badge_a"],
                        "owned_items": ["hat"],
                    },
                    f,
                    indent=2,
                )

            ProgressManager(path).load(state, stage_letters_count=50)

        self.assertEqual(state.settings.current_lesson, 3)
        self.assertEqual(state.lesson.stage, 3)
        self.assertIn(0, state.settings.unlocked_lessons)
        self.assertIn(3, state.settings.unlocked_lessons)
        self.assertIn(2, state.settings.unlocked_lessons)
        self.assertEqual(state.settings.speech_mode, "tts")
        self.assertEqual(state.settings.typing_sound_intensity, "strong")
        self.assertEqual(state.settings.visual_theme, "dark")
        self.assertEqual(state.settings.sentence_language, "Spanish")
        self.assertEqual(state.settings.lesson_stars[1], 2)
        self.assertAlmostEqual(state.settings.lesson_best_wpm[1], 25.5)
        self.assertAlmostEqual(state.settings.lesson_best_accuracy[1], 92.0)
        self.assertIn("badge_a", state.settings.earned_badges)
        self.assertIn("hat", state.settings.owned_items)

    def test_load_ignores_invalid_current_lesson(self):
        state = AppState()
        state.settings.current_lesson = 2
        state.lesson.stage = 2

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "progress.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"current_lesson": 999, "unlocked_lessons": [5]}, f)

            ProgressManager(path).load(state, stage_letters_count=10)

        self.assertEqual(state.settings.current_lesson, 2)
        self.assertEqual(state.lesson.stage, 2)
        self.assertIn(0, state.settings.unlocked_lessons)
        self.assertIn(2, state.settings.unlocked_lessons)
        self.assertIn(5, state.settings.unlocked_lessons)

    def test_load_missing_file_resets_to_defaults(self):
        state = AppState()
        state.settings.current_lesson = 7
        state.lesson.stage = 7
        state.settings.unlocked_lessons = {0, 7}
        state.settings.speech_mode = "off"
        state.settings.visual_theme = "light"
        state.settings.sentence_language = "History Facts"

        ProgressManager("this_file_should_not_exist.json").load(state, stage_letters_count=10)

        self.assertEqual(state.settings.current_lesson, 0)
        self.assertEqual(state.lesson.stage, 0)
        self.assertEqual(state.settings.unlocked_lessons, {0})
        self.assertEqual(state.settings.speech_mode, "auto")
        self.assertEqual(state.settings.visual_theme, "auto")
        self.assertEqual(state.settings.sentence_language, "English")

    def test_save_writes_schema_and_keys(self):
        state = AppState()
        state.settings.current_lesson = 4
        state.settings.unlocked_lessons = {0, 4, 2}
        state.settings.earned_badges = {"b1"}
        state.settings.owned_items = {"item_a"}
        state.settings.typing_sound_intensity = "subtle"

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "progress.json")
            ProgressManager(path).save(state)
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)

        self.assertEqual(saved["schema_version"], PROGRESS_SCHEMA_VERSION)
        self.assertEqual(saved["current_lesson"], 4)
        self.assertEqual(saved["typing_sound_intensity"], "subtle")
        self.assertEqual(saved["unlocked_lessons"], [0, 2, 4])
        self.assertEqual(saved["earned_badges"], ["b1"])
        self.assertEqual(saved["owned_items"], ["item_a"])

    def test_default_main_menu_labels_and_order(self):
        state = AppState()
        items = state.menu_items
        self.assertIn("Games: G", items)
        self.assertIn("Quests: Q", items)
        self.assertIn("Pets: P", items)
        self.assertIn("Pet Shop: P", items)
        self.assertIn("Badges: B", items)
        self.assertIn("About: A", items)
        self.assertNotIn("View Quests: V", items)
        self.assertNotIn("View Badges: V", items)

        self.assertLess(items.index("Games: G"), items.index("Quests: Q"))
        self.assertLess(items.index("Quests: Q"), items.index("Pets: P"))
        self.assertLess(items.index("Pets: P"), items.index("Pet Shop: P"))
        self.assertEqual(items[-1], "About: A")


if __name__ == "__main__":
    unittest.main()
