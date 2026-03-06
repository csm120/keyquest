import unittest

from modules import speech_format


class TestSpeechFormat(unittest.TestCase):
    def test_spell_text_spaces_and_repeated_letters(self):
        self.assertEqual(speech_format.spell_text("aa"), "a, a")
        self.assertEqual(speech_format.spell_text("a a"), "a, space, a")

    def test_spell_text_for_typing_instruction_uses_then_for_sequences(self):
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("a a"),
            "a, then space, then a",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("fef"),
            "f, then e, then f",
        )

    def test_spell_text_for_typing_instruction_keeps_plain_words_compact(self):
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("sad"),
            "s, a, d",
        )

    def test_build_remaining_text_feedback(self):
        msg = speech_format.build_remaining_text_feedback("a a")
        self.assertEqual(msg, "Type: a. Then: a")

    def test_build_remaining_text_feedback_preserves_caps_and_punctuation_in_first_word(self):
        msg = speech_format.build_remaining_text_feedback("Hello, world.")
        self.assertEqual(
            msg,
            "Type: capital h, e, l, l, o, comma. Then: world.",
        )


if __name__ == "__main__":
    unittest.main()
