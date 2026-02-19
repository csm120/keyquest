# Procedural Music Generation Research for KeyQuest

**Last Updated**: 2025-11-10
**Purpose**: Comprehensive research on implementing dynamic, procedurally-generated, adaptive music for KeyQuest

---

## Executive Summary

This document consolidates research on implementing **procedural music generation** for KeyQuest - a system that creates fresh, never-repeating background music that adapts dynamically to typing performance. The music would be:

- **Procedurally Generated**: Algorithmic composition based on musical rules, not pre-recorded loops
- **Always Fresh**: Never repeats exactly the same way twice
- **Adaptive**: Responds to WPM, accuracy, combos, and game state
- **NES/SNES Authentic**: Uses pulse, triangle, and noise channels like classic Nintendo games
- **Screen Reader Friendly**: Low volume, ducking, easy disable
- **Zero File Size**: Generated in real-time using NumPy synthesis

---

## Table of Contents

1. [Current Audio Architecture in KeyQuest](#current-audio-architecture)
2. [NES/SNES Sound Synthesis Foundation](#nessnes-synthesis-foundation)
3. [Procedural Music Generation Techniques](#procedural-generation-techniques)
4. [Adaptive Music Systems](#adaptive-music-systems)
5. [Python Libraries and Tools](#python-libraries-and-tools)
6. [Implementation Strategy for KeyQuest](#implementation-strategy)
7. [References and Resources](#references)

---

## Current Audio Architecture in KeyQuest

### Koji Kondo Two-Tier Philosophy

KeyQuest already implements Nintendo composer Koji Kondo's design philosophy:

**TIER 1 - During Active Typing** (rhythm-matched, instant feedback):
- Correct key: ~80ms (Mario coin sound with harmonics)
- Wrong key: ~130ms (Duck Hunt miss, 880Hz descending)
- Progress tone: ~80ms (rising pitch G5→E6 based on completion)
- Item complete: ~240ms (3 rising tones G5→C6→E6)

**TIER 2 - Dialog Pops Up** (celebratory, elaborate):
- Victory (lesson complete): ~780ms (Mario 1-Up with octave harmonics)
- Unlock (new lesson): ~540ms (melodic jingle with chords)
- Badge (badge earned): ~420ms (3-note coin jingle)
- Level up: ~560ms (PowerUp rising arpeggio)
- Quest complete: ~960ms (grand fanfare with chords)
- Timeout: ~1400ms (neutral descending melody)

### Existing Synthesis Capabilities

**Current Implementation** (`modules/audio_manager.py` and `games/sounds.py`):

✅ **Waveform Generators**:
- `sine_wave()` - Pure sine (soft, mellow)
- `square_wave()` - Harsh, classic 8-bit
- `triangle_wave()` - Softer than square, brighter than sine
- `pulse_wave()` - Adjustable duty cycle (0.125, 0.25, 0.5)

✅ **Effects**:
- `apply_envelope()` - Full ADSR (Attack, Decay, Sustain, Release)
- `apply_vibrato()` - Frequency wobble
- `pitch_slide()` - Glissando effects

✅ **Harmonic Blending**:
- Fundamental + octave harmonics
- Chord arpeggiation (fake polyphony)

✅ **NumPy-based**:
- 44100 Hz sample rate
- Real-time synthesis
- Pygame mixer integration

### What's Missing for Music

❌ LFSR noise generator (for NES-style percussion)
❌ Music composition engine (motif generation)
❌ Markov chain system (probabilistic note selection)
❌ Layer management (adding/removing instrument tracks)
❌ Tempo/key management
❌ Crossfading/transition smoothing
❌ Volume ducking for speech

---

## NES/SNES Sound Synthesis Foundation

### NES Audio Palette (2A03 Chip)

The NES has 5 audio channels:

1. **Pulse Wave 1** (lead melody)
   - 12.5%, 25%, 50%, 75% duty cycles
   - Envelope generator
   - Pitch sweep capability

2. **Pulse Wave 2** (harmony/echo)
   - Same capabilities as Pulse 1
   - Used for harmony or alternate melody

3. **Triangle Wave** (bass)
   - No volume control (always same amplitude)
   - Used for bass lines and low-frequency effects
   - Smoother than pulse waves

4. **Noise Channel** (percussion/effects)
   - Linear Feedback Shift Register (LFSR)
   - 15-bit or 7-bit mode
   - Used for drums, explosions, wind

5. **DPCM Sample** (optional, rare)
   - Low-rate sample playback
   - Used sparingly due to memory constraints

### SNES Audio Palette (S-SMP/S-DSP)

The SNES has 8 sample-based channels:
- 8-voice stereo sampling
- 32 kHz sample rate
- Low-bit samples (typically 4-bit ADPCM)
- Hardware ADSR envelopes
- Echo/reverb effects

### Synthesis Rules for Authenticity

**Sample Rate**:
- 32000 Hz for NES-style (reduces CPU load)
- 44100 Hz for SNES-style (better quality)

**Bit Depth**:
- Quantize to 8-bit for NES authenticity
- 16-bit for SNES-style

**Waveforms**:

```python
# Pulse wave with duty cycle
def pulse(freq, ms, duty, vol):
    n = int(SR * ms / 1000)
    t = (np.arange(n) * freq / SR) % 1.0
    wave = np.where(t < duty, 1.0, -1.0) * vol
    return (wave * 32767).astype(np.int16)

# Triangle wave
def tri(freq, ms, vol):
    n = int(SR * ms / 1000)
    t = (np.arange(n) * freq / SR) % 1.0
    wave = 2 * np.abs(2 * t - 1) - 1
    return (wave * vol * 32767).astype(np.int16)

# LFSR noise (NES-authentic)
def nes_noise(ms, vol):
    n = int(SR * ms / 1000)
    reg = 1
    buf = np.zeros(n, dtype=np.int16)
    for i in range(n):
        bit = (reg ^ (reg >> 1)) & 1
        reg = (reg >> 1) | (bit << 14)
        buf[i] = (1 if (reg & 1) else -1) * int(32767 * vol)
    return buf
```

**Fake Chords (Arpeggiation)**:
```python
# NES can't play chords - must arpeggiate rapidly
def arpeggio(root_hz, intervals, step_ms, cycles, duty):
    frames = []
    tones = [root_hz * r for r in intervals]
    for _ in range(cycles):
        for f in tones:
            frames.append(pulse(f, step_ms, duty, 0.25))
    return np.concatenate(frames)
```

**Envelope Timing**:
- Very fast attack (0-2 ms)
- Fast decay (40-120 ms)
- Low sustain level
- Short release

**Note Duration**:
- 50-200 ms typical for melodic cues
- Rhythmic, percussive, clear

### Recommended Voice Layout

- **Pulse A**: Lead melody (main motif)
- **Pulse B**: Harmony or counter-melody
- **Triangle**: Bass line or movement cues
- **Noise**: Percussion, UI ticks, drums

---

## Procedural Music Generation Techniques

### 1. Markov Chains (Probability-Based)

**Concept**: Generate note sequences based on probability tables trained on musical patterns.

**How It Works**:
```python
# Transition probabilities from note to note
transitions = {
    'C': {'D': 0.4, 'E': 0.3, 'G': 0.2, 'A': 0.1},
    'E': {'D': 0.3, 'F': 0.4, 'G': 0.3},
    'G': {'A': 0.3, 'F': 0.2, 'E': 0.3, 'C': 0.2}
}

def next_note(current_note):
    return random.choices(
        list(transitions[current_note].keys()),
        weights=list(transitions[current_note].values())
    )[0]
```

**Advantages**:
- Always produces musically sensible sequences
- Can learn from existing melodies
- Lightweight computation
- Controllable via probability weights

**Disadvantages**:
- Requires training data or manual probability tables
- Can become repetitive if not enough variation
- No long-term structure (phrase awareness)

**Research Sources**:
- "Markov Chains for Computer Music Generation" (Claremont, 2021)
- "Using Linear Algebra and Markov Chains to Algorithmically Generate Music" (Medium, 2023)
- Stack Overflow: "Using Markov chains for procedural music generation"

**Best For**: Melodic phrase generation, rhythm patterns, chord progressions

### 2. L-Systems (Recursive Growth)

**Concept**: Use Lindenmayer Systems (plant growth algorithms) to generate self-similar musical structures.

**How It Works**:
```python
# Start with axiom, apply production rules
axiom = "C"
rules = {
    'C': "CEG",    # C expands to C-E-G chord
    'E': "GB",     # E expands to G-B interval
    'G': "CD"      # G expands to C-D step
}

# Iteration 1: C
# Iteration 2: CEG
# Iteration 3: CEG-GB-CD
# Organic fractal-like growth
```

**Advantages**:
- Creates self-similar, organic structures (like real music)
- Natural phrase structure emerges
- Fractal properties = interesting variation
- Minimal code, infinite possibilities

**Disadvantages**:
- Can become too complex quickly
- Requires musical interpretation of symbols
- Less direct control than Markov chains

**Research Sources**:
- "Score generation with L-systems" (Przemyslaw Prusinkiewicz, 1986)
- "Growing Music: Musical Interpretations of L-Systems" (SpringerLink, 2006)
- "Evolving L-Systems with Musical Notes" (2016)
- "Creating Fractal Music in Very Few Lines of Code" (David Koelle, Medium)

**Best For**: Phrase structure, theme variations, organic development

### 3. Cellular Automata (Emergent Patterns)

**Concept**: Use grid-based systems like Conway's Game of Life or Rule 110 to generate emergent musical patterns.

**How It Works**:
```python
# Map grid cells to musical parameters
# Live cell = note plays, dead cell = silence
# Cell position = pitch (row) and time (column)

grid = initialize_game_of_life()
for generation in range(16):  # 16 bars
    grid = evolve(grid)
    for row, cells in enumerate(grid):
        pitch = scale[row % len(scale)]
        for col, alive in enumerate(cells):
            if alive:
                play_note(pitch, beat=col)
```

**Advantages**:
- Emergent complexity from simple rules
- Unpredictable but structured patterns
- Visually interesting (can show grid to user)
- Musical "chaos" at edge of order

**Disadvantages**:
- Hard to control musical outcome
- Can produce non-musical results
- Requires careful mapping to musical parameters

**Research Sources**:
- "Game of Life Music Synthesizer" (Cornell ECE 5760)
- "Cellular Music: An Interactive Game of Life Sequencer" (ACM, 2018)
- "Listening to Elementary Cellular Automata" (Medium, 2019)
- "Discussing the Creativity of AUTOMATONE" (ResearchGate, 2024)

**Examples**:
- WolframTones (Stephen Wolfram's online CA music generator)
- Grant Muller's Game of Life MIDI Sequencer
- GlitchDS (Nintendo DS cellular automata music)

**Best For**: Ambient textures, rhythmic patterns, experimental soundscapes

### 4. WaveFunctionCollapse (Constraint-Based)

**Concept**: Use constraint solving to generate music that satisfies multiple musical rules simultaneously.

**How It Works**:
```python
# Define constraints
constraints = {
    'key': 'C_major',
    'chord_progression': ['I', 'vi', 'IV', 'V'],
    'rhythm': '4/4',
    'note_range': (C4, C6),
    'avoid_leaps': True  # Prefer stepwise motion
}

# WFC resolves constraints to generate valid music
music = wavefunction_collapse(constraints)
```

**Advantages**:
- Guarantees musical coherence
- Multiple constraints enforced simultaneously
- Mixed-initiative (user can set some notes, algorithm fills rest)
- Very flexible - can encode any musical rule

**Disadvantages**:
- More complex to implement
- Computationally expensive
- Can fail to find solution if constraints conflict

**Research Sources**:
- "Harmony in Hierarchy: Mixed-Initiative Music Composition Inspired by WFC" (SpringerLink, 2024)
- "Procedural mixed-initiative music composition with hierarchical WFC" (ResearchGate, 2023)
- "Procedural Generation of Several Instrument Music Pieces with Hierarchical WFC" (TU Delft, 2024)
- "WaveFunctionCollapse is Constraint Solving in the Wild" (Isaac Karth)

**Best For**: Complex multi-instrument compositions, ensuring music theory correctness

### 5. Algorithmic Bass Lines & Patterns

**Concept**: Use deterministic algorithms for supporting parts (bass, drums, arpeggios).

**Common Patterns**:

```python
# Walking bass (jazz-style)
def walking_bass(chord_progression):
    bass_line = []
    for chord in chord_progression:
        root = chord.root
        fifth = chord.root * 1.5
        third = chord.root * 1.25
        leading = next_chord.root * 0.94  # Leading tone
        bass_line.extend([root, fifth, third, leading])
    return bass_line

# Root-fifth alternating (simple, effective)
def simple_bass(chord):
    return [chord.root, chord.root * 1.5] * 4

# Alberti bass (classical accompaniment)
def alberti_bass(chord):
    root, third, fifth = chord.notes
    return [root, fifth, third, fifth] * 2
```

**Advantages**:
- Predictable, always sounds good
- Computationally trivial
- Can vary rhythm while keeping pattern

**Best For**: Bass lines, arpeggiated accompaniment, rhythmic foundation

---

## Adaptive Music Systems

### Techniques from Game Industry

Modern video games use several techniques to make music respond to gameplay:

### 1. Vertical Orchestration (Layering)

**Concept**: Different instrument layers fade in/out based on game state.

```python
# Example: Typing game intensity
base_layer = generate_melody()  # Always playing
bass_layer = generate_bass()    # Adds when focused
harmony_layer = generate_harmony()  # Adds when accuracy > 90%
percussion_layer = generate_drums()  # Adds during combo

if wpm > 40:
    mix(base_layer, bass_layer)
if accuracy > 0.9:
    mix(base_layer, bass_layer, harmony_layer)
if in_combo:
    mix(base_layer, bass_layer, harmony_layer, percussion_layer)
```

**Example Games**:
- Banjo-Kazooie: Music layers change based on player location
- The Legend of Zelda: Additional instruments when near enemies
- Minecraft: Sparse ambient layers fade in/out

### 2. Horizontal Re-sequencing

**Concept**: Different musical sections arranged dynamically based on actions.

```python
# Example: Combat vs exploration
if in_combat:
    play_section('intense_drums')
    play_section('fast_melody')
elif exploring:
    play_section('ambient_pad')
    play_section('slow_melody')
```

**Example Games**:
- Doom (2016): Music intensity shifts based on combat state
- Hades: Battle music transitions smoothly in/out of combat

### 3. Dynamic Mixing

**Concept**: Real-time audio parameter adjustment.

```python
def adjust_music(wpm, accuracy):
    tempo = map_range(wpm, 20, 80, 90, 160)  # BPM scales with speed
    volume = map_range(accuracy, 0.5, 1.0, 0.3, 0.7)  # Louder when accurate

    if speech_active:
        music_volume *= 0.2  # Duck for accessibility

    set_tempo(tempo)
    set_volume(volume)
```

**Example Games**:
- Space Invaders (1978): First adaptive music - tempo increases over time
- Guitar Hero: Music tempo adjusts to player accuracy

### 4. Algorithmic/Generative Composition

**Concept**: Generate music in real-time rather than playback recordings.

```python
# Example: Real-time motif generation
def generate_phrase(wpm, accuracy):
    if wpm > 60:
        motif = markov_generate(energetic_chain)
        tempo = 160
    else:
        motif = markov_generate(calm_chain)
        tempo = 100

    return synthesize(motif, tempo)
```

**Example Games**:
- Spore: Uses Pure Data to generate music based on creature evolution
- No Man's Sky: Procedural soundscapes unique to each planet
- Elite Dangerous: Dynamic composition responds to gameplay

### Implementation in Wwise/FMOD

Professional game audio uses middleware:
- **Wwise** (AudioKinetic): Parameter-driven mixing, vertical remixing
- **FMOD** (Firelight): Real-time DSP, adaptive music graphs
- **iMUSE** (LucasArts, 1991): Pioneering adaptive music system

### Impact on Players

Research shows adaptive music:
- ✅ Increases immersion
- ✅ Heightens emotional engagement
- ✅ Improves player satisfaction
- ✅ Reduces repetition fatigue
- ✅ Provides subconscious performance feedback

---

## Python Libraries and Tools

### Production-Ready Libraries

**1. pycomposer** (Algorithmic Composition)
- Stochastic music theory
- GANs and Conditional GANs
- Statistical machine learning
- Requires: NumPy 1.13.3+
- Link: https://pypi.org/project/pycomposer/

**2. isobar** (Pattern Manipulation)
- Musical pattern creation and manipulation
- Built-in: Markov chains, L-systems, Euclidean rhythms
- MIDI/OSC output
- Designed for live coding
- Link: https://github.com/ideoforms/isobar

**3. music21** (Music Theory)
- Comprehensive music analysis
- MIDI parsing and generation
- Music theory objects (scales, chords, intervals)
- Notation rendering
- Perfect for constraint validation

**4. midiutil** (MIDI Generation)
- Simple MIDI file creation
- Tempo, key signature, time signature
- Multi-track support

**5. pyo** (Advanced DSP)
- Real-time audio processing
- Rich synthesis capabilities
- Effects processing
- Server-based architecture

### Supporting Libraries

**NumPy** (Essential):
- Waveform synthesis
- FFT/spectral analysis
- Array operations

**Pygame** (Already in KeyQuest):
- Mixer for playback
- Sound object creation
- Audio streaming

**SciPy** (Signal Processing):
- Filters (lowpass, highpass, bandpass)
- Convolution
- Resampling

---

## Implementation Strategy for KeyQuest

### Phase 1: Core Music Engine (Foundation)

**Goal**: Implement basic procedural music generation

**Tasks**:
1. Implement LFSR noise generator (NES-style percussion)
2. Create `music_manager.py` module
3. Build Markov chain melody generator
   - Define transition tables for C major, A minor, D Dorian
   - Implement `generate_phrase(key, length)` function
4. Implement simple algorithmic bass (root-fifth pattern)
5. Create 8-bar loop system with crossfading

**Deliverables**:
- LFSR noise function
- Markov melody generator
- Simple bass generator
- Loop manager with crossfade

**Success Criteria**:
- Can generate 8-bar melody that sounds musical
- Bass line follows harmonic structure
- Loops seamlessly without clicks

### Phase 2: NES Voice Layout (4-Channel)

**Goal**: Implement full NES-style 4-channel system

**Tasks**:
1. Create channel mixer (Pulse A, Pulse B, Triangle, Noise)
2. Implement pulse wave duty cycle variation
3. Add percussion patterns using noise channel
4. Create arpeggiated chord system for harmony
5. Implement volume balancing (melody louder, bass quieter)

**Deliverables**:
- 4-channel mixer
- Pulse wave with duty cycles (0.125, 0.25, 0.5)
- Noise percussion patterns
- Arpeggio chord generator

**Success Criteria**:
- All 4 channels can play simultaneously
- Pulse waves sound distinct from each other
- Noise channel provides rhythmic foundation

### Phase 3: Adaptive System (Dynamic Response)

**Goal**: Make music respond to typing performance

**Tasks**:
1. Implement tempo scaling (90-160 BPM based on WPM)
2. Add layer management:
   - Base: Melody only
   - +Bass: When focused/typing
   - +Harmony: When accuracy > 90%
   - +Percussion: When combo active
3. Create smooth crossfading for layer changes
4. Implement volume ducking for speech
5. Add mode detection (Speed Test, Practice, Games)

**Deliverables**:
- Tempo adapter
- Layer controller
- Crossfade engine
- Speech ducking system

**Success Criteria**:
- Music speeds up noticeably when typing fast
- Layers add smoothly without jarring transitions
- Music ducks immediately when speech plays
- Different moods for different modes

### Phase 4: Advanced Generation (More Techniques)

**Goal**: Add variety and sophistication

**Tasks**:
1. Implement L-system phrase structure generator
2. Add multiple Markov chains (melody, rhythm, dynamics)
3. Create micro-timing variation (humanization)
4. Implement chord progression system
5. Add key modulation (shift between C major, A minor, etc.)
6. Create motif variation system

**Deliverables**:
- L-system generator
- Multiple Markov chains
- Humanization engine
- Chord progression manager
- Key modulation system

**Success Criteria**:
- Music has recognizable structure (verse/chorus feel)
- Enough variation that 10-minute session doesn't repeat
- Chord changes feel natural
- Timing feels organic, not robotic

### Phase 5: Polish & Integration

**Goal**: Make it production-ready

**Tasks**:
1. Optimize performance (pre-generate, cache patterns)
2. Add user controls in Options menu:
   - Enable/Disable music
   - Volume control
   - Intensity (how adaptive it is)
3. Create "Learn Music System" dialog
4. Integrate with shop (unlock music themes)
5. Add music presets (Energetic, Calm, Retro, Modern)
6. Extensive testing with screen readers

**Deliverables**:
- Performance optimizations
- User controls
- Documentation dialog
- Shop integration
- Music presets

**Success Criteria**:
- No performance impact on typing
- Easy to disable for users who don't want it
- Screen reader users report no interference
- Music adds to experience without distracting

---

## Technical Architecture

### Proposed Module Structure

```
modules/
├── audio_manager.py (existing - sound effects)
└── music_manager.py (new - procedural music)
    ├── MusicEngine
    │   ├── generate_phrase()
    │   ├── generate_bass()
    │   ├── generate_harmony()
    │   └── generate_percussion()
    ├── MarkovChain
    │   ├── load_transitions()
    │   ├── generate_sequence()
    │   └── train_from_midi()
    ├── LSystemGenerator
    │   ├── define_rules()
    │   ├── iterate()
    │   └── interpret_musically()
    ├── LayerMixer
    │   ├── add_layer()
    │   ├── remove_layer()
    │   ├── crossfade()
    │   └── set_volumes()
    └── AdaptiveController
        ├── update_tempo()
        ├── update_layers()
        ├── check_speech()
        └── duck_volume()
```

### Data Flow

```
Typing Performance
    ↓
AdaptiveController (reads WPM, accuracy, combo)
    ↓
MusicEngine (generates new phrases based on state)
    ↓
LayerMixer (combines channels, applies crossfade)
    ↓
AudioManager (plays through pygame mixer)
    ↓
User hears adaptive music
```

### Performance Considerations

**CPU Usage**:
- Generate in background thread
- Pre-generate next phrase while current plays
- Cache common patterns
- Use 32kHz sample rate (not 44.1kHz) for music

**Memory Usage**:
- Keep only current + next phrase in memory
- Don't cache entire compositions
- LFSR noise can be regenerated cheaply

**Latency**:
- Generate 8-bar phrases (8-16 seconds)
- Start generating next phrase at bar 4 of current
- Crossfade last 2 bars with next phrase

---

## Musical Constraints for Quality

### Scale/Key System

```python
SCALES = {
    'C_major': [C, D, E, F, G, A, B],
    'A_minor': [A, B, C, D, E, F, G],
    'D_dorian': [D, E, F, G, A, B, C],
    'E_phrygian': [E, F, G, A, B, C, D],
}

CHORD_PROGRESSIONS = {
    'pop': ['I', 'vi', 'IV', 'V'],      # Very common
    'rock': ['I', 'V', 'vi', 'IV'],     # Pachelbel's Canon
    'jazz': ['ii', 'V', 'I'],           # Turnaround
    'energetic': ['I', 'IV', 'V', 'I'], # Classic
}
```

### Melodic Constraints

```python
CONSTRAINTS = {
    'prefer_stepwise': 0.7,  # 70% of intervals are steps (C→D)
    'max_leap': 7,           # No leaps larger than 7 semitones
    'end_on_tonic': True,    # Phrases resolve to root note
    'avoid_tritone': True,   # No F→B or B→F (unless jazz mode)
    'phrase_length': 8,      # 8-note phrases (2 bars in 4/4)
}
```

### Rhythm Patterns

```python
RHYTHMS = {
    'simple': [1, 1, 1, 1, 1, 1, 1, 1],           # Quarter notes
    'energetic': [0.5, 0.5, 1, 0.5, 0.5, 1, 1],   # Mixed eighths/quarters
    'syncopated': [1, 0.5, 0.5, 1, 1, 0.5, 0.5],  # Off-beat emphasis
}
```

---

## Accessibility Considerations

### Screen Reader Compatibility

**Volume Management**:
- Background music: 20-30% volume (subtle)
- When speech plays: Duck to 5% or mute entirely
- User can adjust or disable completely

**Speech Priority System** (already in KeyQuest):
```python
if speech.is_speaking() or speech.has_priority():
    music_volume = 0.05  # Near silent
else:
    music_volume = user_preference  # 0.2-0.3 default
```

**Non-Visual Cues**:
- Music shouldn't convey critical information
- Tempo/intensity changes are enhancements, not requirements
- All gameplay works identically with music off

### User Controls

Minimum required:
- [ ] Enable/Disable toggle (default: disabled)
- [ ] Volume slider (0-100%)
- [ ] "Duck music when speaking" checkbox (default: on)
- [ ] Intensity slider (how adaptive it is)

Advanced options:
- [ ] Music style preset (Energetic, Calm, Retro)
- [ ] Complexity (Simple, Medium, Complex)
- [ ] Percussion enable/disable

---

## References and Resources

### Academic Papers

1. "Markov Chains for Computer Music Generation" - Claremont Colleges, 2021
2. "Score generation with L-systems" - Przemyslaw Prusinkiewicz, ICMC 1986
3. "Harmony in Hierarchy: Mixed-Initiative Music Composition Inspired by WFC" - SpringerLink, 2024
4. "Procedural mixed-initiative music composition with hierarchical Wave Function Collapse" - ResearchGate, 2023
5. "Growing Music: Musical Interpretations of L-Systems" - SpringerLink, 2006
6. "Cellular Music: An Interactive Game of Life Sequencer" - ACM, 2018
7. "Adaptive Music Composition for Games" - IEEE Transactions on Games, 2019

### Online Resources

1. Wikipedia: "Algorithmic composition" - https://en.wikipedia.org/wiki/Algorithmic_composition
2. Wikipedia: "Adaptive music" - https://en.wikipedia.org/wiki/Adaptive_music
3. "The history of adaptive music in video games" - Splice Blog
4. "Generating Music Using Markov Chains" - HackerNoon
5. "Creating Fractal Music in Very Few Lines of Code" - Medium (David Koelle)
6. "Listening to Elementary Cellular Automata" - Medium
7. "Deep Dive: A framework for generative music in video games" - Game Developer

### Software and Libraries

1. **pycomposer** - https://pypi.org/project/pycomposer/
2. **isobar** - https://github.com/ideoforms/isobar
3. **music21** - http://web.mit.edu/music21/
4. **Wwise** - https://www.audiokinetic.com/products/wwise/
5. **FMOD** - https://www.fmod.com/
6. **WolframTones** - http://tones.wolfram.com/

### Game Examples

1. **Space Invaders** (1978) - First adaptive music (tempo increases)
2. **Banjo-Kazooie** (N64) - Vertical orchestration layers
3. **Spore** (2008) - Real-time procedural generation with Pure Data
4. **No Man's Sky** (2016) - Unique soundscape per planet
5. **Hades** (2020) - Smooth combat transitions
6. **Minecraft** (2011) - Sparse ambient generation

### Articles and Tutorials

1. "Algorithmic Composition" - https://junshern.github.io/algorithmic-music-tutorial/
2. "Mastering Algorithmic Composition in Sound Synthesis" - Number Analytics
3. "Python for Music Composition: Generating Melodies with Code" - MoldStud
4. "My Approach to Automatic Musical Composition" - flujoo.github.io
5. Stack Overflow: "Procedural music generation techniques"
6. "Adaptive Music in Video Games and How It Impacts Player Engagement" - CSUMB

---

## Conclusion

Procedural music generation for KeyQuest is **highly feasible** and would be a **significant enhancement** to the gamification experience. The technical foundation already exists (NumPy synthesis, waveform generators, ADSR envelopes), and only the composition logic needs to be added.

**Recommended Approach**:
1. Start with **Markov chains** for melody generation (proven, simple, effective)
2. Use **algorithmic patterns** for bass/percussion (deterministic, always works)
3. Add **vertical layering** for adaptivity (layers add based on performance)
4. Implement **tempo scaling** for responsiveness (speeds up with WPM)
5. Ensure **screen reader compatibility** (ducking, disable option, low volume)

**Expected Result**: Every KeyQuest session has unique, adaptive, NES-style music that responds to typing performance in real-time, never repeats exactly the same way, and enhances engagement without interfering with accessibility.

The music would be:
- ✅ **Fresh** - Never exactly the same twice
- ✅ **Musical** - Constrained by music theory rules
- ✅ **Adaptive** - Responds to WPM, accuracy, combos
- ✅ **Authentic** - True NES/SNES sound palette
- ✅ **Accessible** - Speech-friendly, easy to disable
- ✅ **Tiny** - Zero audio files, pure synthesis

---

*This research consolidates information from Music.md, docs/dev/HANDOFF.md, modules/audio_manager.py, games/sounds.py, and online sources researched on 2025-11-10.*
