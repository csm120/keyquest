"""Nintendo-style sound effects library for KeyQuest typing games.

This module provides rich, retro-style sound generation using NumPy waveforms.
All sounds are procedurally generated - no audio files needed!
"""

import numpy as np


# ============ WAVEFORM GENERATORS ============

def sine_wave(freq, duration, sample_rate=44100):
    """Pure sine wave (soft, mellow tone)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)


def square_wave(freq, duration, sample_rate=44100):
    """Square wave (harsh, classic 8-bit style)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return np.sign(np.sin(2 * np.pi * freq * t))


def triangle_wave(freq, duration, sample_rate=44100):
    """Triangle wave (softer than square, brighter than sine)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phase = (freq * t) % 1.0
    return 2 * np.abs(2 * phase - 1) - 1


def pulse_wave(freq, duration, duty_cycle=0.5, sample_rate=44100):
    """Pulse wave with adjustable duty cycle (variable tone color)."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phase = (freq * t) % 1.0
    return np.where(phase < duty_cycle, 1.0, -1.0)


# ============ EFFECTS ============

def apply_envelope(wave, attack=0.01, decay=0.05, sustain_level=0.7, release=0.1, sample_rate=44100):
    """Apply ADSR envelope to wave for musical shaping."""
    total_samples = len(wave)

    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = max(0, total_samples - attack_samples - decay_samples - release_samples)

    envelope = np.ones(total_samples)

    # Attack: 0 to 1
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)

    # Decay: 1 to sustain_level
    if decay_samples > 0:
        start = attack_samples
        end = start + decay_samples
        envelope[start:end] = np.linspace(1, sustain_level, decay_samples)

    # Sustain: constant level
    if sustain_samples > 0:
        start = attack_samples + decay_samples
        end = start + sustain_samples
        envelope[start:end] = sustain_level

    # Release: sustain_level to 0
    if release_samples > 0:
        start = attack_samples + decay_samples + sustain_samples
        actual_release_samples = min(release_samples, total_samples - start)
        if actual_release_samples > 0:
            envelope[start:start+actual_release_samples] = np.linspace(sustain_level, 0, actual_release_samples)

    return wave * envelope


def apply_vibrato(wave, vibrato_freq=5, depth=0.02, sample_rate=44100):
    """Add vibrato (frequency wobble) to wave."""
    t = np.linspace(0, len(wave)/sample_rate, len(wave), endpoint=False)
    modulation = 1 + depth * np.sin(2 * np.pi * vibrato_freq * t)
    return wave * modulation


def pitch_slide(start_freq, end_freq, duration, wave_func=sine_wave, sample_rate=44100):
    """Create a pitch-sliding sound effect."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    freq = start_freq + (end_freq - start_freq) * (t / duration)
    # Create instantaneous phase
    phase = np.cumsum(2 * np.pi * freq / sample_rate)
    return np.sin(phase)


# ============ GAME SOUND EFFECTS ============

def letter_hit():
    """Quick pop sound when letter is typed correctly - like Mario hitting a block."""
    # Quick rising pitch like hitting a coin block
    wave = pitch_slide(988, 1319, 0.04)  # B5 to E6 (Mario-style)
    wave = apply_envelope(wave, attack=0.002, decay=0.015, sustain_level=0.2, release=0.023)
    return (0.45 * wave).astype(np.float32)


def letter_miss():
    """Harsh buzz for missing a letter - like taking damage in Megaman."""
    # Use square wave for harsh retro sound
    wave = square_wave(200, 0.12)
    # Add some frequency modulation for damage effect
    wave = apply_vibrato(wave, vibrato_freq=30, depth=0.15)
    wave = apply_envelope(wave, attack=0.001, decay=0.05, sustain_level=0.3, release=0.07)
    return (0.4 * wave).astype(np.float32)


def combo_sound(combo_level):
    """Escalating combo sounds - rising arpeggio like collecting items in Kid Icarus."""
    # Create a quick 2-note arpeggio that gets higher with combo level
    base_freq = 659  # E5
    second_freq = base_freq * (1.3 + (combo_level * 0.1))

    # Two quick notes in succession
    wave1 = pulse_wave(base_freq, 0.05, duty_cycle=0.25)
    wave1 = apply_envelope(wave1, attack=0.002, decay=0.02, sustain_level=0.3, release=0.028)

    wave2 = pulse_wave(second_freq, 0.06, duty_cycle=0.25)
    wave2 = apply_envelope(wave2, attack=0.002, decay=0.025, sustain_level=0.35, release=0.033)

    combined = np.concatenate([wave1, wave2])
    return (0.45 * combined).astype(np.float32)


def powerup_sound():
    """Fast ascending arpeggio for power-ups - Megaman E-Tank style."""
    # Fast rising arpeggio with pulse waves (classic Megaman sound)
    notes = [523, 659, 784, 1047, 1319]  # C5-E5-G5-C6-E6
    dur = 0.06

    tones = []
    for i, freq in enumerate(notes):
        # Vary duty cycle for richer sound
        duty = 0.25 if i % 2 == 0 else 0.125
        wave = pulse_wave(freq, dur, duty_cycle=duty)
        wave = apply_envelope(wave, attack=0.003, decay=0.02, sustain_level=0.4, release=0.037)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.4 * combined).astype(np.float32)


def life_lost():
    """Sad descending sound for losing a life - like Mario losing a life."""
    # Classic descending arpeggio like Mario death
    notes = [659, 622, 587, 554, 523, 494, 440]  # E5 down to A4
    dur = 0.08

    tones = []
    for freq in notes:
        wave = triangle_wave(freq, dur)
        wave = apply_envelope(wave, attack=0.005, decay=0.03, sustain_level=0.5, release=0.045)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.45 * combined).astype(np.float32)


def game_over():
    """Classic game over - Castlevania/NES style death theme."""
    # Dramatic descending sequence like classic NES game over
    notes = [587, 554, 494, 440, 392, 349, 330, 294]  # D5 down to D4
    dur = 0.15

    tones = []
    for i, freq in enumerate(notes):
        # Use pulse wave for retro feel
        wave = pulse_wave(freq, dur, duty_cycle=0.5)
        # Longer envelope on last note
        if i == len(notes) - 1:
            wave = apply_envelope(wave, attack=0.01, decay=0.08, sustain_level=0.5, release=0.4)
        else:
            wave = apply_envelope(wave, attack=0.01, decay=0.06, sustain_level=0.5, release=0.08)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.45 * combined).astype(np.float32)


def level_start():
    """Energetic fanfare for starting a level - like Mario level start."""
    # Quick ascending arpeggio: C-E-G
    notes = [523, 659, 784]  # C5-E5-G5
    dur = 0.12

    tones = []
    for i, freq in enumerate(notes):
        wave = pulse_wave(freq, dur, duty_cycle=0.25)
        # Longer final note for emphasis
        if i == len(notes) - 1:
            wave = apply_envelope(wave, attack=0.01, decay=0.04, sustain_level=0.6, release=0.07)
        else:
            wave = apply_envelope(wave, attack=0.01, decay=0.03, sustain_level=0.5, release=0.08)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.4 * combined).astype(np.float32)


def level_complete():
    """Victory fanfare for completing a level."""
    # Triumphant melody: G-C-E-G-C
    notes = [784, 1047, 1319, 1568, 2093]
    dur = 0.18

    tones = []
    for i, freq in enumerate(notes):
        wave = pulse_wave(freq, dur, duty_cycle=0.25)
        # Longer final note
        if i == len(notes) - 1:
            wave = apply_envelope(wave, attack=0.02, decay=0.05, sustain_level=0.7, release=0.1)
        else:
            wave = apply_envelope(wave, attack=0.01, decay=0.05, sustain_level=0.5, release=0.1)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.35 * combined).astype(np.float32)


def menu_move():
    """Quick blip for menu navigation."""
    wave = square_wave(800, 0.03)
    wave = apply_envelope(wave, attack=0.002, decay=0.01, sustain_level=0.3, release=0.018)
    return (0.3 * wave).astype(np.float32)


def menu_select():
    """Confirmation beep for menu selection."""
    wave = pulse_wave(1200, 0.12, duty_cycle=0.5)
    wave = apply_envelope(wave, attack=0.01, decay=0.04, sustain_level=0.4, release=0.07)
    return (0.35 * wave).astype(np.float32)


def coin_collect():
    """Classic coin collection sound - rising arpeggio."""
    notes = [988, 1319]  # B5 to E6
    dur = 0.08

    tones = []
    for freq in notes:
        wave = square_wave(freq, dur)
        wave = apply_envelope(wave, attack=0.01, decay=0.03, sustain_level=0.3, release=0.04)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.4 * combined).astype(np.float32)


def speed_up():
    """Rapidly ascending alert for speed increase - like DK barrel rolling."""
    # Quick ascending chromatic run with square wave
    notes = [523, 587, 659, 784, 880, 1047]  # C5 up to C6
    dur = 0.035

    tones = []
    for freq in notes:
        wave = square_wave(freq, dur)
        wave = apply_envelope(wave, attack=0.002, decay=0.015, sustain_level=0.3, release=0.018)
        tones.append(wave)

    combined = np.concatenate(tones)
    return (0.4 * combined).astype(np.float32)


def countdown_beep(number):
    """Different beeps for countdown (3, 2, 1, GO!)."""
    if number == 0:  # GO!
        freq = 1200
        dur = 0.3
    else:
        freq = 600 + (number * 50)
        dur = 0.15

    wave = square_wave(freq, dur)
    wave = apply_envelope(wave, attack=0.01, decay=0.05, sustain_level=0.6, release=0.08)
    return (0.45 * wave).astype(np.float32)


def warning_beep():
    """Urgent warning sound (alternating high-low)."""
    # Alternating frequencies
    wave1 = square_wave(1000, 0.1)
    wave2 = square_wave(700, 0.1)

    combined = np.concatenate([wave1, wave2, wave1])
    combined = apply_envelope(combined, attack=0.01, decay=0.1, sustain_level=0.6, release=0.18)
    return (0.4 * combined).astype(np.float32)


# Musical notes reference for creating melodies
NOTES = {
    'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392, 'A4': 440, 'B4': 494,
    'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698, 'G5': 784, 'A5': 880, 'B5': 988,
    'C6': 1047, 'D6': 1175, 'E6': 1319, 'F6': 1397, 'G6': 1568,
}
