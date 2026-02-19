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


if __name__ == "__main__":
    unittest.main()
