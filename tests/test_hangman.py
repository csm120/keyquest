import unittest

from games.hangman import (
    HangmanGame,
    WORD_BANK,
    build_sentence_practice_items,
    build_spoken_word_progress,
    build_visual_word_progress,
    describe_hangman_stage,
    load_candidate_length_buckets,
    load_candidate_pool,
)


class _DummySpeech:
    last_message = ""

    def say(self, *args, **kwargs):
        if args:
            self.last_message = str(args[0])
        return None


class TestHangmanGuessAccounting(unittest.TestCase):
    def _build_game(self):
        game = HangmanGame(
            screen=None,
            fonts={"title_font": None, "text_font": None, "small_font": None},
            speech=_DummySpeech(),
            play_sound_func=lambda *_args, **_kwargs: None,
            show_info_dialog_func=lambda *_args, **_kwargs: None,
        )
        game.mode = "PLAYING"
        game.running = True
        game.word = "tomorrow"
        game.word_definition = "The day after today."
        game.guessed_letters = set()
        game.max_wrong = 10
        game.remaining_guesses = 10
        game.wrong_guesses = 0
        game.correct_guesses = 0
        game.guess_attempts = 0
        game.repeated_guesses = 0
        return game

    def test_correct_guess_does_not_reduce_remaining(self):
        game = self._build_game()
        game.process_guess("t")
        self.assertEqual(game.remaining_guesses, 10)
        self.assertEqual(game.wrong_guesses, 0)

    def test_wrong_guess_reduces_remaining_once(self):
        game = self._build_game()
        game.process_guess("z")
        self.assertEqual(game.remaining_guesses, 9)
        self.assertEqual(game.wrong_guesses, 1)

    def test_repeated_guess_has_no_penalty(self):
        game = self._build_game()
        game.process_guess("t")
        game.process_guess("t")
        self.assertEqual(game.remaining_guesses, 10)
        self.assertEqual(game.wrong_guesses, 0)

    def test_sentence_ctrl_space_announces_remaining_text_style(self):
        game = self._build_game()
        game.mode = "SENTENCE_PRACTICE"
        game.sentence_items = ["Typing tomorrow is useful."]
        game.sentence_index = 0
        game.sentence_typed = "Typing "
        game.announce_sentence_remaining()
        self.assertIn("Missing:", game.speech.last_message)
        self.assertIn("Remaining text:", game.speech.last_message)

    def test_copy_word_and_definition_payload(self):
        game = self._build_game()
        game.word = "tomorrow"
        game.word_definition = "The day after today."
        captured = {}

        def _fake_clipboard(text):
            captured["text"] = text
            return True

        game._set_clipboard_text = _fake_clipboard
        game.copy_word_and_definition()
        self.assertEqual(captured["text"], "Word: TOMORROW\nDefinition: The day after today.")
        self.assertEqual(game.speech.last_message, "Copied word and definition to clipboard.")

    def test_announce_letter_count_reports_remaining_and_total(self):
        game = self._build_game()
        game.word = "tomorrow"
        game.guessed_letters = {"t", "o", "m"}
        game.announce_letter_count()
        self.assertEqual(game.speech.last_message, "3 letters left. 8 total letters.")


class TestHangmanProgressFormatting(unittest.TestCase):
    def test_spoken_progress_uses_blank_for_unknown_letters(self):
        result = build_spoken_word_progress("tomorrow", {"t"})
        self.assertEqual(result, "t, blank, blank, blank, blank, blank, blank, blank")

    def test_spoken_progress_reveals_guessed_letters(self):
        result = build_spoken_word_progress("tomorrow", {"t", "o"})
        self.assertEqual(result, "t, o, blank, o, blank, blank, o, blank")

    def test_visual_progress_uses_underscores(self):
        result = build_visual_word_progress("tomorrow", {"t", "o"})
        self.assertEqual(result, "T O _ O _ _ O _")

    def test_spoken_progress_marks_spaces(self):
        result = build_spoken_word_progress("typing practice", {"t"})
        self.assertEqual(result, "t, blank, blank, blank, blank, blank, space, blank, blank, blank, blank, t, blank, blank, blank")

    def test_visual_progress_marks_spaces(self):
        result = build_visual_word_progress("typing practice", {"t"})
        self.assertEqual(result, "T _ _ _ _ _ / _ _ _ _ T _ _ _")

    def test_word_bank_words_are_five_or_more_characters(self):
        self.assertTrue(all(len(word) >= 5 for word in WORD_BANK.keys()))

    def test_candidate_pool_words_have_definitions(self):
        pool = load_candidate_pool()
        self.assertTrue(pool)
        self.assertTrue(all(len(word) >= 5 and bool(defn) for word, defn in pool))

    def test_candidate_pool_has_no_generic_placeholder_definitions(self):
        pool = load_candidate_pool()
        self.assertTrue(all("is a valid english word" not in defn.lower() for _, defn in pool))

    def test_candidate_length_buckets_include_multiple_lengths(self):
        buckets = load_candidate_length_buckets()
        self.assertTrue(buckets)
        self.assertTrue(len(buckets.keys()) > 1)

    def test_sentence_practice_items_include_word(self):
        items = build_sentence_practice_items("tomorrow", count=4)
        self.assertEqual(len(items), 4)
        self.assertTrue(all("tomorrow" in s.lower() for s in items))

    def test_hangman_stage_descriptions_cover_all_ten_steps(self):
        for stage in range(1, 11):
            self.assertTrue(describe_hangman_stage(stage))


if __name__ == "__main__":
    unittest.main()
