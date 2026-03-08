import unittest

from modules import speech_format


class TestSpeechFormat(unittest.TestCase):
    def test_spell_text_spaces_and_repeated_letters(self):
        self.assertEqual(speech_format.spell_text("aa"), "a, a")
        self.assertEqual(speech_format.spell_text("a a"), "a, space, a")

    def test_spell_text_for_typing_instruction_compacts_repeated_identical_letters(self):
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("aa"),
            "a twice",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("aaa"),
            "a 3 times",
        )

    def test_spell_text_for_typing_instruction_keeps_plain_words_natural(self):
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("sad", natural_words={"sad", "dad"}),
            "sad",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("dad", natural_words={"sad", "dad"}),
            "dad",
        )

    def test_spell_text_for_typing_instruction_spells_non_words(self):
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("a a"),
            "a, space, a",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("df"),
            "d, f",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("sAA"),
            "s, a, a",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("aass"),
            "a, a, s, s",
        )
        self.assertEqual(
            speech_format.spell_text_for_typing_instruction("asas", natural_words={"sad", "dad"}),
            "a, s, a, s",
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
