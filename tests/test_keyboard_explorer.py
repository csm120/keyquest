import unittest

from modules import keyboard_explorer


class TestKeyboardExplorer(unittest.TestCase):
    def test_f_description_includes_home_row_orientation(self):
        text = keyboard_explorer.get_key_description("f")
        self.assertTrue(text.startswith("Letter F. F, like foxtrot."))
        self.assertIn("left pinky should land on A", text)
        self.assertIn("F, like", text)
        self.assertIn("Feel the bump", text)

    def test_j_description_includes_home_row_orientation(self):
        text = keyboard_explorer.get_key_description("j")
        self.assertTrue(text.startswith("Letter J. J, like juliet."))
        self.assertIn("confirm your right hand is on home row", text)
        self.assertIn("J, like", text)
        self.assertIn("Feel the bump", text)


if __name__ == "__main__":
    unittest.main()
