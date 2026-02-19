"""Letter Fall - Type falling letters before they reach the bottom!

A fun typing game where letters fall from the top of the screen.
Type them correctly to score points and prevent them from reaching the bottom.
The game gets progressively faster as you score more points.
"""

import random
import time
import pygame
from games.base_game import BaseGame
from games import sounds
from ui.a11y import draw_controls_hint


class LetterFallGame(BaseGame):
    """Letters fall from the top - type them before they hit bottom!"""

    # Game metadata
    NAME = "Letter Fall"
    DESCRIPTION = "Type falling letters before they reach the bottom! Game speeds up as you score."
    INSTRUCTIONS = (
        "Type the letters as they fall before they reach the bottom. Press Tab to hear the "
        "letters currently on screen. Press Control plus Space to hear your score, lives, "
        "and combo. Press Escape three times during play to return to the main menu. "
        "In the results dialog, press Space or Escape to close."
    )
    HOTKEYS = """Type the falling letters: Letter keys
List current falling letters: Tab
Repeat current score: Ctrl+Space
Escape x3: Exit to main menu"""

    def __init__(self, screen, fonts, speech, play_sound_func, show_info_dialog_func, session_complete_callback=None):
        """Initialize the Letter Fall game."""
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
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0

        # Game difficulty
        self.fall_speed = 1.0
        self.spawn_interval = 1.5  # seconds

        # Active letters: list of (letter, x, y, speed)
        self.letters = []
        self.last_spawn = 0

        # Visual effects
        self.last_hit_time = 0
        self.hit_letter = ""
        self.hit_x = 0
        self.hit_y = 0

        # Speech management
        self.last_letter_announcement = 0
        self.announce_interval = 3.0  # Announce letters every 3 seconds
        self.game_start_time = 0.0

    def start_playing(self):
        """Initialize/reset game state and begin playing."""
        self.mode = "PLAYING"
        self.running = True
        self.score = 0
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        self.fall_speed = 1.0
        self.spawn_interval = 1.5
        self.letters = []
        self.last_spawn = time.time()
        self.last_hit_time = 0
        self.game_start_time = time.time()

        # Welcome message
        msg = f"{self.NAME}. Type letters as they fall. Press Escape to pause."
        self.speech.say(msg, priority=True, protect_seconds=3.0)
        self.play_sound(sounds.level_start())

    def handle_game_input(self, event, mods):
        """Handle input during gameplay."""
        if event.key == pygame.K_ESCAPE:
            self.running = False
            self.mode = "MENU"
            # Announce final score and return to menu
            self.speech.say(
                f"Game paused. Final score: {self.score}. Returning to menu.",
                priority=True
            )
            self.say_game_menu()
            return None

        elif event.key == pygame.K_SPACE and (mods & pygame.KMOD_CTRL):
            # Repeat current score
            self.announce_score()
            return None

        elif event.key == pygame.K_TAB:
            # List all current letters
            self.announce_current_letters()
            return None

        # Check if typed letter matches any falling letter
        char = event.unicode.lower()
        if char.isalpha() and len(char) == 1:
            self.try_hit_letter(char)

        return None

    def try_hit_letter(self, char):
        """Try to hit a falling letter."""
        # Find matching letter (highest one first - closest to top)
        for i, (letter, x, y, spd) in enumerate(self.letters):
            if letter == char:
                # Hit!
                self.letters.pop(i)
                self.score += 10
                self.combo += 1
                self.max_combo = max(self.max_combo, self.combo)

                # Update high score
                if self.score > self.high_score:
                    self.high_score = self.score

                # Visual effect
                self.last_hit_time = time.time()
                self.hit_letter = char.upper()
                self.hit_x = x
                self.hit_y = y

                # Play sound based on combo (sound is enough, no speech needed)
                if self.combo >= 5:
                    self.play_sound(sounds.powerup_sound())
                elif self.combo >= 3:
                    self.play_sound(sounds.combo_sound(self.combo))
                else:
                    self.play_sound(sounds.letter_hit())

                # Announce combos
                if self.combo == 3:
                    self.speech.say("Combo 3!", priority=False)
                elif self.combo == 5:
                    self.speech.say("Combo 5! On fire!", priority=False)
                elif self.combo == 10:
                    self.speech.say("Amazing! Combo 10!", priority=False)

                # Increase difficulty every 50 points
                if self.score > 0 and self.score % 50 == 0:
                    self.fall_speed += 0.2
                    self.spawn_interval = max(0.8, self.spawn_interval - 0.1)
                    self.speech.say("Speed up!", priority=False)
                    self.play_sound(sounds.speed_up())

                return True

        # Miss - no matching letter found (sound is enough, no speech needed)
        self.combo = 0
        self.play_sound(sounds.letter_miss())
        return False

    def update(self, dt):
        """Update game logic.

        Args:
            dt: Delta time in seconds since last update
        """
        if self.mode != "PLAYING" or not self.running:
            return

        current_time = time.time()

        # Spawn new letters
        if current_time - self.last_spawn > self.spawn_interval:
            self.spawn_letter()
            self.last_spawn = current_time

        # Move letters down
        updated_letters = []
        for letter, x, y, spd in self.letters:
            new_y = y + (spd * self.fall_speed * 120 * dt)

            # Check if letter reached bottom
            if new_y >= 520:
                # Letter missed - lose life
                self.lives -= 1
                self.combo = 0
                self.play_sound(sounds.life_lost())

                if self.lives > 0:
                    self.speech.say(f"Missed {letter}! {self.lives} lives left.", priority=True)
                else:
                    # Game over - show results and return to menu
                    self.running = False
                    self.mode = "MENU"
                    self.play_sound(sounds.game_over())

                    # Show results dialog
                    results = f"""GAME OVER

Final Score: {self.score}
High Score: {self.high_score}
Max Combo: {self.max_combo}

{self._get_performance_message()}

--- End of file ---
"""
                    elapsed_minutes = max(0.01, (time.time() - self.game_start_time) / 60.0)
                    self.show_game_results(
                        results,
                        session_stats={
                            "score": self.score,
                            "accuracy": min(100.0, 65.0 + min(30, self.max_combo * 2)),
                            "session_duration_minutes": elapsed_minutes,
                            "pet_xp": max(10, int(self.score / 20)),
                        },
                    )

                    # Return to game menu
                    self.say_game_menu()
            else:
                updated_letters.append((letter, x, new_y, spd))

        self.letters = updated_letters

        # Periodically announce current letters if any are active
        if self.letters and current_time - self.last_letter_announcement > self.announce_interval:
            self.announce_current_letters()
            self.last_letter_announcement = current_time

    def spawn_letter(self):
        """Spawn a new falling letter."""
        letter = random.choice('abcdefghijklmnopqrstuvwxyz')
        x = random.randint(50, 750)
        y = 50
        speed = 1.0

        self.letters.append((letter, x, y, speed))

        # Announce the new letter
        self.speech.say(letter.upper(), priority=False)

    def announce_score(self):
        """Announce current score and stats."""
        msg = f"Score: {self.score}. Lives: {self.lives}. Combo: {self.combo}."
        self.speech.say(msg, priority=True)

    def announce_current_letters(self):
        """Announce all currently falling letters."""
        if not self.letters:
            self.speech.say("No letters falling.", priority=True)
        else:
            # Sort by Y position (top to bottom)
            sorted_letters = sorted(self.letters, key=lambda l: l[2])
            letter_list = [l[0].upper() for l in sorted_letters]

            if len(letter_list) == 1:
                msg = f"Letter: {letter_list[0]}"
            else:
                letters_str = ", ".join(letter_list)
                msg = f"{len(letter_list)} letters: {letters_str}"

            self.speech.say(msg, priority=True)

    def _get_performance_message(self):
        """Get an encouraging message based on performance."""
        if self.score >= 500:
            return "Outstanding performance!"
        elif self.score >= 300:
            return "Great job!"
        elif self.score >= 150:
            return "Good work!"
        elif self.score >= 50:
            return "Nice try! Keep practicing."
        else:
            return "Keep practicing to improve!"

    def draw_game(self):
        """Draw the actual game screen."""

        # Title
        title_surf, _ = self.title_font.render(self.NAME, self.ACCENT)
        self.screen.blit(title_surf, (400 - title_surf.get_width() // 2, 10))

        mode_surf, _ = self.small_font.render("Type now: Falling letters", self.ACCENT)
        self.screen.blit(mode_surf, (400 - mode_surf.get_width() // 2, 40))

        # Draw falling letters
        for letter, x, y, _ in self.letters:
            # Color based on height (danger zone at bottom)
            in_danger = y > 400
            if in_danger:
                color = self.DANGER
            else:
                color = self.FG

            label = f"!{letter.upper()}" if in_danger else letter.upper()
            letter_surf, _ = self.text_font.render(label, color)
            self.screen.blit(letter_surf, (int(x), int(y)))

        # Draw hit effect (brief flash)
        if time.time() - self.last_hit_time < 0.3:
            hit_surf, _ = self.text_font.render(self.hit_letter, self.GOOD)
            self.screen.blit(hit_surf, (int(self.hit_x), int(self.hit_y)))

        # Score and stats
        score_text = f"Score: {self.score}  Lives: {self.lives}  Combo: {self.combo}"
        score_surf, _ = self.small_font.render(score_text, self.ACCENT)
        self.screen.blit(score_surf, (20, 540))

        # High score
        if self.high_score > 0:
            hs_text = f"High Score: {self.high_score}"
            hs_surf, _ = self.small_font.render(hs_text, self.ACCENT)
            self.screen.blit(hs_surf, (600, 540))

        letters_left_text = f"Letters on screen: {len(self.letters)}"
        left_surf, _ = self.small_font.render(letters_left_text, self.ACCENT)
        self.screen.blit(left_surf, (20, 515))

        draw_controls_hint(
            screen=self.screen,
            small_font=self.small_font,
            text="Type letters; Tab list; Ctrl+Space score; Esc quit",
            screen_w=900,
            y=575,
            accent=self.FG,
        )

        # Danger zone indicator
        pygame.draw.line(self.screen, self.DANGER, (0, 520), (900, 520), 2)
        if any(y > 400 for _, _, y, _ in self.letters):
            warn_text = "DANGER ZONE!"
            warn_surf, _ = self.small_font.render(warn_text, self.DANGER)
            self.screen.blit(warn_surf, (400 - warn_surf.get_width() // 2, 450))
