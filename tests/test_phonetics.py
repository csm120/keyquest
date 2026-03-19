import unittest

from modules import phonetics


class TestPhonetics(unittest.TestCase):
    def test_format_needed_keys_for_speech(self):
        text = phonetics.format_needed_keys_for_speech(["a", "1", " "])
        self.assertEqual(text, "A, like alpha, 1, Space")

    def test_format_needed_keys_for_display(self):
        text = phonetics.format_needed_keys_for_display(["b", "2"])
        self.assertEqual(text, "B (like Bravo), 2")


if __name__ == "__main__":
    unittest.main()
