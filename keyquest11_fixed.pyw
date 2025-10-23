# KeyQuest 11 (Fixed)
#
# Major improvements over KeyQuest 9:
# - System theme detection (dark/light/high contrast), defaults to white on black
# - Adaptive difficulty based on real-time performance tracking
# - Lesson progression starts from tutorial keys (arrows, space, enter)
# - Builds words, phrases, and sentences as skill progresses
# - Gamification with encouragement and smart pacing
# - Non-consecutive key tracking for advancement
# - Improved tutorial with gradual Enter integration
# - Expanded speed test sentences for fast typers
# - Smart review system: slow down on struggles, give wins, return to challenges
# - FIXED: Restored "remaining text" feedback on typing errors from KQ9

import sys
import time
import random
import threading
import traceback
import json
from dataclasses import dataclass, field
from collections import Counter, deque
from typing import List, Dict, Set, Tuple

# ---- Error logging ----
LOG_FILE = "keyquest_error.log"

def log_exception(e: BaseException):
    """Append an exception traceback to the log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("=== Unhandled exception ===\n")
            traceback.print_exc(file=f)
            f.write("\n")
    except Exception:
        pass

# ---- Optional accessibility dependencies ----
try:
    from accessible_output2.outputs.auto import Auto as AO2Auto
except Exception:
    AO2Auto = None

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import darkdetect
except Exception:
    darkdetect = None

# Pygame
import pygame
import pygame.freetype
import numpy as np

# ----------------- Config -----------------
SCREEN_W, SCREEN_H = 900, 600

# Theme colors - detect system theme or default to dark (white on black)
def detect_theme():
    """Detect system theme, default to dark mode (white on black)."""
    if darkdetect:
        try:
            theme = darkdetect.theme()
            if theme == "Light":
                return "light"
            elif theme == "Dark":
                return "dark"
        except:
            pass
    # Default to dark (white on black) as requested
    return "dark"

SYSTEM_THEME = detect_theme()

if SYSTEM_THEME == "light":
    BG = (255, 255, 255)
    FG = (0, 0, 0)
    ACCENT = (0, 100, 200)
    HILITE = (200, 220, 255)
else:  # dark or high contrast
    BG = (0, 0, 0)
    FG = (255, 255, 255)  # Pure white on black for maximum contrast
    ACCENT = (180, 220, 255)
    HILITE = (60, 100, 160)

FONT_NAME = None
TITLE_SIZE = 36
TEXT_SIZE = 28
SMALL_SIZE = 20

LESSON_BATCH = 8
TEST_SECONDS = 60

# Expanded test sentences for fast typers
TEST_SENTENCES = [
    "Keep going.",
    "Stay relaxed.",
    "Type with care.",
    "Small steps add up.",
    "Find a steady pace.",
    "Focus and breathe.",
    "Hands on home row.",
    "Make few errors.",
    "Stay calm.",
    "You can do this.",
    "Practice makes perfect.",
    "One key at a time.",
    "Build your skills.",
    "Trust the process.",
    "You are improving.",
    "Stay consistent.",
    "Take your time.",
    "Accuracy matters.",
    "Speed will come.",
    "Believe in yourself.",
    "Every try counts.",
    "Learn from mistakes.",
    "Progress not perfection.",
    "You got this.",
    "Keep practicing.",
    "Stay positive.",
    "One step forward.",
    "Celebrate small wins.",
    "You are capable.",
    "Never give up.",
]

# NEW LESSON PROGRESSION: Start from tutorial keys
# Stage 0: Tutorial keys (arrows not typed, but space/enter are)
# Stage 1: Add left home row gradually
STAGE_LETTERS = [
    {" "},                      # Stage 0: Space (from tutorial)
    {"a", "s"},                 # Stage 1: Left home - pinky, ring
    {"d", "f"},                 # Stage 2: Left home - middle, index
    {"j", "k"},                 # Stage 3: Right home - index, middle
    {"l", ";"},                 # Stage 4: Right home - ring, pinky
    {"g", "h"},                 # Stage 5: Inner home row
    {"e", "r"},                 # Stage 6: Left top row - middle, index
    {"u", "i"},                 # Stage 7: Right top row - index, middle
    {"q", "w"},                 # Stage 8: Left top row - pinky, ring
    {"o", "p"},                 # Stage 9: Right top row - ring, pinky
    {"t", "y"},                 # Stage 10: Mid top row
    {"c", "v"},                 # Stage 11: Left bottom - middle, index
    {"n", "m"},                 # Stage 12: Right bottom - index, middle
    {"z", "x"},                 # Stage 13: Left bottom - pinky, ring
    {",", "."},                 # Stage 14: Right bottom - ring, pinky
    {"b"},                      # Stage 15: Center bottom
    {"1", "2", "3"},            # Stage 16: Left numbers
    {"4", "5", "6"},            # Stage 17: Mid numbers
    {"7", "8", "9", "0"},       # Stage 18: Right numbers
    {"'", "/"},                 # Stage 19: Punctuation
]

# Common words for each stage (once user shows proficiency)
STAGE_WORDS = {
    0: [""],  # Just space
    1: ["as", "a"],
    2: ["ad", "ads", "as", "dad", "sad", "fad"],
    3: ["jak", "ask", "sad", "add", "lass"],
    4: ["lad", "lass", "all", "fall", "jass", "salad"],
    5: ["had", "has", "gag", "shag", "hash", "gash"],
    6: ["red", "fed", "deer", "fear", "read", "seed"],
    7: ["rude", "fused", "used", "ruse"],
    8: ["was", "war", "wed", "weed", "sawed"],
    9: ["open", "rope", "pope", "pore", "sore"],
    10: ["type", "yet", "toy", "try", "tray"],
    # Add more as stages progress
}

# Phrases for later stages
STAGE_PHRASES = {
    6: ["read the", "feed her", "she read"],
    7: ["use it", "our jug", "pure juice"],
    8: ["we were", "was here", "ware house"],
    # Add more
}

# Tutorial config with improved Enter integration
PHASE1_KEYS = [
    ("up", pygame.K_UP),
    ("down", pygame.K_DOWN),
    ("left", pygame.K_LEFT),
    ("right", pygame.K_RIGHT),
    ("space", pygame.K_SPACE),
]

# Phase 2: Introduce Enter, then mix with everything
PHASE2_INTRO_KEYS = [("enter", pygame.K_RETURN)]
PHASE2_MIX_KEYS = PHASE1_KEYS + PHASE2_INTRO_KEYS

TUTORIAL_EACH_COUNT = 3
TUTORIAL_MIX_COUNT = 5  # Mixed practice after Enter introduction

FRIENDLY = {
    "up": "Up Arrow",
    "down": "Down Arrow",
    "left": "Left Arrow",
    "right": "Right Arrow",
    "space": "Space bar",
    "enter": "Enter",
}

HINTS = {
    "up": "Arrow pointing up, above the Down Arrow.",
    "down": "Arrow pointing down, below the Up Arrow.",
    "left": "Arrow pointing left, to the left of Right.",
    "right": "Arrow pointing right, to the right of Left.",
    "space": "Long bar in the middle at the bottom of the keyboard.",
    "enter": "Large key on the right side of the letters; often tall or L‑shaped.",
}

RELATION = {
    ("up","down"): "Try Down — one step below.",
    ("down","up"): "Try Up — one step above.",
    ("left","right"): "Try Right — the opposite direction.",
    ("right","left"): "Try Left — the opposite direction.",
    ("space","up"): "Try Up Arrow — above the Down key cluster.",
    ("space","down"): "Try Down Arrow — below the Up key.",
    ("space","left"): "Try Left Arrow — to the left of Right.",
    ("space","right"): "Try Right Arrow — to the right of Left.",
    ("up","enter"): "Try Enter — on the right side of the keyboard.",
    ("down","enter"): "Try Enter — on the right side.",
    ("left","enter"): "Try Enter — near the right edge, often tall.",
    ("right","enter"): "Try Enter — just to your right from the letters.",
    ("enter","space"): "Try Space — the long bar at the bottom.",
    ("space","enter"): "Try Enter — on the right side of the keyboard.",
}

# Encouragement messages
ENCOURAGEMENT = {
    "correct": ["Great!", "Nice!", "Perfect!", "Excellent!", "Well done!", "Good job!"],
    "streak_3": ["You're on fire!", "Three in a row!", "Keep it up!", "Awesome streak!"],
    "streak_5": ["Five correct! Amazing!", "You're crushing it!", "Fantastic!"],
    "stage_complete": ["Stage complete!", "You did it!", "Moving up!", "Great progress!"],
    "struggle": ["That's okay!", "Keep trying!", "You'll get it!", "Practice helps!"],
    "comeback": ["There you go!", "Back on track!", "Nice recovery!"],
}

# ----------------- Speech System -----------------
class Speech:
    """Speech system with AO2 priority, pyttsx3 fallback."""
    def __init__(self):
        self.enabled = True
        self._lock = threading.Lock()
        self._engine = None
        self._ao = None
        self.backend = "none"
        self._priority_until = 0.0

        if AO2Auto is not None:
            try:
                self._ao = AO2Auto()
                self.backend = "ao2"
            except Exception:
                self._ao = None

        if self._ao is None and pyttsx3 is not None:
            try:
                self._engine = pyttsx3.init()
                self.backend = "tts"
            except Exception:
                self._engine = None

    def say(self, text: str, priority: bool=False, protect_seconds: float=0.0):
        if not self.enabled or not text:
            return
        with self._lock:
            now = time.time()
            if priority:
                self._priority_until = now + protect_seconds
            else:
                if now < self._priority_until:
                    return
            try:
                if self.backend == "ao2":
                    self._ao.output(text)
                elif self.backend == "tts":
                    self._engine.stop()
                    self._engine.say(text)
                    self._engine.runAndWait()
                else:
                    print(text)
            except Exception as e:
                log_exception(e)

# ---- Audio ----
def make_tone(freq: float, dur_ms: float):
    fs = 44100
    t = np.linspace(0, dur_ms / 1000.0, int(fs * dur_ms / 1000.0), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    return wave.astype(np.float32)

def mod_ctrl(mods: int) -> bool:
    return (mods & pygame.KMOD_CTRL) != 0

# ----------------- Performance Tracking -----------------
@dataclass
class KeyPerformance:
    """Track performance for individual keys."""
    key: str
    attempts: int = 0
    correct: int = 0
    recent_attempts: deque = field(default_factory=lambda: deque(maxlen=10))

    def accuracy(self) -> float:
        if self.attempts == 0:
            return 1.0
        return self.correct / self.attempts

    def recent_accuracy(self) -> float:
        if not self.recent_attempts:
            return 1.0
        return sum(self.recent_attempts) / len(self.recent_attempts)

    def record_attempt(self, success: bool):
        self.attempts += 1
        if success:
            self.correct += 1
        self.recent_attempts.append(1 if success else 0)

@dataclass
class AdaptiveTracker:
    """Track overall performance and adapt difficulty."""
    key_performance: Dict[str, KeyPerformance] = field(default_factory=dict)
    recent_keys: deque = field(default_factory=lambda: deque(maxlen=10))  # Track last 10 keys
    consecutive_correct: int = 0
    consecutive_wrong: int = 0
    total_correct: int = 0
    total_attempts: int = 0

    def record_keystroke(self, key: str, correct: bool):
        """Record a keystroke and update adaptive metrics."""
        if key not in self.key_performance:
            self.key_performance[key] = KeyPerformance(key=key)

        self.key_performance[key].record_attempt(correct)
        self.recent_keys.append((key, correct))
        self.total_attempts += 1

        if correct:
            self.total_correct += 1
            self.consecutive_wrong = 0
            # Only count non-consecutive keys for streak
            if len(self.recent_keys) >= 2:
                if self.recent_keys[-1][0] != self.recent_keys[-2][0]:
                    self.consecutive_correct += 1
            else:
                self.consecutive_correct += 1
        else:
            self.consecutive_correct = 0
            # Only count non-consecutive keys for wrong streak
            if len(self.recent_keys) >= 2:
                if self.recent_keys[-1][0] != self.recent_keys[-2][0]:
                    self.consecutive_wrong += 1
            else:
                self.consecutive_wrong += 1

    def overall_accuracy(self) -> float:
        if self.total_attempts == 0:
            return 1.0
        return self.total_correct / self.total_attempts

    def should_advance(self) -> bool:
        """Determine if user should advance to next stage."""
        # Need 3+ consecutive correct (non-consecutive keys)
        if self.consecutive_correct >= 3:
            # And overall accuracy > 85%
            return self.overall_accuracy() > 0.85
        return False

    def should_slow_down(self) -> bool:
        """Determine if user is struggling."""
        # 2+ consecutive wrong (non-consecutive keys) or accuracy < 70%
        return self.consecutive_wrong >= 2 or self.overall_accuracy() < 0.70

    def get_struggling_keys(self) -> List[str]:
        """Return keys user struggles with."""
        struggling = []
        for key, perf in self.key_performance.items():
            if perf.attempts >= 3 and perf.recent_accuracy() < 0.75:
                struggling.append(key)
        return struggling

# ----------------- Data Classes -----------------
@dataclass
class LessonState:
    stage: int = 0
    batch_words: list = field(default_factory=list)
    index: int = 0
    typed: str = ""
    tracker: AdaptiveTracker = field(default_factory=AdaptiveTracker)
    use_words: bool = False  # Use real words vs random strings
    review_mode: bool = False  # In review mode for struggling keys
    review_keys: List[str] = field(default_factory=list)

@dataclass
class TestState:
    running: bool = False
    start_time: float = 0.0
    current: str = ""
    remaining: list = field(default_factory=list)
    typed: str = ""
    correct_chars: int = 0
    total_chars: int = 0

@dataclass
class TutorialState:
    phase: int = 1  # 1=arrows+space, 2=introduce enter, 3=mix all
    sequence: list = field(default_factory=list)
    index: int = 0
    required_name: str = ""
    required_key: int = 0
    counts_done: Counter = field(default_factory=Counter)

@dataclass
class Settings:
    show_tutorial: bool = True

@dataclass
class AppState:
    mode: str = "MENU"
    settings: Settings = field(default_factory=Settings)
    lesson: LessonState = field(default_factory=LessonState)
    test: TestState = field(default_factory=TestState)
    tutorial: TutorialState = field(default_factory=TutorialState)
    results_text: str = ""
    backend_label: str = ""
    menu_items: list = field(default_factory=lambda: ["Tutorial", "Lesson", "Speed Test", "Quit"])
    menu_index: int = 0

# ----------------- Main App -----------------
class KeyQuestApp:
    def __init__(self):
        try:
            pygame.init()
            pygame.mixer.init()
        except Exception as e:
            log_exception(e)
            raise

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Key Quest 11")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.freetype.SysFont(FONT_NAME, TITLE_SIZE)
        self.text_font = pygame.freetype.SysFont(FONT_NAME, TEXT_SIZE)
        self.small_font = pygame.freetype.SysFont(FONT_NAME, SMALL_SIZE)

        self.state = AppState()
        self.speech = Speech()
        self.state.backend_label = self._backend_label()

        try:
            self.tone_ok = make_tone(1200, 70)
            self.tone_bad = make_tone(300, 100)
        except Exception as e:
            log_exception(e)
            self.tone_ok = None
            self.tone_bad = None

        self.load_progress()

    def load_progress(self):
        try:
            with open("progress.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            stage = int(data.get("stage", 0))
            if 0 <= stage < len(STAGE_LETTERS):
                self.state.lesson.stage = stage
        except Exception:
            self.state.lesson.stage = 0

    def save_progress(self):
        try:
            data = {"stage": int(self.state.lesson.stage)}
            with open("progress.json", "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            log_exception(e)

    def _backend_label(self) -> str:
        if self.speech.backend == "ao2":
            return "AO2"
        elif self.speech.backend == "tts":
            return "TTS"
        return "No Speech"

    def _play_wave(self, wave):
        try:
            if wave is None:
                return
            arr = (wave * 32767).astype(np.int16)
            init = pygame.mixer.get_init()
            if init is not None:
                freq, fmt, channels = init
                if channels == 2:
                    arr = np.column_stack((arr, arr))
            sound = pygame.sndarray.make_sound(arr)
            sound.play()
        except Exception as e:
            log_exception(e)

    def beep_ok(self):
        self._play_wave(self.tone_ok)

    def beep_bad(self):
        self._play_wave(self.tone_bad)

    def run(self):
        self.say_menu()
        while True:
            for event in pygame.event.get():
                try:
                    self.handle_event(event)
                except Exception as e:
                    log_exception(e)
                    raise
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if self.state.mode == "MENU":
                self.handle_menu_input(event)
            elif self.state.mode == "TUTORIAL":
                self.handle_tutorial_input(event, mods)
            elif self.state.mode == "LESSON":
                self.handle_lesson_input(event, mods)
            elif self.state.mode == "TEST":
                self.handle_test_input(event, mods)
            elif self.state.mode == "RESULTS":
                self.handle_results_input(event, mods)

    # ==================== MENU ====================
    def say_menu(self):
        items = self.state.menu_items
        idx = self.state.menu_index
        self.speech.say(
            f"Key Quest. Main menu. {items[idx]}. Use Up and Down to choose. Press Enter or Space to select.",
            priority=True,
            protect_seconds=2.0,
        )

    def handle_menu_input(self, event):
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit(0)
        elif event.key == pygame.K_UP:
            self.state.menu_index = (self.state.menu_index - 1) % len(self.state.menu_items)
            self.speech.say(self.state.menu_items[self.state.menu_index])
        elif event.key == pygame.K_DOWN:
            self.state.menu_index = (self.state.menu_index + 1) % len(self.state.menu_items)
            self.speech.say(self.state.menu_items[self.state.menu_index])
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = self.state.menu_items[self.state.menu_index]
            if choice == "Tutorial":
                self.start_tutorial()
            elif choice == "Lesson":
                self.start_lesson()
            elif choice == "Speed Test":
                self.start_test()
            elif choice == "Quit":
                pygame.quit()
                sys.exit(0)

    # ==================== TUTORIAL (IMPROVED) ====================
    def start_tutorial(self):
        self.state.mode = "TUTORIAL"
        t = self.state.tutorial
        t.phase = 1
        t.sequence = []
        t.counts_done = Counter()

        # Phase 1: arrows and space
        for name, key in PHASE1_KEYS:
            t.sequence.extend([(name, key)] * TUTORIAL_EACH_COUNT)
        random.shuffle(t.sequence)
        t.index = 0

        self.speech.say(
            "Tutorial. First: arrows and the space bar, three each. Arrows are together: Up above Down, Left beside Right. Space is the long bar at the bottom.",
            priority=True, protect_seconds=2.5,
        )
        self.load_tutorial_prompt()

    def load_tutorial_prompt(self):
        t = self.state.tutorial

        if t.index >= len(t.sequence):
            if t.phase == 1:
                # Phase 2: Introduce Enter only
                t.phase = 2
                t.sequence = [(name, key) for name, key in PHASE2_INTRO_KEYS] * TUTORIAL_EACH_COUNT
                t.index = 0
                self.speech.say(
                    "Great! Now learn Enter. Enter is on the right side of the letters, often tall or L‑shaped.",
                    priority=True, protect_seconds=2.5,
                )
            elif t.phase == 2:
                # Phase 3: Mix everything together
                t.phase = 3
                t.sequence = []
                for name, key in PHASE2_MIX_KEYS:
                    t.sequence.extend([(name, key)] * TUTORIAL_MIX_COUNT)
                random.shuffle(t.sequence)
                t.index = 0
                self.speech.say(
                    "Excellent! Now practice all keys together: arrows, space, and enter.",
                    priority=True, protect_seconds=2.5,
                )
            else:
                # Tutorial complete
                self.state.mode = "MENU"
                self.speech.say("Tutorial complete! You're ready for lessons. Returning to menu.", priority=True)
                self.say_menu()
                return

        name, key = t.sequence[t.index]
        t.required_name = name
        t.required_key = key
        self.speech.say(f"Press {FRIENDLY[name]}.")

    def handle_tutorial_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
            return

        if event.key == pygame.K_SPACE and mod_ctrl(mods):
            self.speech.say(f"Press {FRIENDLY[self.state.tutorial.required_name]}.")
            return

        t = self.state.tutorial
        keyset = PHASE1_KEYS if t.phase == 1 else (PHASE2_INTRO_KEYS if t.phase == 2 else PHASE2_MIX_KEYS)

        pressed_name = None
        for name, key in keyset:
            if event.key == key:
                pressed_name = name
                break

        if pressed_name is None:
            if t.phase == 1:
                self.speech.say("Use the arrow keys or the space bar.")
            elif t.phase == 2:
                self.speech.say("Use Enter.")
            else:
                self.speech.say("Use arrows, space, or Enter.")
            return

        if event.key == t.required_key:
            self.beep_ok()
            t.counts_done[t.required_name] += 1
            t.index += 1
            self.speech.say(random.choice(ENCOURAGEMENT["correct"]))
            self.load_tutorial_prompt()
        else:
            self.beep_bad()
            target = t.required_name
            pressed = pressed_name
            guidance = RELATION.get((pressed, target), f"Try {FRIENDLY[target]}.")
            hint = HINTS[target]
            self.speech.say(f"{FRIENDLY[pressed]}. {guidance} {hint}")

    # ==================== LESSON (ADAPTIVE) ====================
    def start_lesson(self):
        """Begin adaptive lesson."""
        self.state.mode = "LESSON"
        stage = max(0, min(self.state.lesson.stage, len(STAGE_LETTERS) - 1))
        self.state.lesson = LessonState(stage=stage)

        # Check if user is proficient enough for words
        if stage >= 2:  # After learning basic keys
            self.state.lesson.use_words = True

        self.build_lesson_batch()

        current_keys = set().union(*STAGE_LETTERS[:stage + 1])
        self.speech.say(
            f"Lesson Stage {stage + 1}. Keys: {', '.join(sorted(current_keys))}. Control Space repeats.",
            priority=True,
        )
        self.lesson_prompt()

    def build_lesson_batch(self):
        """Build adaptive lesson batch based on performance."""
        stage = self.state.lesson.stage
        l = self.state.lesson

        # Get allowed keys
        allowed = set().union(*STAGE_LETTERS[:stage + 1])
        allowed_list = sorted(allowed)

        # Check for struggling keys
        struggling = l.tracker.get_struggling_keys()

        batch = []

        if l.review_mode and struggling:
            # Review mode: focus on struggling keys with easier content
            l.review_keys = struggling[:3]  # Focus on top 3
            for _ in range(LESSON_BATCH):
                length = random.randint(2, 3)  # Shorter in review
                word = "".join(random.choice(l.review_keys) for _ in range(length))
                batch.append(word)
        elif l.use_words and stage in STAGE_WORDS and random.random() < 0.6:
            # Use real words 60% of the time when available
            words = STAGE_WORDS[stage]
            for _ in range(LESSON_BATCH):
                batch.append(random.choice(words))
        elif l.use_words and stage in STAGE_PHRASES and random.random() < 0.3:
            # Use phrases 30% of the time when available
            phrases = STAGE_PHRASES[stage]
            for _ in range(LESSON_BATCH):
                batch.append(random.choice(phrases))
        else:
            # Random character practice
            for _ in range(LESSON_BATCH):
                min_len = 2 if stage < 3 else 3
                max_len = 4 if stage < 5 else 5
                length = random.randint(min_len, max_len)
                word = "".join(random.choice(allowed_list) for _ in range(length))
                batch.append(word)

        l.batch_words = batch
        l.index = 0
        l.typed = ""

    def lesson_prompt(self):
        target = self.state.lesson.batch_words[self.state.lesson.index]
        self.speech.say(f"Type: {target}", priority=True)

    def next_lesson_item(self):
        l = self.state.lesson
        l.index += 1
        l.typed = ""

        # Check adaptive triggers
        if l.tracker.consecutive_correct >= 3:
            msg = random.choice(ENCOURAGEMENT["streak_3"])
            self.speech.say(msg)
        elif l.tracker.consecutive_correct >= 5:
            msg = random.choice(ENCOURAGEMENT["streak_5"])
            self.speech.say(msg)

        if l.index >= len(l.batch_words):
            # Batch complete - check if should advance/review/repeat
            self.evaluate_lesson_performance()
        else:
            self.lesson_prompt()

    def evaluate_lesson_performance(self):
        """Evaluate performance and decide next action."""
        l = self.state.lesson

        if l.tracker.should_advance():
            # Advance to next stage
            l.stage = min(l.stage + 1, len(STAGE_LETTERS) - 1)
            self.save_progress()
            self.state.mode = "RESULTS"
            self.state.results_text = (
                f"{random.choice(ENCOURAGEMENT['stage_complete'])} "
                f"Moving to stage {l.stage + 1}. "
                "Press Space to continue, Enter to practice more, or Escape for menu."
            )
        elif l.tracker.should_slow_down():
            # Enter review mode
            self.state.mode = "RESULTS"
            self.state.results_text = (
                f"{random.choice(ENCOURAGEMENT['struggle'])} "
                "Let's practice those keys again. "
                "Press Space for focused review, Enter to try again, or Escape for menu."
            )
            l.review_mode = True
        else:
            # Continue current stage
            self.state.mode = "RESULTS"
            self.state.results_text = (
                "Good progress! "
                "Press Space to continue, Enter to practice more, or Escape for menu."
            )

        self.speech.say(self.state.results_text, priority=True, protect_seconds=3.0)

    def current_word(self):
        return self.state.lesson.batch_words[self.state.lesson.index]

    def handle_lesson_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
        elif event.key == pygame.K_SPACE and mod_ctrl(mods):
            self.lesson_prompt()
        else:
            self.process_lesson_typing(event)

    def process_lesson_typing(self, event):
        target = self.current_word()
        ch = None

        if event.unicode and event.unicode.isprintable():
            ch = event.unicode
        elif event.key == pygame.K_BACKSPACE:
            self.state.lesson.typed = self.state.lesson.typed[:-1]
            return
        else:
            return

        if ch is not None:
            l = self.state.lesson
            l.typed += ch
            typed = l.typed

            if not target.startswith(typed):
                self.beep_bad()
                # FIXED: Calculate what was remaining before the error
                before_error = l.typed[:-1]  # Remove the wrong character
                if before_error and target.startswith(before_error):
                    remaining = target[len(before_error):]
                else:
                    remaining = target
                # Record incorrect keystroke
                l.tracker.record_keystroke(ch, False)
                l.typed = ""
                # FIXED: Tell user what they need to type (like kq9)
                self.speech.say(f"Remaining: {remaining}", priority=True)
                # Encouragement on struggle
                if l.tracker.consecutive_wrong == 1:
                    self.speech.say(random.choice(ENCOURAGEMENT["struggle"]))
                return

            # Correct so far
            l.tracker.record_keystroke(ch, True)

            if typed == target:
                self.beep_ok()
                # Comeback after struggle
                if l.tracker.total_attempts > 0 and l.tracker.consecutive_correct == 1:
                    if l.tracker.consecutive_wrong > 0:  # Just recovered
                        self.speech.say(random.choice(ENCOURAGEMENT["comeback"]))
                self.next_lesson_item()

    # ==================== SPEED TEST ====================
    def start_test(self):
        self.state.mode = "TEST"
        self.state.test = TestState(
            running=False,
            start_time=0.0,
            remaining=random.sample(TEST_SENTENCES, k=len(TEST_SENTENCES)),
            current="",
            typed="",
            correct_chars=0,
            total_chars=0,
        )
        self.speech.say("Speed test. Sixty seconds. Control Space repeats the remaining text.")
        self.load_next_sentence()

    def load_next_sentence(self):
        if not self.state.test.remaining:
            self.finish_test()
            return
        self.state.test.current = self.state.test.remaining.pop(0)
        self.state.test.typed = ""
        self.speech.say(self.state.test.current)

    def finish_test(self):
        self.state.test.running = False
        t = self.state.test

        acc = 0.0
        if t.total_chars:
            acc = (t.correct_chars / t.total_chars) * 100.0

        if t.start_time > 0.0:
            elapsed = max(1e-3, time.time() - t.start_time)
        else:
            elapsed = TEST_SECONDS

        words_typed = t.correct_chars / 5.0
        minutes = elapsed / 60.0
        wpm = words_typed / minutes if minutes > 0 else 0.0

        self.state.mode = "RESULTS"
        self.state.results_text = (
            f"Speed test complete! WPM {wpm:.1f}. Accuracy {acc:.1f} percent. "
            "Press Enter to try again, or Escape for menu."
        )
        self.speech.say(self.state.results_text, priority=True, protect_seconds=3.0)

    def handle_test_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
        elif event.key == pygame.K_SPACE and mod_ctrl(mods):
            self.speak_test_remaining()
        else:
            self.process_test_typing(event)

    def process_test_typing(self, event):
        ch = None
        if event.unicode and event.unicode.isprintable():
            ch = event.unicode
        elif event.key == pygame.K_BACKSPACE:
            self.state.test.typed = self.state.test.typed[:-1]
            return
        else:
            return

        if ch is not None:
            t = self.state.test
            if not t.running:
                t.start_time = time.time()
                t.running = True

            t.typed += ch
            pos = len(t.typed) - 1

            if pos < len(t.current) and ch == t.current[pos]:
                t.correct_chars += 1
            t.total_chars += 1

            if t.typed == t.current:
                self.load_next_sentence()

    def speak_test_remaining(self):
        current = self.state.test.current
        typed = self.state.test.typed
        remaining = current[len(typed):] if current.startswith(typed) else current
        self.speech.say(remaining, priority=True)

    # ==================== RESULTS ====================
    def handle_results_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
        elif event.key == pygame.K_SPACE:
            if "stage" in self.state.results_text.lower() or "continue" in self.state.results_text.lower():
                # Reset review mode if exiting it
                self.state.lesson.review_mode = False
                # Advance or continue lesson
                self.save_progress()
                self.start_lesson()
        elif event.key == pygame.K_RETURN:
            if "Speed test" in self.state.results_text:
                self.start_test()
            else:
                self.save_progress()
                self.start_lesson()

    # ==================== DRAWING ====================
    def draw(self):
        self.screen.fill(BG)
        if self.state.mode == "MENU":
            self.draw_menu()
        elif self.state.mode == "TUTORIAL":
            self.draw_tutorial()
        elif self.state.mode == "LESSON":
            self.draw_lesson()
        elif self.state.mode == "TEST":
            self.draw_test()
        elif self.state.mode == "RESULTS":
            self.draw_results()

    def draw_menu(self):
        y = 120
        for idx, item in enumerate(self.state.menu_items):
            color = HILITE if idx == self.state.menu_index else FG
            text_surf, _ = self.title_font.render(item, color)
            x = SCREEN_W // 2 - text_surf.get_width() // 2
            self.screen.blit(text_surf, (x, y))
            y += 50

        stage = self.state.lesson.stage
        info = f"Current Stage: {stage + 1} / {len(STAGE_LETTERS)}"
        info_surf, _ = self.small_font.render(info, ACCENT)
        self.screen.blit(info_surf, (SCREEN_W // 2 - info_surf.get_width() // 2, y + 20))

    def draw_tutorial(self):
        t = self.state.tutorial
        prompt = f"Press {FRIENDLY[t.required_name]}"
        prompt_surf, _ = self.title_font.render(prompt, FG)
        self.screen.blit(prompt_surf, (SCREEN_W // 2 - prompt_surf.get_width() // 2, 100))

        y = 200
        keyset = PHASE1_KEYS if t.phase == 1 else (PHASE2_INTRO_KEYS if t.phase == 2 else PHASE2_MIX_KEYS)
        for name, key in keyset:
            cnt = t.counts_done.get(name, 0)
            total = TUTORIAL_EACH_COUNT if t.phase < 3 else TUTORIAL_MIX_COUNT
            lbl = f"{FRIENDLY[name]}: {cnt}/{total}"
            surf, _ = self.text_font.render(lbl, FG)
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))
            y += 40

    def draw_lesson(self):
        l = self.state.lesson
        target = self.current_word()
        typed = l.typed

        target_surf, _ = self.title_font.render(target, ACCENT)
        target_x = SCREEN_W // 2 - target_surf.get_width() // 2
        self.screen.blit(target_surf, (target_x, 150))

        typed_surf, _ = self.text_font.render(typed, FG)
        typed_x = SCREEN_W // 2 - typed_surf.get_width() // 2
        self.screen.blit(typed_surf, (typed_x, 230))

        stage = l.stage
        current_keys = set().union(*STAGE_LETTERS[:stage + 1])
        info = f"Stage {stage + 1}: {', '.join(sorted(current_keys))}"
        info_surf, _ = self.small_font.render(info, ACCENT)
        self.screen.blit(info_surf, (SCREEN_W // 2 - info_surf.get_width() // 2, 320))

        # Show accuracy
        acc = l.tracker.overall_accuracy() * 100
        acc_text = f"Accuracy: {acc:.0f}%"
        acc_surf, _ = self.small_font.render(acc_text, ACCENT)
        self.screen.blit(acc_surf, (SCREEN_W // 2 - acc_surf.get_width() // 2, 350))

    def draw_test(self):
        t = self.state.test
        current = t.current
        typed = t.typed

        cur_surf, _ = self.text_font.render(current, ACCENT)
        self.screen.blit(cur_surf, (SCREEN_W // 2 - cur_surf.get_width() // 2, 200))

        typed_surf, _ = self.text_font.render(typed, FG)
        self.screen.blit(typed_surf, (SCREEN_W // 2 - typed_surf.get_width() // 2, 260))

        if t.running and t.start_time > 0:
            elapsed = time.time() - t.start_time
            remaining = max(0, TEST_SECONDS - elapsed)
        else:
            remaining = TEST_SECONDS

        time_msg = f"{int(remaining):>2}s left"
        time_surf, _ = self.small_font.render(time_msg, ACCENT)
        self.screen.blit(time_surf, (SCREEN_W // 2 - time_surf.get_width() // 2, 320))

    def draw_results(self):
        lines = []
        words = self.state.results_text.split()
        line = ""
        for w in words:
            test = f"{line} {w}".strip()
            surf, _ = self.text_font.render(test, FG)
            if surf.get_width() > SCREEN_W - 40:
                lines.append(line)
                line = w
            else:
                line = test
        if line:
            lines.append(line)

        y = 150
        for ln in lines:
            surf, _ = self.text_font.render(ln, FG)
            self.screen.blit(surf, (SCREEN_W // 2 - surf.get_width() // 2, y))
            y += 40


def main():
    app = KeyQuestApp()
    try:
        app.run()
    except Exception as e:
        log_exception(e)
        raise


if __name__ == "__main__":
    main()
