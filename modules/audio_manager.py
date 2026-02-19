"""Audio management and sound generation for KeyQuest.

Centralizes all audio/tone generation with caching for better performance.
All sounds are generated using numpy for consistency.
"""

import numpy as np
import pygame


class AudioManager:
    """Manages all audio generation and playback for KeyQuest."""

    # Audio constants
    SAMPLE_RATE = 44100  # Standard sample rate
    TYPING_INTENSITY_GAIN = {
        "subtle": 0.70,
        "normal": 1.00,
        "strong": 1.35,
    }

    def __init__(self):
        """Initialize audio manager and cache common sounds."""
        # Cache frequently-used sounds for performance
        self.tone_ok = None
        self.tone_bad = None
        self._sound_ok = None
        self._sound_bad = None
        self._feedback_channel = None
        self.typing_sound_intensity = "normal"

        try:
            self._refresh_typing_sounds()
            # Reserve one channel for rapid typing feedback so short sounds are less likely to be lost.
            self._feedback_channel = pygame.mixer.find_channel(force=False)
        except Exception as e:
            print(f"Warning: Could not initialize audio tones: {e}")
            self.tone_ok = None
            self.tone_bad = None
            self._sound_ok = None
            self._sound_bad = None
            self._feedback_channel = None

    # ========== Basic Tone Generation ==========

    @staticmethod
    def make_tone(freq: float, dur_ms: float):
        """Generate a simple sine wave tone.

        Args:
            freq: Frequency in Hz
            dur_ms: Duration in milliseconds

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)
        wave = 0.5 * np.sin(2 * np.pi * freq * t)
        return wave.astype(np.float32)

    @staticmethod
    def make_coin_sound():
        """Generate Mario-style coin sound - TIER 1: Ultra-short for typing rhythm.

        Based on Mario coin: E6 (1319Hz) with B7 harmonic (2637Hz).
        Duration: ~110ms - still quick, but easier to perceive consistently.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 110  # Short and more audible
        t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)

        # E6 fundamental with B7 harmonic (perfect fifth, 2 octaves up)
        fundamental = 1319  # E6
        harmonic = 2637     # B7 (perfect fifth overtone)

        # Sharp attack envelope for crisp feedback
        envelope = np.exp(-6.0 * t / (dur_ms / 1000.0))
        wave = 0.35 * np.sin(2 * np.pi * fundamental * t) * envelope
        wave += 0.15 * np.sin(2 * np.pi * harmonic * t) * envelope  # Quieter harmonic

        return wave.astype(np.float32)

    @staticmethod
    def make_miss_sound():
        """Generate Duck Hunt-style miss sound - TIER 1: Short for typing rhythm.

        Based on Duck Hunt missed: ~880Hz (A5), short descending.
        Duration: ~160ms - quick correction cue, clearer on slower audio stacks.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 160  # Short and clearer
        t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)

        # Start at A5 (880Hz), descend to F5 (698Hz)
        start_freq = 880
        end_freq = 698
        freq_sweep = start_freq - (start_freq - end_freq) * (t / (dur_ms / 1000.0))

        phase = 2 * np.pi * np.cumsum(freq_sweep) / fs
        envelope = np.exp(-5.5 * t / (dur_ms / 1000.0))  # Sharper envelope
        wave = 0.4 * np.sin(phase) * envelope

        return wave.astype(np.float32)

    @staticmethod
    def make_progressive_tone(percentage: float):
        """Generate a quick rising tone - TIER 1: Derivative of success sound.

        Based on the first note of the success sound (G5) but raised in pitch
        as percentage increases, making it more audible than the old chirp.

        Args:
            percentage: Completion percentage (0.0 to 1.0)

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 95  # Slightly longer so in-word progress is easier to hear

        # Start from G5 (784 Hz) and raise pitch as we progress
        # At 0%: G5 (784 Hz), at 100%: E6 (1319 Hz)
        # This follows the same note progression as success sound but condensed
        base_freq = 784  # G5 (first note of success sound)
        pitch_range = 535  # Range from G5 to E6 (1319 - 784)
        fundamental = base_freq + (pitch_range * percentage)

        # Harmonic is one octave higher (like in success sound)
        harmonic = fundamental * 2

        t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)

        # Same envelope style as success sound for consistency
        envelope = np.exp(-5.0 * t / (dur_ms / 1000.0))

        # Same harmonic blend as success sound - fundamental + octave harmonic
        tone = 0.35 * np.sin(2 * np.pi * fundamental * t) * envelope
        tone += 0.12 * np.sin(2 * np.pi * harmonic * t) * envelope

        return tone.astype(np.float32)

    @staticmethod
    def make_success_tones():
        """Generate 3 rising tones - TIER 1: Quick completion cue.

        Duration: ~240ms total - fast enough to not break typing flow.

        Returns:
            numpy array of audio samples (3 concatenated tones)
        """
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 80  # Each tone is 80ms (total: 240ms)
        tones = []

        # Three ascending tones with harmonics: G5, C6, E6
        notes = [
            (784, 1568),    # G5 with G6 harmonic
            (1047, 2093),   # C6 with C7 harmonic
            (1319, 2637)    # E6 with E7 harmonic
        ]

        for fundamental, harmonic in notes:
            t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)
            envelope = np.exp(-5.0 * t / (dur_ms / 1000.0))
            tone = 0.35 * np.sin(2 * np.pi * fundamental * t) * envelope
            tone += 0.12 * np.sin(2 * np.pi * harmonic * t) * envelope
            tones.append(tone)

        # Concatenate all tones
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_buzz_sound():
        """Generate a timeout melody - TIER 2: Neutral, informative "time's up" sound.

        Descending melodic pattern that conveys "time ended" without being harsh or gloomy.
        Not celebratory, just informative. Like a clock chiming to mark the hour.
        Duration: ~1.4s - dialog shows timeout results.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE

        # Neutral descending pattern: G5, E5, C5, G4 (descending in C major)
        # Tempo is moderate - not rushed, not slow
        # Pattern feels like "time... has... ended... now"
        melody = [
            (784, 0.28),   # G5 (start high)
            (659, 0.28),   # E5 (descend)
            (523, 0.28),   # C5 (descend more)
            (392, 0.56)    # G4 (final resolution, held longer)
        ]

        tones = []
        for freq, dur in melody:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)

            # Moderate envelope - not too sharp, not too long
            # The final note has longer sustain for resolution
            decay_rate = 2.0 if dur > 0.4 else 2.8
            envelope = np.exp(-decay_rate * t / dur)

            # Note with subtle harmonic for clarity
            tone = 0.38 * np.sin(2 * np.pi * freq * t) * envelope
            tone += 0.10 * np.sin(2 * np.pi * freq * 2 * t) * envelope  # Subtle octave harmonic

            tones.append(tone)

        # Concatenate all notes (total: ~1.4s)
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_victory_sound():
        """Generate Mario 1-Up victory sound - TIER 2: Dialog pops up, can be elaborate.

        Based on Mario 1-Up: E5->G5->E6->E6->G6->E7 with rich harmonics.
        Duration: ~780ms - celebratory, dialog shows results so time to hear it.
        Used for: Lesson complete

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        note_duration = 0.13  # 130ms per note (6 notes = 780ms total)

        # Melody with harmonics: E5, G5, E6 (octave jump), E6, G6, E7
        # Each note has its octave harmonic for richness
        melody = [
            (659, 1319),    # E5 with E6 harmonic
            (784, 1568),    # G5 with G6 harmonic
            (1319, 2637),   # E6 with E7 harmonic (octave jump)
            (1319, 2637),   # E6 with E7 harmonic (repeat for emphasis)
            (1568, 3136),   # G6 with G7 harmonic
            (2637, 5274)    # E7 with E8 harmonic (final high note)
        ]

        tones = []
        for fundamental, harmonic in melody:
            t = np.linspace(0, note_duration, int(fs * note_duration), endpoint=False)

            # Musical envelope
            envelope = np.exp(-3.0 * t / note_duration)

            # Fundamental + octave harmonic for rich Mario-like sound
            tone = 0.35 * np.sin(2 * np.pi * fundamental * t) * envelope
            tone += 0.15 * np.sin(2 * np.pi * harmonic * t) * envelope

            tones.append(tone)

        # Concatenate all notes
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_unlock_sound():
        """Generate unlock jingle - TIER 2: Dialog pops up, celebratory melody.

        Two-part melody: unlock chord, then triumphant fanfare.
        Duration: ~540ms - dialog announces unlock, so time for celebration.
        Used for: New lesson unlocked

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE

        # Part 1: "Unlock" chord (G4 + B4 together, then D5 + G5 together)
        unlock_chords = [
            ([392, 494], 0.11),    # G4 + B4 (major third)
            ([587, 784], 0.11)     # D5 + G5 (perfect fourth)
        ]

        # Part 2: Triumphant melody: C5, E5, G5, C6 with varied rhythm
        reveal_melody = [
            (523, 0.09),   # C5
            (659, 0.09),   # E5
            (784, 0.09),   # G5
            (1047, 0.18)   # C6 (held longer for finish)
        ]

        tones = []

        # Generate unlock chords (total: 220ms)
        for freqs, dur in unlock_chords:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)
            envelope = np.exp(-5.0 * t / dur)
            chord_wave = np.zeros_like(t)

            for freq in freqs:
                chord_wave += 0.25 * np.sin(2 * np.pi * freq * t)

            chord_wave *= envelope
            tones.append(chord_wave)

        # Generate triumphant reveal melody (total: 450ms)
        for freq, dur in reveal_melody:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)
            envelope = np.exp(-3.0 * t / dur)

            # Note with octave harmonic
            tone = 0.35 * np.sin(2 * np.pi * freq * t) * envelope
            tone += 0.12 * np.sin(2 * np.pi * freq * 2 * t) * envelope
            tones.append(tone)

        # Concatenate all parts (total: ~540ms)
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_badge_sound():
        """Generate badge earned jingle - TIER 2: Dialog pops up, bright celebration.

        Based on Mario coin sound with rich harmonics.
        Duration: ~420ms - dialog shows badge, time for bright celebration.
        Used for: Badge unlocked

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur_ms = 140  # Each note 140ms

        # Three-note jingle: B5 -> E6 -> B6 (octave jump), all with harmonics
        notes = [
            (988, 1976),    # B5 with B6 harmonic (octave)
            (1319, 2637),   # E6 with B7 harmonic (perfect fifth, 2 octaves up)
            (1976, 3951)    # B6 with B7 harmonic (final high note)
        ]

        tones = []
        for fundamental, harmonic in notes:
            t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)
            envelope = np.exp(-4.5 * t / (dur_ms / 1000.0))

            # Fundamental + harmonic for richness
            tone = 0.35 * np.sin(2 * np.pi * fundamental * t) * envelope
            tone += 0.15 * np.sin(2 * np.pi * harmonic * t) * envelope
            tones.append(tone)

        # Concatenate notes (total: ~420ms)
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_levelup_sound():
        """Generate Mario PowerUp rising arpeggio - TIER 2: Dialog pops up, triumphant.

        Based on Mario PowerUp: D4->F#4->A4->D5->F#5->A5->D6 (rising arpeggio).
        Duration: ~560ms - dialog shows new level, time for energetic celebration.
        Used for: Level up

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        note_duration = 0.08  # 80ms per note (7 notes = 560ms total)

        # Rising arpeggio in D major: D4, F#4, A4, D5, F#5, A5, D6
        melody = [294, 370, 440, 587, 740, 880, 1175]

        tones = []
        for freq in melody:
            t = np.linspace(0, note_duration, int(fs * note_duration), endpoint=False)

            # Quick envelope for energetic feel
            envelope = np.exp(-4.0 * t / note_duration)
            tone = 0.32 * np.sin(2 * np.pi * freq * t) * envelope

            # Add octave harmonic for richness
            tone += 0.12 * np.sin(2 * np.pi * freq * 2 * t) * envelope

            tones.append(tone)

        # Concatenate all notes (total: ~560ms)
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    @staticmethod
    def make_quest_sound():
        """Generate quest fanfare - TIER 2: Dialog pops up, biggest celebration.

        Melodic jingle with chords and rhythm variation like Mario level clear.
        Duration: ~960ms - dialog shows quest complete, time for grand fanfare.
        Used for: Quest complete

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE

        # Fanfare melody with harmony: intro notes, then triumphant ending
        # Pattern: G4, G4, G4, E5, (pause), C5+E5 chord, G5+C6 chord (held)
        notes = [
            ([392], 0.12),        # G4
            ([392], 0.12),        # G4
            ([392], 0.12),        # G4
            ([659], 0.18),        # E5 (longer)
            ([523, 659], 0.16),   # C5 + E5 chord
            ([784, 1047], 0.38)   # G5 + C6 chord (final, held longer)
        ]

        tones = []
        for freqs, dur in notes:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)

            # Envelope - longer sustain on final chord
            decay_rate = 1.8 if dur > 0.3 else 3.5
            envelope = np.exp(-decay_rate * t / dur)

            # Generate note or chord
            wave = np.zeros_like(t)
            volume = 0.3 if len(freqs) > 1 else 0.36  # Quieter for chords
            for freq in freqs:
                wave += volume * np.sin(2 * np.pi * freq * t)
                # Add octave harmonic
                wave += volume * 0.15 * np.sin(2 * np.pi * freq * 2 * t)

            wave *= envelope
            tones.append(wave)

        # Concatenate all notes (total: ~960ms)
        wave = np.concatenate(tones)
        return wave.astype(np.float32)

    # ========== Playback Methods ==========

    def _apply_typing_intensity(self, wave):
        """Apply current typing-sound intensity gain with clipping protection."""
        if wave is None:
            return None
        gain = self.TYPING_INTENSITY_GAIN.get(self.typing_sound_intensity, 1.0)
        adjusted = wave * gain
        return np.clip(adjusted, -1.0, 1.0).astype(np.float32)

    def _refresh_typing_sounds(self):
        """Rebuild cached typing sounds after intensity change."""
        base_ok = self.make_coin_sound()
        base_bad = self.make_miss_sound()
        self.tone_ok = self._apply_typing_intensity(base_ok)
        self.tone_bad = self._apply_typing_intensity(base_bad)
        self._sound_ok = self._make_sound_object(self.tone_ok)
        self._sound_bad = self._make_sound_object(self.tone_bad)

    def set_typing_sound_intensity(self, intensity: str):
        """Set typing sound intensity preset: subtle, normal, or strong."""
        if intensity not in self.TYPING_INTENSITY_GAIN:
            intensity = "normal"
        self.typing_sound_intensity = intensity
        try:
            self._refresh_typing_sounds()
        except Exception:
            pass

    def _make_sound_object(self, wave):
        """Convert float wave [-1,1] to a reusable pygame Sound object."""
        if wave is None:
            return None
        arr = (wave * 32767).astype(np.int16)
        init = pygame.mixer.get_init()
        if init is not None:
            _, _, channels = init
            if channels == 2:
                arr = np.column_stack((arr, arr))
        return pygame.sndarray.make_sound(arr)

    def play_wave(self, wave):
        """Play an audio wave through pygame.

        Args:
            wave: numpy array of audio samples

        Returns:
            None
        """
        try:
            if wave is None:
                return

            sound = self._make_sound_object(wave)
            if sound is None:
                return
            sound.play()
        except Exception as e:
            # Silently ignore audio errors (non-critical)
            pass

    def beep_ok(self):
        """Play a positive feedback beep (high tone)."""
        try:
            if self._sound_ok is not None:
                if self._feedback_channel is None:
                    self._feedback_channel = pygame.mixer.find_channel(force=False)
                if self._feedback_channel is not None:
                    self._feedback_channel.play(self._sound_ok)
                else:
                    self._sound_ok.play()
                return
        except Exception:
            pass
        self.play_wave(self.tone_ok)

    def beep_bad(self):
        """Play a negative feedback beep (low tone)."""
        try:
            if self._sound_bad is not None:
                if self._feedback_channel is None:
                    self._feedback_channel = pygame.mixer.find_channel(force=False)
                if self._feedback_channel is not None:
                    self._feedback_channel.play(self._sound_bad)
                else:
                    self._sound_bad.play()
                return
        except Exception:
            pass
        self.play_wave(self.tone_bad)

    def play_progressive(self, percentage: float):
        """Play a progressive tone based on completion percentage.

        Args:
            percentage: Completion percentage (0.0 to 1.0)
        """
        tone = self._apply_typing_intensity(self.make_progressive_tone(percentage))
        self.play_wave(tone)

    def play_success(self):
        """Play success tones (3 rising notes)."""
        tones = self._apply_typing_intensity(self.make_success_tones())
        self.play_wave(tones)

    def play_victory(self):
        """Play victory melody (lesson complete)."""
        victory = self.make_victory_sound()
        self.play_wave(victory)

    def play_unlock(self):
        """Play unlock sound (new lesson unlocked)."""
        unlock = self.make_unlock_sound()
        self.play_wave(unlock)

    def play_badge(self):
        """Play badge sound (badge earned)."""
        badge = self.make_badge_sound()
        self.play_wave(badge)

    def play_levelup(self):
        """Play level up sound (leveled up)."""
        levelup = self.make_levelup_sound()
        self.play_wave(levelup)

    def play_quest(self):
        """Play quest complete sound (quest finished)."""
        quest = self.make_quest_sound()
        self.play_wave(quest)

    def play_buzz(self):
        """Play timeout buzz sound."""
        buzz = self.make_buzz_sound()
        self.play_wave(buzz)

    # ========== Pet Sounds ==========

    @staticmethod
    def make_robot_sound():
        """Generate retro robot beep - R2D2-style chirp with pitch bend.

        Chiptune style:
        - Square wave (pulse) for classic 8-bit character
        - Pitch bend from 600Hz up to 900Hz
        - Duration: 0.25s
        - Simple exponential decay

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur = 0.25

        t = np.linspace(0, dur, int(fs * dur), endpoint=False)

        # Pitch bend upward (R2D2-style chirp)
        start_freq = 600
        end_freq = 900
        freq = start_freq + (end_freq - start_freq) * (t / dur)

        # Generate phase for varying frequency
        phase = 2 * np.pi * np.cumsum(freq) / fs

        # Square wave (pulse) - classic chiptune sound
        # Use sign of sine to create square wave
        beep = np.sign(np.sin(phase))

        # Smooth edges slightly to reduce harshness
        beep = 0.7 * beep + 0.3 * np.sin(phase)

        # Sharp decay envelope
        envelope = np.exp(-4.0 * t / dur)

        beep = beep * envelope
        return (0.25 * beep).astype(np.float32)

    @staticmethod
    def make_dragon_sound():
        """Generate retro dragon growl - deep portamento slide.

        Chiptune style:
        - Triangle wave for deeper, less harsh tone
        - Pitch slide from 280Hz down to 180Hz (portamento growl)
        - Duration: 0.4s
        - Attack-sustain-release envelope

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur = 0.4

        t = np.linspace(0, dur, int(fs * dur), endpoint=False)

        # Downward pitch slide (growl effect)
        start_freq = 280
        end_freq = 180
        freq = start_freq + (end_freq - start_freq) * (t / dur)

        # Generate phase
        phase = 2 * np.pi * np.cumsum(freq) / fs

        # Triangle wave - softer than square, good for growls
        # sawtooth modulo approach to create triangle
        triangle = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1

        # Mix with sine for smoother sound
        wave = 0.6 * triangle + 0.4 * np.sin(phase)

        # ASR envelope
        attack_samples = int(fs * 0.05)
        release_samples = int(fs * 0.15)
        sustain_samples = len(t) - attack_samples - release_samples

        envelope = np.concatenate([
            np.linspace(0, 1, attack_samples),
            np.ones(sustain_samples),
            np.linspace(1, 0, release_samples)
        ])

        wave = wave * envelope
        return (0.35 * wave).astype(np.float32)

    @staticmethod
    def make_owl_sound():
        """Generate retro owl hoot - classic 'hoo hoo' pattern.

        Chiptune style:
        - Two simple sine wave hoots at 420Hz
        - Each hoot 0.18s with 0.12s gap
        - Bell-shaped envelope for smooth hoots
        - Pure tone (no harmonics)

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        hoot_dur = 0.18
        gap_dur = 0.12

        hoots = []
        for _ in range(2):  # Two hoots
            t = np.linspace(0, hoot_dur, int(fs * hoot_dur), endpoint=False)

            # Simple sine wave at 420Hz (from Duck Hunt intro analysis)
            freq = 420
            wave = np.sin(2 * np.pi * freq * t)

            # Bell-shaped envelope
            envelope = np.exp(-6.0 * ((t - hoot_dur/2) / hoot_dur) ** 2)

            wave = wave * envelope
            hoots.append(wave)

        # Combine with gap
        silence = np.zeros(int(fs * gap_dur))
        combined = np.concatenate([hoots[0], silence, hoots[1]])
        return (0.28 * combined).astype(np.float32)

    @staticmethod
    def make_cat_sound():
        """Generate retro cat meow - cartoon-style with pitch bend and vibrato.

        Chiptune style:
        - Triangle wave for softer tone
        - Pitch: 600Hz -> 900Hz -> 500Hz (meow contour)
        - Duration: 0.35s
        - Vibrato on the held portion

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur = 0.35

        t = np.linspace(0, dur, int(fs * dur), endpoint=False)

        # Pitch contour (meow shape)
        pitch = np.zeros_like(t)
        for i, time in enumerate(t):
            progress = time / dur
            if progress < 0.25:
                # Rise to peak
                pitch[i] = 600 + (300 * (progress / 0.25))
            elif progress < 0.65:
                # Hold at peak with vibrato
                vibrato = 20 * np.sin(2 * np.pi * 8 * time)
                pitch[i] = 900 + vibrato
            else:
                # Drop to end
                drop_prog = (progress - 0.65) / 0.35
                pitch[i] = 900 - (400 * drop_prog)

        # Generate phase
        phase = 2 * np.pi * np.cumsum(pitch) / fs

        # Triangle wave
        triangle = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1

        # Simple envelope
        envelope = np.exp(-1.8 * t / dur)

        meow = triangle * envelope
        return (0.28 * meow).astype(np.float32)

    @staticmethod
    def make_dog_sound():
        """Generate retro dog bark - high-pitched yappy bark with pitch drop.

        Chiptune style with vocal characteristics:
        - Pitch sweep from 1100Hz down to 700Hz (yap!)
        - Triangle wave dominant (warmer, less harsh)
        - Softer attack (less percussive)
        - Longer duration for vocal quality
        - Three yappy barks

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        bark_dur = 0.15  # Longer for more vocal quality
        gap_dur = 0.08

        barks = []
        for _ in range(3):  # Three barks
            t = np.linspace(0, bark_dur, int(fs * bark_dur), endpoint=False)

            # Pitch drops during bark (yap characteristic: high to lower)
            start_pitch = 1100  # High yappy start
            end_pitch = 700    # Drop to lower
            # Exponential drop (fast at first, then levels)
            pitch_progress = 1 - np.exp(-4 * t / bark_dur)
            freq = start_pitch - (start_pitch - end_pitch) * pitch_progress

            # Generate phase with varying pitch
            phase = 2 * np.pi * np.cumsum(freq) / fs

            # Use mostly triangle wave (warmer, less metallic than pulse)
            triangle = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1

            # Add some sine for smoothness
            bark = 0.7 * triangle + 0.3 * np.sin(phase)

            # Add very light noise for texture (not too much)
            noise = np.random.normal(0, 1, len(t))
            window_size = 8
            filtered_noise = np.convolve(noise, np.ones(window_size)/window_size, mode='same')

            bark = 0.85 * bark + 0.15 * filtered_noise

            # Softer attack envelope (less percussive, more vocal)
            attack_samples = int(fs * 0.02)  # 20ms soft attack
            sustain_samples = int(fs * 0.05)
            decay_samples = len(t) - attack_samples - sustain_samples

            envelope = np.concatenate([
                np.linspace(0, 1, attack_samples),  # Soft attack
                np.ones(sustain_samples),            # Brief sustain
                np.exp(-5.0 * np.linspace(0, 1, decay_samples))  # Decay
            ])

            bark = bark * envelope
            barks.append(bark)

        # Combine with gaps
        silence = np.zeros(int(fs * gap_dur))
        combined = np.concatenate([
            barks[0], silence,
            barks[1], silence,
            barks[2]
        ])
        return (0.32 * combined).astype(np.float32)

    @staticmethod
    def make_phoenix_sound():
        """Generate retro phoenix chime - magical ascending arpeggio.

        Chiptune style:
        - Triangle waves for magical tone
        - Ascending notes: E5(659), G5(784), B5(988), E6(1319)
        - Each note 0.12s
        - Simple decay envelopes

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        note_duration = 0.12

        # Magical ascending melody
        melody = [659, 784, 988, 1319]

        tones = []
        for i, freq in enumerate(melody):
            t = np.linspace(0, note_duration, int(fs * note_duration), endpoint=False)

            # Triangle wave for magical chime character
            phase = 2 * np.pi * freq * t
            triangle = 2 * np.abs(2 * (phase / (2 * np.pi) % 1) - 1) - 1

            # Add sine for smoothness
            wave = 0.6 * triangle + 0.4 * np.sin(phase)

            # Longer decay on final note
            if i == len(melody) - 1:
                envelope = np.exp(-2.5 * t / note_duration)
            else:
                envelope = np.exp(-4.0 * t / note_duration)

            wave = wave * envelope
            tones.append(wave)

        combined = np.concatenate(tones)
        return (0.30 * combined).astype(np.float32)

    @staticmethod
    def make_tribble_sound():
        """Generate retro tribble squeak - high-pitched small creature sound.

        Chiptune style:
        - High sine wave at 3700Hz (small creature frequency)
        - Vibrato for character
        - Duration: 0.3s
        - Soft envelope

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        dur = 0.3

        t = np.linspace(0, dur, int(fs * dur), endpoint=False)

        # High-pitched squeak (from small creature analysis)
        base_freq = 3700
        vibrato_rate = 8  # Fast vibrato for cute character
        vibrato_depth = 0.08  # 8% variation
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        freq = base_freq * vibrato

        phase = 2 * np.pi * np.cumsum(freq) / fs

        # Pure sine wave
        squeak = np.sin(phase)

        # Gentle envelope
        attack_samples = int(fs * 0.05)
        release_samples = int(fs * 0.10)
        sustain_samples = len(t) - attack_samples - release_samples

        envelope = np.concatenate([
            np.linspace(0, 1, attack_samples),
            np.ones(sustain_samples),
            np.linspace(1, 0, release_samples)
        ])

        squeak = squeak * envelope
        return (0.22 * squeak).astype(np.float32)

    @staticmethod
    def make_pet_feed_sound():
        """Generate pet feeding sound - happy eating sounds.

        Cheerful ascending notes indicating satisfaction.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE

        # Happy eating: quick ascending chirps
        notes = [523, 659, 784]  # C5, E5, G5
        dur = 0.1

        tones = []
        for freq in notes:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)
            wave = np.sin(2 * np.pi * freq * t)
            wave += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
            envelope = np.exp(-6.0 * t / dur)
            wave = wave * envelope
            tones.append(wave)

        combined = np.concatenate(tones)
        return (0.35 * combined).astype(np.float32)

    @staticmethod
    def make_pet_play_sound():
        """Generate pet playing sound - excited playful chirps.

        Bouncy, energetic pattern.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE

        # Playful bouncing pattern: up-down-up
        notes = [659, 523, 784]  # E5, C5, G5
        dur = 0.08

        tones = []
        for freq in notes:
            t = np.linspace(0, dur, int(fs * dur), endpoint=False)
            # Pulse wave for playful character
            phase = (freq * t) % 1.0
            wave = np.where(phase < 0.5, 1.0, -1.0)
            envelope = np.exp(-7.0 * t / dur)
            wave = wave * envelope
            tones.append(wave)

        combined = np.concatenate(tones)
        return (0.3 * combined).astype(np.float32)

    @staticmethod
    def make_pet_evolve_sound():
        """Generate pet evolution sound - magical transformation.

        Dramatic rising arpeggio with sparkle.

        Returns:
            numpy array of audio samples
        """
        fs = AudioManager.SAMPLE_RATE
        note_duration = 0.1

        # Magical ascending scale: C5 to C6
        melody = [523, 587, 659, 784, 880, 988, 1047]

        tones = []
        for freq in melody:
            t = np.linspace(0, note_duration, int(fs * note_duration), endpoint=False)

            # Rich harmonics for magical quality
            wave = 0.3 * np.sin(2 * np.pi * freq * t)
            wave += 0.2 * np.sin(2 * np.pi * freq * 2 * t)
            wave += 0.1 * np.sin(2 * np.pi * freq * 4 * t)  # Add sparkle

            envelope = np.exp(-4.0 * t / note_duration)
            wave = wave * envelope
            tones.append(wave)

        combined = np.concatenate(tones)
        return (0.38 * combined).astype(np.float32)

    def play_pet_sound(self, pet_type: str):
        """Play the sound for a specific pet type.

        Args:
            pet_type: One of: robot, dragon, owl, cat, dog, phoenix, tribble
        """
        sound_map = {
            'robot': self.make_robot_sound,
            'dragon': self.make_dragon_sound,
            'owl': self.make_owl_sound,
            'cat': self.make_cat_sound,
            'dog': self.make_dog_sound,
            'phoenix': self.make_phoenix_sound,
            'tribble': self.make_tribble_sound
        }

        if pet_type in sound_map:
            sound = sound_map[pet_type]()
            self.play_wave(sound)

    def play_pet_feed(self):
        """Play pet feeding sound."""
        sound = self.make_pet_feed_sound()
        self.play_wave(sound)

    def play_pet_play(self):
        """Play pet playing sound."""
        sound = self.make_pet_play_sound()
        self.play_wave(sound)

    def play_pet_evolve(self):
        """Play pet evolution sound."""
        sound = self.make_pet_evolve_sound()
        self.play_wave(sound)
