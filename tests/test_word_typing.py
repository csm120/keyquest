import unittest
from unittest import mock

from games.word_typing import WordTypingGame


class _DummySpeech:
    def __init__(self):
        self.messages = []

    def say(self, text, priority=False, protect_seconds=0.0):
        self.messages.append(text)


class _DummyGameState:
    def __init__(self):
        self.mode = "PLAYING"
        self.running = True
        self.game_start_time = 0.0
        self.game_duration = 30.0
        self.warned_10_seconds = False
        self.warned_5_seconds = False
        self.speech = _DummySpeech()
        self.end_called = 0

    def end_game(self):
        self.end_called += 1


class TestWordTypingCountdownAnnouncements(unittest.TestCase):
    def test_ten_and_five_second_warnings_are_announced_once(self):
        state = _DummyGameState()

        with mock.patch("games.word_typing.time.time", return_value=20.0):
            WordTypingGame.update(state, 0.016)
            WordTypingGame.update(state, 0.016)

        self.assertEqual(state.speech.messages.count("10 seconds left!"), 1)
        self.assertTrue(state.warned_10_seconds)

        with mock.patch("games.word_typing.time.time", return_value=25.0):
            WordTypingGame.update(state, 0.016)
            WordTypingGame.update(state, 0.016)

        self.assertEqual(state.speech.messages.count("5 seconds!"), 1)
        self.assertTrue(state.warned_5_seconds)


class TestWordTypingGameplay(unittest.TestCase):
    def _build_game(self):
        spoken = _DummySpeech()
        played = []
        game = WordTypingGame(
            screen=None,
            fonts={"title_font": None, "text_font": None, "small_font": None},
            speech=spoken,
            play_sound_func=lambda sound, *_args, **_kwargs: played.append(sound),
            show_info_dialog_func=lambda *_args, **_kwargs: None,
        )
        return game, spoken, played

    def test_start_playing_announces_word_only(self):
        game, spoken, played = self._build_game()

        with mock.patch("games.word_typing.time.time", return_value=10.0), mock.patch(
            "games.word_typing.random.sample", side_effect=lambda seq, count: list(seq)[:count]
        ), mock.patch("games.word_typing.random.shuffle", side_effect=lambda seq: None):
            game.start_playing()

        self.assertEqual(game.current_word, "cat")
        self.assertEqual(spoken.messages, ["cat"])
        self.assertTrue(played)

    def test_ctrl_space_repeats_word_only(self):
        game, spoken, _played = self._build_game()
        game.mode = "PLAYING"
        game.running = True
        game.current_word = "garden"

        event = type("Event", (), {"key": 32, "unicode": ""})()
        game.handle_game_input(event, 64)

        self.assertEqual(spoken.messages[-1], "garden")

    def test_correct_word_uses_lesson_tone(self):
        game, _spoken, played = self._build_game()
        game.current_word = "cat"
        game.typed_text = "cat"
        game.word_pool = ["cat", "dog"]

        with mock.patch("games.word_typing.audio_manager.AudioManager.make_coin_sound", return_value="lesson-good"):
            game.check_word()

        self.assertEqual(played[0], "lesson-good")

    def test_wrong_word_uses_lesson_bad_tone(self):
        game, spoken, played = self._build_game()
        game.current_word = "cat"
        game.typed_text = "cap"

        with mock.patch("games.word_typing.audio_manager.AudioManager.make_miss_sound", return_value="lesson-bad"):
            game.check_word()

        self.assertEqual(played[0], "lesson-bad")
        self.assertEqual(spoken.messages[-1], "Incorrect. Try again.")


if __name__ == "__main__":
    unittest.main()
