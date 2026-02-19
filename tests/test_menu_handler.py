import unittest

from modules import menu_handler


class TestMenuHandler(unittest.TestCase):
    def test_cycle_typing_sound_intensity(self):
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("subtle", "right"), "normal")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("normal", "right"), "strong")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("strong", "right"), "subtle")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("normal", "left"), "subtle")


if __name__ == "__main__":
    unittest.main()
