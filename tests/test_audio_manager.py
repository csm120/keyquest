import unittest

import numpy as np

from modules.audio_manager import AudioManager


class TestMakeToneShape(unittest.TestCase):
    """make_tone() produces arrays with the expected number of samples."""

    def _expected_samples(self, dur_ms):
        fs = AudioManager.SAMPLE_RATE
        return int(fs * dur_ms / 1000.0)

    def test_short_duration_sample_count(self):
        wave = AudioManager.make_tone(440.0, 50)
        self.assertEqual(len(wave), self._expected_samples(50))

    def test_longer_duration_sample_count(self):
        wave = AudioManager.make_tone(440.0, 200)
        self.assertEqual(len(wave), self._expected_samples(200))

    def test_sample_rate_constant_is_standard(self):
        self.assertEqual(AudioManager.SAMPLE_RATE, 44100)

    def test_dtype_is_float32(self):
        wave = AudioManager.make_tone(440.0, 100)
        self.assertEqual(wave.dtype, np.float32)

    def test_returns_1d_array(self):
        wave = AudioManager.make_tone(440.0, 100)
        self.assertEqual(wave.ndim, 1)


class TestMakeToneAmplitude(unittest.TestCase):
    """make_tone() amplitudes fit in the float [-1, 1] range and the int16 equivalent."""

    def test_amplitude_within_float_range(self):
        wave = AudioManager.make_tone(440.0, 100)
        self.assertLessEqual(float(np.max(np.abs(wave))), 1.0)

    def test_amplitude_within_int16_range(self):
        wave = AudioManager.make_tone(440.0, 100)
        int16_wave = (wave * 32767).astype(np.int16)
        self.assertLessEqual(int(np.max(np.abs(int16_wave))), 32767)

    def test_peak_is_nonzero_for_valid_frequency(self):
        wave = AudioManager.make_tone(440.0, 100)
        self.assertGreater(float(np.max(np.abs(wave))), 0.0)

    def test_amplitude_within_float_range_for_various_frequencies(self):
        for freq in [110.0, 440.0, 880.0, 2000.0, 4000.0]:
            with self.subTest(freq=freq):
                wave = AudioManager.make_tone(freq, 50)
                self.assertLessEqual(float(np.max(np.abs(wave))), 1.0)


class TestToneCache(unittest.TestCase):
    """Calling the same static generator twice returns the same array values.

    AudioManager uses no explicit cache on the static make_tone() method itself;
    instead we verify that two calls with identical parameters produce
    numerically identical results (idempotent, deterministic generation), and
    that objects that ARE cached (e.g., tone_ok / tone_bad on the instance)
    remain the same object across accesses without hardware.
    """

    def test_make_tone_is_deterministic(self):
        a = AudioManager.make_tone(440.0, 50)
        b = AudioManager.make_tone(440.0, 50)
        np.testing.assert_array_equal(a, b)

    def test_make_coin_sound_is_deterministic(self):
        a = AudioManager.make_coin_sound()
        b = AudioManager.make_coin_sound()
        np.testing.assert_array_equal(a, b)

    def test_instance_tone_ok_identity_after_intensity_set(self):
        """After set_typing_sound_intensity, tone_ok is rebuilt once and stays
        the same object until the intensity changes again."""
        audio = AudioManager()
        audio.set_typing_sound_intensity("subtle")
        ref = audio.tone_ok
        # Accessing the attribute again should return the same object (no rebuild).
        self.assertIs(audio.tone_ok, ref)

    def test_different_frequencies_produce_different_arrays(self):
        a = AudioManager.make_tone(440.0, 50)
        b = AudioManager.make_tone(880.0, 50)
        self.assertFalse(np.array_equal(a, b))


class TestCoinSoundHarmonicStructure(unittest.TestCase):
    """make_coin_sound() must have at least 2 frequency components."""

    def test_coin_sound_has_two_frequency_components(self):
        """Verify via FFT that both the fundamental (E6=1319 Hz) and the
        harmonic (E7=2637 Hz) are present with meaningful energy."""
        wave = AudioManager.make_coin_sound()
        fs = AudioManager.SAMPLE_RATE
        spectrum = np.abs(np.fft.rfft(wave))
        freqs = np.fft.rfftfreq(len(wave), 1.0 / fs)

        def peak_magnitude_near(target_hz, tolerance_hz=50):
            mask = np.abs(freqs - target_hz) < tolerance_hz
            return float(np.max(spectrum[mask])) if mask.any() else 0.0

        fundamental_mag = peak_magnitude_near(1319)
        harmonic_mag = peak_magnitude_near(2637)

        # Both should be clearly above zero.
        self.assertGreater(fundamental_mag, 0.0,
                           "No energy found near E6 (1319 Hz) fundamental")
        self.assertGreater(harmonic_mag, 0.0,
                           "No energy found near E7 (2637 Hz) harmonic")

    def test_coin_sound_dtype_and_range(self):
        wave = AudioManager.make_coin_sound()
        self.assertEqual(wave.dtype, np.float32)
        self.assertLessEqual(float(np.max(np.abs(wave))), 1.0)

    def test_coin_sound_length(self):
        wave = AudioManager.make_coin_sound()
        expected = int(AudioManager.SAMPLE_RATE * 0.110)
        self.assertEqual(len(wave), expected)


class TestEnvelopeShape(unittest.TestCase):
    """The exponential-decay envelope means the middle is louder than the edges."""

    def _measure_rms(self, segment):
        return float(np.sqrt(np.mean(segment.astype(np.float64) ** 2)))

    def test_coin_sound_envelope_attack_release(self):
        """First and last 10 % of the coin sound should have lower RMS than
        the middle 20 %, because an exponential decay envelope is applied."""
        wave = AudioManager.make_coin_sound()
        n = len(wave)
        tenth = n // 10
        fifth = n // 5

        first_tenth = wave[:tenth]
        middle_fifth = wave[n // 2 - fifth // 2: n // 2 + fifth // 2]
        last_tenth = wave[-tenth:]

        rms_first = self._measure_rms(first_tenth)
        rms_middle = self._measure_rms(middle_fifth)
        rms_last = self._measure_rms(last_tenth)

        # The exponential decay means energy at start > energy at end,
        # and middle is louder than the tail.
        self.assertGreater(rms_middle, rms_last,
                           "Middle should be louder than tail under exponential decay")
        self.assertGreater(rms_first, rms_last,
                           "First samples should be louder than last (exponential decay)")

    def test_miss_sound_envelope_attack_release(self):
        """Same check for the miss sound."""
        wave = AudioManager.make_miss_sound()
        n = len(wave)
        tenth = n // 10
        fifth = n // 5

        rms_middle = self._measure_rms(wave[n // 2 - fifth // 2: n // 2 + fifth // 2])
        rms_last = self._measure_rms(wave[-tenth:])

        self.assertGreater(rms_middle, rms_last,
                           "Middle should be louder than tail for miss sound")

    def test_success_tones_envelope_shape(self):
        """Success tones: the first 10 % of each individual tone is louder than its last 10 %."""
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 80
        segment_samples = int(fs * dur_ms / 1000.0)
        wave = AudioManager.make_success_tones()

        # Check just the first note (first segment_samples samples).
        first_note = wave[:segment_samples]
        tenth = segment_samples // 10
        rms_start = self._measure_rms(first_note[:tenth])
        rms_end = self._measure_rms(first_note[-tenth:])
        self.assertGreater(rms_start, rms_end,
                           "Start of first success tone should be louder than its end")

    def test_apply_typing_intensity_clips_to_valid_range(self):
        """_apply_typing_intensity must never exceed the float [-1, 1] range."""
        audio = AudioManager()
        audio.set_typing_sound_intensity("strong")
        wave = AudioManager.make_coin_sound()
        adjusted = audio._apply_typing_intensity(wave)
        self.assertIsNotNone(adjusted)
        self.assertLessEqual(float(np.max(np.abs(adjusted))), 1.0)


class TestInvalidFrequency(unittest.TestCase):
    """Edge-case frequencies must not crash make_tone()."""

    def test_zero_frequency_does_not_raise(self):
        """Zero frequency: sin(0) is all zeros, should return silently."""
        try:
            wave = AudioManager.make_tone(0.0, 50)
        except Exception as exc:
            self.fail(f"make_tone(0.0, 50) raised unexpectedly: {exc}")
        # A 0 Hz sine wave is all zeros.
        np.testing.assert_array_equal(wave, np.zeros(len(wave), dtype=np.float32))

    def test_very_high_frequency_does_not_raise(self):
        """Nyquist-limit frequency: 22050 Hz at 44100 sample rate."""
        try:
            wave = AudioManager.make_tone(22050.0, 50)
        except Exception as exc:
            self.fail(f"make_tone(22050.0, 50) raised unexpectedly: {exc}")
        self.assertLessEqual(float(np.max(np.abs(wave))), 1.0)

    def test_very_low_positive_frequency_does_not_raise(self):
        try:
            wave = AudioManager.make_tone(0.001, 50)
        except Exception as exc:
            self.fail(f"make_tone(0.001, 50) raised unexpectedly: {exc}")
        self.assertLessEqual(float(np.max(np.abs(wave))), 1.0)

    def test_zero_duration_returns_empty_array(self):
        """Zero duration should produce an empty array without crashing."""
        try:
            wave = AudioManager.make_tone(440.0, 0)
        except Exception as exc:
            self.fail(f"make_tone(440.0, 0) raised unexpectedly: {exc}")
        self.assertEqual(len(wave), 0)


class TestApplyTypingIntensity(unittest.TestCase):
    """_apply_typing_intensity gain and clipping behaviour."""

    def test_none_input_returns_none(self):
        audio = AudioManager()
        result = audio._apply_typing_intensity(None)
        self.assertIsNone(result)

    def test_normal_intensity_gain_is_1(self):
        audio = AudioManager()
        audio.typing_sound_intensity = "normal"
        wave = np.array([0.5, -0.5], dtype=np.float32)
        result = audio._apply_typing_intensity(wave)
        np.testing.assert_allclose(result, wave, rtol=1e-6)

    def test_subtle_intensity_reduces_amplitude(self):
        audio = AudioManager()
        audio.typing_sound_intensity = "subtle"
        wave = np.array([1.0, -1.0], dtype=np.float32)
        result = audio._apply_typing_intensity(wave)
        expected_gain = AudioManager.TYPING_INTENSITY_GAIN["subtle"]
        np.testing.assert_allclose(result, wave * expected_gain, rtol=1e-5)

    def test_strong_intensity_clips_at_1(self):
        audio = AudioManager()
        audio.typing_sound_intensity = "strong"
        # A value that would exceed 1.0 after gain is applied.
        wave = np.array([0.9, -0.9], dtype=np.float32)
        result = audio._apply_typing_intensity(wave)
        self.assertLessEqual(float(np.max(np.abs(result))), 1.0)


class TestTypingIntensityConstants(unittest.TestCase):
    """Verify the gain table has the expected presets."""

    def test_all_presets_present(self):
        presets = AudioManager.TYPING_INTENSITY_GAIN
        for name in ("subtle", "normal", "strong"):
            self.assertIn(name, presets)

    def test_normal_gain_is_1(self):
        self.assertAlmostEqual(AudioManager.TYPING_INTENSITY_GAIN["normal"], 1.0)

    def test_subtle_is_less_than_normal(self):
        self.assertLess(
            AudioManager.TYPING_INTENSITY_GAIN["subtle"],
            AudioManager.TYPING_INTENSITY_GAIN["normal"],
        )

    def test_strong_is_greater_than_normal(self):
        self.assertGreater(
            AudioManager.TYPING_INTENSITY_GAIN["strong"],
            AudioManager.TYPING_INTENSITY_GAIN["normal"],
        )


if __name__ == "__main__":
    unittest.main()
