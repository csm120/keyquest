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


if __name__ == "__main__":
    unittest.main()

