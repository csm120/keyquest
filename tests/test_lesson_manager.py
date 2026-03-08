import unittest

from modules import lesson_manager


class TestLessonData(unittest.TestCase):
    def test_stage_letters_and_names_align(self):
        self.assertEqual(len(lesson_manager.STAGE_LETTERS), len(lesson_manager.LESSON_NAMES))
        self.assertGreater(len(lesson_manager.STAGE_LETTERS), 0)

    def test_stage_zero_contains_space_and_a(self):
        self.assertIn(" ", lesson_manager.STAGE_LETTERS[0])
        self.assertIn("a", lesson_manager.STAGE_LETTERS[0])

    def test_stage_keys_are_nonempty_strings(self):
        for stage_keys in lesson_manager.STAGE_LETTERS:
            self.assertTrue(stage_keys)
            for key in stage_keys:
                self.assertIsInstance(key, str)
                self.assertNotEqual(key, "")

    def test_key_locations_align_with_actual_lessons(self):
        self.assertEqual(lesson_manager.KEY_LOCATIONS[4]["keys"], "j")
        self.assertEqual(lesson_manager.KEY_LOCATIONS[5]["keys"], "k")
        self.assertEqual(lesson_manager.KEY_LOCATIONS[6]["keys"], "l")
        self.assertEqual(lesson_manager.KEY_LOCATIONS[7]["keys"], ";")

    def test_authored_words_and_phrases_only_use_introduced_keys(self):
        for stage, words in lesson_manager.STAGE_WORDS.items():
            for word in words:
                self.assertTrue(
                    lesson_manager.content_uses_only_introduced_keys(stage, word),
                    msg=f"Stage {stage} word uses future keys: {word}",
                )

        for stage, phrases in lesson_manager.STAGE_PHRASES.items():
            for phrase in phrases:
                self.assertTrue(
                    lesson_manager.content_uses_only_introduced_keys(stage, phrase),
                    msg=f"Stage {stage} phrase uses future keys: {phrase}",
                )


if __name__ == "__main__":
    unittest.main()
