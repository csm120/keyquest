import unittest

from modules import lesson_intro_mode
from modules import lesson_manager
from modules import state_manager


class _DummySpeech:
    def __init__(self):
        self.messages = []

    def say(self, text, **_kwargs):
        self.messages.append(text)


class _DummyAudio:
    def __init__(self):
        self.ok_count = 0

    def beep_ok(self):
        self.ok_count += 1


class _DummyApp:
    def __init__(self):
        self.state = state_manager.AppState()
        self.speech = _DummySpeech()
        self.audio = _DummyAudio()
        self.started_lesson = None
        self.menu_announced = False

    def say_menu(self):
        self.menu_announced = True

    def begin_lesson_practice(self, lesson_num: int):
        self.started_lesson = lesson_num


class _Event:
    def __init__(self, key=0, unicode=""):
        self.key = key
        self.unicode = unicode


class TestLessonIntroMode(unittest.TestCase):
    def test_show_lesson_intro_initializes_state_and_speaks(self):
        app = _DummyApp()
        lesson_intro_mode.show_lesson_intro(app, 0)

        self.assertEqual(app.state.mode, "LESSON_INTRO")
        self.assertEqual(app.state.lesson_intro.lesson_num, 0)
        self.assertEqual(app.state.lesson_intro.required_keys, set(lesson_manager.KEY_LOCATIONS[0]["keys"].lower()))
        self.assertTrue(app.speech.messages)

    def test_handle_lesson_intro_input_finds_key_and_starts_lesson(self):
        app = _DummyApp()
        lesson_intro_mode.show_lesson_intro(app, 0)

        lesson_intro_mode.handle_lesson_intro_input(app, _Event(unicode="a"), mods=0)

        self.assertEqual(app.audio.ok_count, 1)
        self.assertEqual(app.started_lesson, 0)


if __name__ == "__main__":
    unittest.main()

