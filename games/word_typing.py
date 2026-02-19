"""Word Typing - Fast-paced word typing practice game!

A clean, simple word typing game. Type words as fast as you can
to build speed and accuracy.
"""

import random
import time
import pygame
from games.base_game import BaseGame
from games import sounds
from ui.a11y import draw_controls_hint, draw_focus_frame


# Word lists by difficulty
EASY_WORDS = [
    "cat", "dog", "run", "sit", "hot", "cold", "big", "small", "fast", "slow",
    "yes", "no", "day", "sun", "car", "hat", "cup", "bag", "box", "key",
    "pen", "bed", "red", "blue", "tree", "book", "door", "hand", "foot", "head"
]

MEDIUM_WORDS = [
    "happy", "quick", "table", "chair", "water", "bread", "music", "dance",
    "think", "learn", "build", "start", "summer", "family", "person", "window",
    "garden", "planet", "rocket", "castle", "forest", "ocean", "mountain", "river",
    "flower", "animal", "season", "number", "letter", "friend", "school", "teacher"
]

HARD_WORDS = [
    "keyboard", "computer", "practice", "question", "mountain", "library",
    "important", "beautiful", "wonderful", "dangerous", "remember", "yesterday",
    "something", "everywhere", "adventure", "chocolate", "butterfly", "education",
    "celebration", "experience", "government", "technology", "vocabulary", "entertainment",
    "development", "environment", "opportunity", "temperature", "restaurant", "competition"
]


class WordTypingGame(BaseGame):
    """Fast-paced word typing practice!"""

    # Game metadata
    NAME = "Word Typing"
    DESCRIPTION = "Type words as quickly and accurately as you can in a 30-second session."
    INSTRUCTIONS = (
        "Words appear one at a time. Type the current word and press Enter to submit. "
        "The session ends after 30 seconds. Results show corrected words per minute, "
        "total words per minute, and accuracy. Press Escape three times during play to return to the main menu and end the "
        "session. In the results dialog, press Space or Escape to close."
    )
    HOTKEYS = """Type the word: Letter keys
Submit word: Enter
Correct mistakes: Backspace
Repeat current word: Ctrl+Space
Escape x3: Exit to main menu"""

    def __init__(self, screen, fonts, speech, play_sound_func, show_info_dialog_func, session_complete_callback=None):
        """Initialize the Word Typing game."""
        super().__init__(
            screen,
            fonts,
            speech,
            play_sound_func,
            show_info_dialog_func,
            session_complete_callback,
        )

        # Game state
        self.running = False
        self.game_start_time = 0
        self.game_duration = 30.0  # Default 30 seconds

        # Scoring
        self.words_completed = 0
        self.words_attempted = 0
        self.total_chars_typed = 0
        self.correct_chars = 0

        # Current word
        self.current_word = ""
        self.typed_text = ""
        self.word_pool = []

        # Best scores
        self.best_wpm = 0
        self.best_accuracy = 0
        self.warned_10_seconds = False
        self.warned_5_seconds = False

    def start_playing(self):
        """Initialize/reset game state and begin playing."""
        self.mode = "PLAYING"
        self.running = True
        self.game_start_time = time.time()

        # Reset scores
        self.words_completed = 0
        self.words_attempted = 0
        self.total_chars_typed = 0
        self.correct_chars = 0
        self.typed_text = ""
        self.warned_10_seconds = False
        self.warned_5_seconds = False

        # Build word pool (mixed difficulty by default)
        self.word_pool = (
            random.sample(EASY_WORDS, min(10, len(EASY_WORDS))) +
            random.sample(MEDIUM_WORDS, min(30, len(MEDIUM_WORDS))) +
            random.sample(HARD_WORDS, min(10, len(HARD_WORDS)))
        )
        random.shuffle(self.word_pool)

        # Get first word
        self.current_word = self.word_pool[0] if self.word_pool else "word"

        # Welcome
        msg = f"{self.NAME}. Type words as fast as you can! {int(self.game_duration)} seconds. Starting now!"
        self.speech.say(msg, priority=True, protect_seconds=2.5)
        self.play_sound(sounds.level_start())

        # Announce first word
        self.speech.say(f"Type: {self.current_word}", priority=True)

    def handle_game_input(self, event, mods):
        """Handle input during gameplay."""
        # Game over
        if not self.running:
            if event.key == pygame.K_ESCAPE:
                self.mode = "MENU"
                self.say_game_menu()
            return None

        # Exit game
        if event.key == pygame.K_ESCAPE:
            self.end_game()
            return None

        # Repeat current word
        elif event.key == pygame.K_SPACE and (mods & pygame.KMOD_CTRL):
            self.speech.say(f"Current word: {self.current_word}", priority=True)
            return None

        # Backspace
        elif event.key == pygame.K_BACKSPACE:
            if self.typed_text:
                self.typed_text = self.typed_text[:-1]
            return None

        # Submit word
        elif event.key == pygame.K_RETURN:
            if self.typed_text:
                self.check_word()
            return None

        # Type character
        char = event.unicode
        if char and (char.isalpha() or char == "'" or char == "-"):
            self.typed_text += char.lower()
            return None

        return None

    def check_word(self):
        """Check if typed word matches current word."""
        self.words_attempted += 1
        typed = self.typed_text.strip().lower()
        target = self.current_word.lower()

        # Count correct characters
        for i, char in enumerate(typed):
            self.total_chars_typed += 1
            if i < len(target) and char == target[i]:
                self.correct_chars += 1

        # Check if word is correct
        if typed == target:
            self.words_completed += 1
            self.play_sound(sounds.letter_hit())

            # Get next word
            self.next_word()
        else:
            # Wrong word
            self.play_sound(sounds.letter_miss())
            self.speech.say("Incorrect. Try again.", priority=True)
            self.typed_text = ""

    def next_word(self):
        """Move to next word."""
        # Cycle through word pool
        if self.word_pool:
            self.word_pool.append(self.word_pool.pop(0))
            self.current_word = self.word_pool[0]

        self.typed_text = ""

        # Announce new word
        self.speech.say(f"Type: {self.current_word}", priority=True)

    def end_game(self):
        """End the game and show results."""
        self.running = False
        self.play_sound(sounds.game_over())

        # Calculate stats
        elapsed_minutes = (time.time() - self.game_start_time) / 60.0
        net_wpm = int((self.correct_chars / 5.0) / elapsed_minutes) if elapsed_minutes > 0 else 0
        gross_wpm = int((self.total_chars_typed / 5.0) / elapsed_minutes) if elapsed_minutes > 0 else 0
        accuracy = int((self.correct_chars / self.total_chars_typed) * 100) if self.total_chars_typed > 0 else 0

        # Update bests
        if net_wpm > self.best_wpm:
            self.best_wpm = net_wpm
        if accuracy > self.best_accuracy:
            self.best_accuracy = accuracy

        # Performance message
        if net_wpm >= 60:
            perf_msg = "Outstanding speed! Expert level!"
        elif net_wpm >= 40:
            perf_msg = "Great performance! Very fast typing!"
        elif net_wpm >= 25:
            perf_msg = "Good job! Keep practicing!"
        else:
            perf_msg = "Nice try! Practice makes perfect!"

        # Show results
        results = f"""GAME OVER

Words Completed: {self.words_completed}
Words Attempted: {self.words_attempted}

Corrected Words Per Minute: {net_wpm}
Total Words Per Minute: {gross_wpm}
Accuracy: {accuracy}%

Best WPM: {self.best_wpm}
Best Accuracy: {self.best_accuracy}%

{perf_msg}

--- End of file ---
"""
        self.show_game_results(
            results,
            session_stats={
                "words_completed": self.words_completed,
                "accuracy": float(accuracy),
                "session_duration_minutes": elapsed_minutes,
                "pet_xp": max(10, self.words_completed * 2),
            },
        )

        # Announce
        msg = (
            f"Game over! Corrected words per minute {net_wpm}. "
            f"Total words per minute {gross_wpm}. Accuracy {accuracy} percent."
        )
        self.speech.say(msg, priority=True)

        # Return to menu
        self.mode = "MENU"
        self.say_game_menu()

    def update(self, dt):
        """Update game logic."""
        if self.mode != "PLAYING" or not self.running:
            return

        # Check time
        elapsed = time.time() - self.game_start_time
        remaining = self.game_duration - elapsed

        # Time warnings
        if remaining <= 10 and not self.warned_10_seconds:
            self.warned_10_seconds = True
            self.speech.say("10 seconds left!", priority=True)
        elif remaining <= 5 and not self.warned_5_seconds:
            self.warned_5_seconds = True
            self.speech.say("5 seconds!", priority=True)

        # Time's up
        if remaining <= 0:
            self.end_game()

    def draw_game(self):
        """Draw the game screen."""
        # Title
        title_surf, _ = self.title_font.render(f"{self.NAME}", self.ACCENT)
        self.screen.blit(title_surf, (450 - title_surf.get_width() // 2, 50))

        # Timer
        elapsed = time.time() - self.game_start_time
        remaining = max(0, self.game_duration - elapsed)
        timer_text = f"Time: {int(remaining)}s"
        timer_surf, _ = self.text_font.render(timer_text, self.FG)
        self.screen.blit(timer_surf, (450 - timer_surf.get_width() // 2, 120))

        # Score
        score_text = f"Words: {self.words_completed}"
        score_surf, _ = self.text_font.render(score_text, self.GOOD)
        self.screen.blit(score_surf, (450 - score_surf.get_width() // 2, 160))

        # Current word
        target_label, _ = self.small_font.render("Type now:", self.ACCENT)
        self.screen.blit(target_label, (450 - target_label.get_width() // 2, 215))
        word_surf, _ = self.title_font.render(self.current_word, self.FG)
        word_rect = word_surf.get_rect(topleft=(450 - word_surf.get_width() // 2, 250))
        self.screen.blit(word_surf, word_rect)
        draw_focus_frame(self.screen, word_rect, self.GOOD, self.ACCENT)

        # Typed text
        typed_label, _ = self.small_font.render("You typed:", self.ACCENT)
        self.screen.blit(typed_label, (450 - typed_label.get_width() // 2, 320))
        typed_value = self.typed_text if self.typed_text else "_"
        # Check if correct so far
        correct_so_far = self.current_word.lower().startswith(self.typed_text.lower())
        color = self.GOOD if correct_so_far else self.DANGER
        typed_surf, _ = self.text_font.render(typed_value, color)
        self.screen.blit(typed_surf, (450 - typed_surf.get_width() // 2, 350))

        draw_controls_hint(
            screen=self.screen,
            small_font=self.small_font,
            text="Type word; Enter submit; Backspace correct; Ctrl+Space repeat; Esc quit",
            screen_w=900,
            y=535,
            accent=self.FG,
        )
