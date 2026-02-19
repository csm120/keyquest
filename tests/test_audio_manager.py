import unittest

from modules.audio_manager import AudioManager


class TestAudioManager(unittest.TestCase):
    def test_typing_tones_are_not_too_short(self):
        fs = AudioManager.SAMPLE_RATE

        ok = AudioManager.make_coin_sound()
        miss = AudioManager.make_miss_sound()
        progressive = AudioManager.make_progressive_tone(0.5)

        self.assertEqual(len(ok), int(fs * 0.110))
        self.assertEqual(len(miss), int(fs * 0.160))
        self.assertEqual(len(progressive), int(fs * 0.095))

    def test_set_typing_sound_intensity_updates_state(self):
        audio = AudioManager()
        audio.set_typing_sound_intensity("strong")
        self.assertEqual(audio.typing_sound_intensity, "strong")
        audio.set_typing_sound_intensity("invalid")
        self.assertEqual(audio.typing_sound_intensity, "normal")


if __name__ == "__main__":
    unittest.main()
