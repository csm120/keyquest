import unittest

from modules import menu_handler


class TestMenuHandler(unittest.TestCase):
    def test_cycle_typing_sound_intensity(self):
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("subtle", "right"), "normal")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("normal", "right"), "strong")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("strong", "right"), "subtle")
        self.assertEqual(menu_handler.cycle_typing_sound_intensity("normal", "left"), "subtle")

    def test_cycle_bool_toggles_value(self):
        self.assertFalse(menu_handler.cycle_bool(True))
        self.assertTrue(menu_handler.cycle_bool(False))

    def test_focus_assist_explanation(self):
        self.assertIn("stronger panels", menu_handler.get_focus_assist_explanation(True))
        self.assertIn("standard visual emphasis", menu_handler.get_focus_assist_explanation(False))

    def test_cycle_font_scale_includes_low_vision_sizes(self):
        self.assertEqual(menu_handler.cycle_font_scale("150%", "right"), "175%")
        self.assertEqual(menu_handler.cycle_font_scale("175%", "right"), "200%")
        self.assertEqual(menu_handler.cycle_font_scale("200%", "right"), "auto")


if __name__ == "__main__":
    unittest.main()
