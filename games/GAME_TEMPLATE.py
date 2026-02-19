"""Template for creating new KeyQuest typing games.

Copy this file and customize it to create your own game.
All games must inherit from BaseGame to ensure consistent structure.
"""

from games.base_game import BaseGame
from games import sounds
import pygame
import random


class MyNewGame(BaseGame):
    """Short description of your game."""

    # ========== REQUIRED: Game Metadata ==========
    NAME = "My New Game"
    DESCRIPTION = "A fun typing game where you [describe what the player does]. Challenge yourself to improve your typing speed and accuracy!"
    INSTRUCTIONS = "Letters will appear on screen. Type the correct letter before time runs out. You start with 3 lives. Missing a letter costs a life. Get combos for bonus points. Press Escape to pause."
    HOTKEYS = """Type letters: Letter keys
Repeat score: Ctrl+Space
Pause game: Escape"""

    def __init__(
        self,
        screen,
        fonts,
        speech,
        play_sound_func,
        show_info_dialog_func,
        session_complete_callback=None,
    ):
        """Initialize your game.

        Args:
            screen: Pygame display surface
            fonts: Dict with 'title_font', 'text_font', 'small_font'
            speech: Speech object for announcements
            play_sound_func: Function to play sound waves
            show_info_dialog_func: Function to show accessible info dialogs
        """
        # Call parent constructor (REQUIRED)
        super().__init__(
            screen,
            fonts,
            speech,
            play_sound_func,
            show_info_dialog_func,
            session_complete_callback,
        )

        # Add your game-specific state here
        self.score = 0
        self.high_score = 0
        self.lives = 3
        self.running = False

        # Example: Game elements
        self.current_letter = ""
        self.time_remaining = 0

    # ========== REQUIRED: Game Start ==========

    def start_playing(self):
        """Called when user selects 'Play Game' from menu.

        Initialize/reset all game state and begin playing.
        """
        self.mode = "PLAYING"
        self.running = True
        self.score = 0
        self.lives = 3

        # Initialize your game elements
        self.spawn_letter()

        # Welcome message for screen reader users
        msg = f"{self.NAME} starting. Type the letters you see. Press Escape to pause."
        self.speech.say(msg, priority=True, protect_seconds=2.0)

    # ========== REQUIRED: Input Handling ==========

    def handle_game_input(self, event, mods):
        """Handle keyboard input during gameplay.

        Args:
            event: Pygame key event
            mods: Keyboard modifiers (use pygame.KMOD_CTRL for Ctrl key)

        Returns:
            None to continue, or "GAMES_MENU" to exit (handled automatically)
        """
        # Escape to pause (common pattern)
        if event.key == pygame.K_ESCAPE:
            self.running = False
            self.mode = "MENU"
            self.speech.say(f"Game paused. Score: {self.score}.", priority=True)
            self.say_game_menu()
            return None

        # Ctrl+Space to announce score (common pattern)
        elif event.key == pygame.K_SPACE and (mods & pygame.KMOD_CTRL):
            msg = f"Score: {self.score}. Lives: {self.lives}."
            self.speech.say(msg, priority=True)
            return None

        # Handle letter typing
        char = event.unicode.lower()
        if char.isalpha() and len(char) == 1:
            self.check_letter(char)

        return None

    # ========== OPTIONAL: Update Logic ==========

    def update(self, dt):
        """Update game logic each frame.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Only update when actually playing
        if self.mode != "PLAYING" or not self.running:
            return

        # Example: Update timer
        self.time_remaining -= dt
        if self.time_remaining <= 0:
            # Time ran out - lose a life
            self.lose_life()

    # ========== REQUIRED: Drawing ==========

    def draw_game(self):
        """Draw the game screen when mode is PLAYING."""

        # Title
        title_surf, _ = self.title_font.render(self.NAME, self.ACCENT)
        self.screen.blit(title_surf, (450 - title_surf.get_width() // 2, 30))

        # Draw current letter (example)
        if self.current_letter:
            letter_surf, _ = self.title_font.render(self.current_letter.upper(), self.FG)
            self.screen.blit(letter_surf, (450 - letter_surf.get_width() // 2, 250))

        # Score and lives
        stats = f"Score: {self.score}   Lives: {self.lives}"
        stats_surf, _ = self.text_font.render(stats, self.ACCENT)
        self.screen.blit(stats_surf, (450 - stats_surf.get_width() // 2, 450))

        # High score
        if self.high_score > 0:
            hs_surf, _ = self.small_font.render(f"High: {self.high_score}", self.ACCENT)
            self.screen.blit(hs_surf, (450 - hs_surf.get_width() // 2, 490))

        # Controls hint
        controls = "Type the letter | Ctrl+Space = score | Esc = pause"
        ctrl_surf, _ = self.small_font.render(controls, self.FG)
        self.screen.blit(ctrl_surf, (450 - ctrl_surf.get_width() // 2, 550))

    # ========== Game Logic Methods (Your Custom Code) ==========

    def spawn_letter(self):
        """Spawn a new letter for the player to type."""
        self.current_letter = random.choice('abcdefghijklmnopqrstuvwxyz')
        self.time_remaining = 3.0  # 3 seconds to type it

        # Announce for screen reader users
        self.speech.say(self.current_letter.upper(), priority=False)

    def check_letter(self, char):
        """Check if typed letter is correct."""
        if char == self.current_letter:
            # Correct!
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score

            # Play success sound
            self.play_sound(sounds.letter_hit())

            # Spawn next letter
            self.spawn_letter()
        else:
            # Wrong letter
            self.play_sound(sounds.letter_miss())

    def lose_life(self):
        """Player loses a life."""
        self.lives -= 1
        self.play_sound(sounds.life_lost())

        if self.lives > 0:
            self.speech.say(f"Time's up! {self.lives} lives left.", priority=True)
            self.spawn_letter()
        else:
            # Game over - show results and return to menu
            self.running = False
            self.mode = "MENU"
            self.play_sound(sounds.game_over())

            # Show results dialog (accessible, screen reader friendly)
            results = f"""GAME OVER

Final Score: {self.score}
High Score: {self.high_score}

Thanks for playing!
"""
            self.show_game_results(results)

            # Return to game menu
            self.say_game_menu()


# ========== NOTES FOR GAME DEVELOPERS ==========
"""
IMPORTANT PATTERNS FOR ALL GAMES:

1. ALWAYS inherit from BaseGame
2. Set NAME, DESCRIPTION, INSTRUCTIONS, HOTKEYS
3. Implement: start_playing(), handle_game_input(), draw_game()
4. Optionally implement: update() if you need frame-by-frame logic

ACCESSIBILITY REQUIREMENTS:
- Announce all game events via self.speech.say()
- Use sounds from games.sounds for audio feedback
- Support Ctrl+Space to repeat score/status
- Support Escape to pause/exit
- Make everything playable with keyboard only (no mouse)
- Announce letters/words/targets when they appear
- Provide clear audio/speech feedback for hits/misses

SOUND USAGE:
- sounds.letter_hit() - Correct letter typed
- sounds.letter_miss() - Wrong letter typed
- sounds.combo_sound(level) - Combo achieved
- sounds.powerup_sound() - Powerup collected
- sounds.life_lost() - Lost a life
- sounds.game_over() - Game over
- sounds.speed_up() - Speed increased

MENU STRUCTURE (Handled by BaseGame):
- Play Game → calls your start_playing()
- Game Info → shows combined description + instructions dialog
- Keyboard Controls → shows keyboard controls dialog
- Back to Games → returns to games menu

INFO SCREENS USE ACCESSIBLE DIALOGS:
All games should use show_info_dialog() for info screens, NOT speech.say().
This allows screen reader users to navigate content line by line.

The default implementation combines DESCRIPTION and INSTRUCTIONS into
a single "Game Info" dialog. You can override show_game_info() if needed.

Example (override show_controls() if you need custom formatting):
    def show_controls(self):
        content = \"\"\"KEYBOARD CONTROLS

        What it does: Key Name
        Another action: Another Key

        --- End of file ---
        \"\"\"
        self.show_info_dialog(f"{self.NAME} - Keyboard Controls", content)

NOTE: HOTKEYS format should be "Description: Key" (one per line).
Example:
    HOTKEYS = \"\"\"Type letters: Letter keys
Pause game: Escape
Repeat score: Ctrl+Space\"\"\"

GAME OVER PATTERN:
Always show results dialog and return to menu:
1. Set self.running = False and self.mode = "MENU"
2. Play game over sound
3. Show results dialog with final score/stats
4. Return to game menu (call self.say_game_menu())

Example (see lose_life() method above):
    results = f\"\"\"GAME OVER

Final Score: {self.score}
High Score: {self.high_score}

Great job!
\"\"\"
    self.show_game_results(results)  # Shows accessible dialog
    self.say_game_menu()  # Return to menu

RESULTS DIALOG:
Use self.show_game_results(content) to show final scores/stats.
- Shows in accessible dialog (same as speed test results)
- Screen reader users can navigate line by line
- Uses monospace font to preserve alignment
- User presses Enter/Escape to close and return to menu

All menu navigation and announcements are handled automatically!
"""
