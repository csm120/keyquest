import unittest

from modules import menu_handler
from modules.state_manager import Settings


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

    def test_auto_start_next_lesson_explanation(self):
        self.assertIn("automatically", menu_handler.get_auto_start_next_lesson_explanation(True))
        self.assertIn("choice screen", menu_handler.get_auto_start_next_lesson_explanation(False))

    def test_cycle_font_scale_includes_low_vision_sizes(self):
        self.assertEqual(menu_handler.cycle_font_scale("150%", "right"), "175%")
        self.assertEqual(menu_handler.cycle_font_scale("175%", "right"), "200%")
        self.assertEqual(menu_handler.cycle_font_scale("200%", "right"), "auto")

    def test_get_options_items_includes_auto_start_next_lesson(self):
        settings = Settings()
        options = menu_handler.get_options_items(settings)
        self.assertIn("Auto Start Next Lesson: Off", options)

    def test_navigate_first_and_last_helpers(self):
        self.assertEqual(menu_handler.navigate_first(5), 0)
        self.assertEqual(menu_handler.navigate_last(5), 4)

    def test_menu_home_and_end_jump_to_bounds(self):
        spoken = []
        menu = menu_handler.Menu(
            name="Test",
            items=["One", "Two", "Three"],
            speech_system=type("Speech", (), {"say": lambda _self, text, **_kwargs: spoken.append(text)})(),
            on_select_callback=lambda _item: None,
        )
        menu.current_index = 1

        menu.handle_input(type("Event", (), {"key": menu_handler.pygame.K_HOME, "unicode": ""})())
        self.assertEqual(menu.current_index, 0)

        menu.handle_input(type("Event", (), {"key": menu_handler.pygame.K_END, "unicode": ""})())
        self.assertEqual(menu.current_index, 2)

    def test_options_menu_home_and_end_jump_to_bounds(self):
        spoken = []
        options_menu = menu_handler.OptionsMenu(
            name="Options",
            options=[
                {
                    "name": "a",
                    "get_value": lambda: False,
                    "set_value": lambda _v: None,
                    "get_text": lambda: "A",
                    "get_explanation": lambda: "First",
                    "cycle": lambda value, _direction: value,
                },
                {
                    "name": "b",
                    "get_value": lambda: False,
                    "set_value": lambda _v: None,
                    "get_text": lambda: "B",
                    "get_explanation": lambda: "Second",
                    "cycle": lambda value, _direction: value,
                },
                {
                    "name": "c",
                    "get_value": lambda: False,
                    "set_value": lambda _v: None,
                    "get_text": lambda: "C",
                    "get_explanation": lambda: "Third",
                    "cycle": lambda value, _direction: value,
                },
            ],
            speech_system=type("Speech", (), {"say": lambda _self, text, **_kwargs: spoken.append(text)})(),
            on_change_callback=lambda *_args: None,
        )
        options_menu.current_index = 1

        options_menu.handle_input(type("Event", (), {"key": menu_handler.pygame.K_HOME})())
        self.assertEqual(options_menu.current_index, 0)

        options_menu.handle_input(type("Event", (), {"key": menu_handler.pygame.K_END})())
        self.assertEqual(options_menu.current_index, 2)


if __name__ == "__main__":
    unittest.main()
