import unittest

from modules import phonetics


class TestPhonetics(unittest.TestCase):
    def test_format_needed_keys_for_speech(self):
        text = phonetics.format_needed_keys_for_speech(["a", "1", " "])
        self.assertIn("A, like alpha", text)
        self.assertIn("1, like one", text)

    def test_format_needed_keys_for_display(self):
        text = phonetics.format_needed_keys_for_display(["b", "2"])
        self.assertIn("B (like Bravo)", text)
        self.assertIn("2 (like Two)", text)


if __name__ == "__main__":
    unittest.main()

