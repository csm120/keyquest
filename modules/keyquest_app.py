#!python3.9
# KeyQuest (Enhanced Learning System)
#
# - System theme detection (dark/light/high contrast), defaults to white on black
# - Adaptive difficulty based on real-time performance tracking
# - NEW: WPM requirement - minimum 20 WPM for lessons 6+ (when phrases are introduced)
# - NEW: Variable-length lessons - shorter for excelling students (min 12), longer for struggling (max 30)
# - NEW: Early completion - finish after 12 items if accuracy > 90% and 5+ consecutive correct
# - NEW: Auto-extension - struggling students get 5-10 more practice items automatically
# - NEW: Options menu - customize speech mode (auto/screen reader/tts/off) and visual theme
# - NEW: Lesson intro screens - learn where keys are BEFORE typing!
# - NEW: Key finding requirement - must find new keys to start lesson
# - NEW: Progressive pitch sounds - rising tone as you complete each word
# - NEW: Tutorial-style guidance - help when you make 3+ errors
# - NEW: Auto-advance to next lesson on good performance!
# - NEW: Lesson unlocking system - master lessons to unlock new ones
# - NEW: Lesson selection menu - replay any unlocked lesson
# - NEW: 33 lessons - covers entire 104-key keyboard including function keys!
# - NEW: Descriptive lesson names (e.g., "Letter A (Left Pinky)")
# - NEW: Touch-typing instructions for finding keys by feel
# - NEW: Lesson 0 adds 'a' (first new key!) - no boring space-only practice
# - NEW: Gradual left homerow introduction (a, s, d, f one at a time)
# - IMPROVED: Lessons start where tutorial left off (use space, learn letters!)
# - IMPROVED: Much more randomization in lesson content (varied lengths, mixed types)
# - IMPROVED: Faster progression (80% accuracy, smaller batches of 6 vs 8)
# - IMPROVED: No chatter between keystrokes - just beeps and clear prompts
# - IMPROVED: Clear error feedback - "Type [target]" instead of "Remaining: [text]"
# - Builds words, phrases, and sentences as skill progresses
# - Non-consecutive key tracking for advancement
# - Improved tutorial with gradual Enter and Control key integration
# - Expanded speed test sentences for fast typers
# - Smart review system: slow down on struggles, give wins, return to challenges

import sys
import os
import time
import random
import threading
import traceback
import json
import webbrowser
from collections import Counter
from typing import Optional, Tuple

# Program modules
from modules.app_paths import get_app_dir
from modules import dialog_manager
from modules import audio_manager
from modules import results_formatter
from modules import state_manager
from modules import lesson_manager
from modules import menu_handler
from modules import keyboard_explorer
from modules import badge_manager
# Phase 2 modules
from modules import xp_manager
from modules import challenge_manager
from modules import quest_manager
from modules import dashboard_manager
# Phase 4 modules
from modules import currency_manager
from modules.speech_manager import Speech
from modules import config as app_config
from modules import theme as theme_manager
from modules import error_logging
from modules import sentences_manager
from modules import streak_manager
from modules import test_modes
from modules import input_utils
from modules import phonetics
from modules import speech_format
from modules import tutorial_data
from modules import lesson_intro_mode
from modules import lesson_mode
from modules import sound_catalog
from modules import sound_demo
from modules import learn_sounds_mode
from modules.escape_guard import EscapePressGuard
from modules import shop_mode
from modules import pet_mode
from modules import pet_manager
from modules import progress_views
from modules import notifications
from modules.version import __version__
from ui.render_menus import draw_main_menu, draw_lesson_menu, draw_games_menu
from ui.render_shop import draw_shop
from ui.render_pet import draw_pet
from ui.render_options import draw_options
from ui.render_results import draw_results_screen
from ui.render_lesson import draw_lesson_screen
from ui.render_test_setup import draw_test_setup_screen, draw_practice_setup_screen
from ui.render_lesson_intro import draw_lesson_intro_screen
from ui.render_learn_sounds import draw_learn_sounds_menu
from ui.render_test_active import draw_test_screen, draw_practice_screen
from ui.render_keyboard_explorer import draw_keyboard_explorer_screen
from ui.render_free_practice_ready import draw_free_practice_ready_screen
from ui.render_tutorial import draw_tutorial_screen
from ui.text_wrap import wrap_text

# Optional wxPython for accessible dialogs
try:
    import wx
    WX_AVAILABLE = True
except Exception:
    wx = None
    WX_AVAILABLE = False

# Pygame
import pygame
import pygame.freetype
import numpy as np

# Games
from games import LetterFallGame
from games import HangmanGame
from games.word_typing import WordTypingGame

# ----------------- Config -----------------
SCREEN_W, SCREEN_H = app_config.SCREEN_W, app_config.SCREEN_H
FONT_NAME = app_config.FONT_NAME
TITLE_SIZE, TEXT_SIZE, SMALL_SIZE = app_config.TITLE_SIZE, app_config.TEXT_SIZE, app_config.SMALL_SIZE

SYSTEM_THEME = theme_manager.detect_theme()
BG, FG, ACCENT, HILITE = theme_manager.get_theme_colors(SYSTEM_THEME)


def _detect_dpi_scale() -> float:
    """Return the system DPI scale factor (1.0 = 100%, 1.25 = 125%, etc.)."""
    try:
        import ctypes
        dpi = ctypes.windll.user32.GetDpiForSystem()
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0

# Lesson configuration constants moved to modules/lesson_manager.py
# Access as: lesson_manager.lesson_manager.LESSON_BATCH, lesson_manager.lesson_manager.MIN_WPM, etc.



# ----------------- Lesson System Data -----------------
# All lesson data moved to modules/lesson_manager.py
# Access as: lesson_manager.lesson_manager.STAGE_LETTERS, lesson_manager.lesson_manager.LESSON_NAMES, etc.






# ---- Audio ---- (now handled by audio_manager module)

# ----------------- State & Data Classes -----------------
# All state classes moved to modules/state_manager.py
# Import them as: state_manager.AppState, state_manager.Settings, etc.

# ----------------- Main App -----------------
class KeyQuestApp:
    def __init__(self):
        # CRITICAL: Initialize wx.App FIRST before pygame
        # This prevents crashes when showing modal dialogs later
        try:
            import wx
            if not wx.App.Get():
                self.wx_app = wx.App(False)
                print("wx.App initialized at startup")
        except ImportError:
            self.wx_app = None
            print("wxPython not available - dialogs will print to console")
        except Exception as e:
            self.wx_app = None
            print(f"Warning: Could not initialize wx.App: {e}")

        try:
            # Lower mixer buffer for snappier short typing sounds.
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.init()
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
        except Exception as e:
            error_logging.log_exception(e)
            raise

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Key Quest")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.freetype.SysFont(FONT_NAME, TITLE_SIZE)
        self.text_font = pygame.freetype.SysFont(FONT_NAME, TEXT_SIZE)
        self.small_font = pygame.freetype.SysFont(FONT_NAME, SMALL_SIZE)

        self.state = state_manager.AppState()
        self.speech = Speech()
        self.state.backend_label = self._backend_label()
        self._last_speech_backend_check = 0.0
        self._startup_menu_event = pygame.USEREVENT + 1
        self._startup_menu_armed = False
        self.escape_guard = EscapePressGuard()

        # Visual flash feedback state (deaf/HoH users — visual equivalent of beep_ok/bad)
        self._flash_color = (0, 0, 0)
        self._flash_until = 0.0

        # Escape guard visual state — shows remaining presses needed
        self._escape_remaining: int = 0
        self._escape_noun: str = ""

        # Initialize managers
        self.audio = audio_manager.AudioManager()
        self.progress_manager = state_manager.ProgressManager()
        self.speed_test_sentences = []
        self.practice_sentences = []
        self.practice_setup_options = []
        self.practice_setup_index = 0
        self.practice_topic_options = []
        self.practice_topic_index = 0
        self.practice_setup_view = "menu"

        # Initialize games
        fonts = {
            'title_font': self.title_font,
            'text_font': self.text_font,
            'small_font': self.small_font
        }
        self.games = [
            LetterFallGame(
                self.screen,
                fonts,
                self.speech,
                self.audio.play_wave,
                self.show_info_dialog,
                self.handle_game_session_complete,
            ),
            WordTypingGame(
                self.screen,
                fonts,
                self.speech,
                self.audio.play_wave,
                self.show_info_dialog,
                self.handle_game_session_complete,
            ),
            HangmanGame(
                self.screen,
                fonts,
                self.speech,
                self.audio.play_wave,
                self.show_info_dialog,
                self.handle_game_session_complete,
            ),
        ]
        self.current_game = None
        self.game_time = 0

        self.load_progress()

        # Apply user font scale (or DPI auto-detect) after settings are loaded.
        self._rebuild_fonts()

        # Check and update daily streak
        self.check_and_update_streak()

        # Phase 2: Initialize quests
        quest_manager.initialize_quests(self.state.settings)

        # Phase 2: Check and reset daily challenge if new day
        if challenge_manager.check_if_new_day(self.state.settings):
            challenge_manager.reset_daily_challenge(self.state.settings)
            self.save_progress()

        # Load practice sentences based on language setting
        self.speed_test_sentences = sentences_manager.load_speed_test_sentences()
        self.practice_sentences = sentences_manager.load_practice_sentences(self.state.settings.sentence_language)
        print(f"Loaded {len(self.practice_sentences)} practice sentences in {self.state.settings.sentence_language}")

        # Initialize menu system
        self._init_menus()

    def _init_menus(self):
        """Initialize all menu objects."""
        # Main menu
        self.main_menu = menu_handler.Menu(
            name="Main",
            items=self.state.menu_items,
            speech_system=self.speech,
            on_select_callback=self._handle_main_menu_select,
            initial_announcement=lambda: menu_handler.build_main_menu_announcement(
                self.state.menu_items[self.main_menu.current_index],
                self.get_streak_announcement()
            ),
            on_escape_callback=self._quit_app,
            enable_letter_nav=True
        )

        # Lesson menu (dynamic items)
        self.lesson_menu = menu_handler.Menu(
            name="Lesson",
            items=lambda: sorted(list(self.state.settings.unlocked_lessons)),
            speech_system=self.speech,
            on_select_callback=self.start_lesson,
            get_item_text_func=self._get_lesson_item_text,
            initial_announcement=lambda: self._get_lesson_menu_announcement(),
            on_escape_callback=self._return_to_main_menu
        )

        # Games menu
        self.games_menu = menu_handler.Menu(
            name="Games",
            items=self.games,
            speech_system=self.speech,
            on_select_callback=lambda game: self.start_game(self.games.index(game)),
            get_item_text_func=lambda game: f"{game.NAME}. {game.DESCRIPTION}",
            initial_announcement=lambda: self._get_games_menu_announcement(),
            on_escape_callback=self._return_to_main_menu
        )

        # Learn Sounds menu
        self.sound_items = list(sound_catalog.SOUND_ITEMS)
        self.sounds_menu = menu_handler.Menu(
            name="Learn Sounds",
            items=self.sound_items,
            speech_system=self.speech,
            on_select_callback=self._play_sound_demo,
            get_item_text_func=lambda item: f"{item['name']}. {item['description']}",
            initial_announcement=lambda: "Learn Sounds menu. Press Enter or Space on a sound to hear it. Press Escape to return to the main menu.",
            on_escape_callback=self._return_to_main_menu
        )

        # About menu
        self.about_items = [
            {
                "id": "app",
                "display": f"Application: KeyQuest {__version__}",
                "speak": f"Application: KeyQuest version {__version__}.",
            },
            {
                "id": "release_date",
                "display": "Release Date: 2026-02-19",
                "speak": "Release date: February 19, 2026.",
            },
            {
                "id": "name",
                "display": "Name: Casey Mathews",
                "speak": "Name: Casey Mathews.",
            },
            {
                "id": "company",
                "display": "Company: Web Friendly Help",
                "speak": "Company: Web Friendly Help.",
            },
            {
                "id": "tagline",
                "display": "Tagline: Helping You Tame Your Access Technology",
                "speak": "Tagline: Helping You Tame Your Access Technology.",
            },
            {
                "id": "copyright",
                "display": "Copyright: (c) 2026 Casey Mathews and Web Friendly Help",
                "speak": "Copyright 2026 Casey Mathews and Web Friendly Help.",
            },
            {
                "id": "license",
                "display": "License: MIT (free to use, modify, and distribute)",
                "speak": "License: M I T. Free to use, modify, and distribute.",
            },
            {
                "id": "website",
                "display": "Website: webfriendlyhelp.com",
                "speak": "Website: webfriendlyhelp.com. Press Enter to open in your browser.",
            },
            {
                "id": "credits",
                "display": "Credits: Built with Python and Pygame",
                "speak": "Credits: Built with Python and Pygame.",
            },
            {
                "id": "back",
                "display": "Back to Main Menu",
                "speak": "Back to Main Menu.",
            },
        ]
        self.about_menu = menu_handler.Menu(
            name="About",
            items=self.about_items,
            speech_system=self.speech,
            on_select_callback=self._handle_about_select,
            get_item_text_func=lambda item: item["speak"],
            initial_announcement=self._get_about_menu_announcement,
            on_escape_callback=self._return_to_main_menu,
        )

        # Options menu
        self.options_menu = menu_handler.OptionsMenu(
            name="Options",
            options=[
                {
                    'name': 'speech_mode',
                    'get_value': lambda: self.state.settings.speech_mode,
                    'set_value': lambda v: setattr(self.state.settings, 'speech_mode', v),
                    'get_text': lambda: f"Speech: {self.state.settings.speech_mode}",
                    'get_explanation': lambda: menu_handler.get_speech_mode_explanation(self.state.settings.speech_mode),
                    'cycle': menu_handler.cycle_speech_mode
                },
                {
                    'name': 'typing_sound_intensity',
                    'get_value': lambda: self.state.settings.typing_sound_intensity,
                    'set_value': lambda v: setattr(self.state.settings, 'typing_sound_intensity', v),
                    'get_text': lambda: f"Typing Sounds: {self.state.settings.typing_sound_intensity}",
                    'get_explanation': lambda: menu_handler.get_typing_sound_intensity_explanation(self.state.settings.typing_sound_intensity),
                    'cycle': menu_handler.cycle_typing_sound_intensity
                },
                {
                    'name': 'tts_rate',
                    'get_value': lambda: self.state.settings.tts_rate,
                    'set_value': lambda v: setattr(self.state.settings, 'tts_rate', v),
                    'get_text': lambda: f"TTS Rate: {self.state.settings.tts_rate} WPM",
                    'get_explanation': lambda: menu_handler.get_tts_rate_explanation(self.state.settings.tts_rate),
                    'cycle': menu_handler.cycle_tts_rate
                },
                {
                    'name': 'tts_volume',
                    'get_value': lambda: self.state.settings.tts_volume,
                    'set_value': lambda v: setattr(self.state.settings, 'tts_volume', v),
                    'get_text': lambda: f"TTS Volume: {int(self.state.settings.tts_volume * 100)}%",
                    'get_explanation': lambda: menu_handler.get_tts_volume_explanation(self.state.settings.tts_volume),
                    'cycle': menu_handler.cycle_tts_volume
                },
                {
                    'name': 'tts_voice',
                    'get_value': lambda: self.state.settings.tts_voice,
                    'set_value': lambda v: setattr(self.state.settings, 'tts_voice', v),
                    'get_text': lambda: f"TTS Voice: {menu_handler.get_voice_name_from_id(self.state.settings.tts_voice, self.speech.get_available_voices())}",
                    'get_explanation': lambda: menu_handler.get_tts_voice_explanation(menu_handler.get_voice_name_from_id(self.state.settings.tts_voice, self.speech.get_available_voices())),
                    'cycle': lambda v, d: menu_handler.cycle_tts_voice(v, self.speech.get_available_voices(), d)
                },
                {
                    'name': 'visual_theme',
                    'get_value': lambda: self.state.settings.visual_theme,
                    'set_value': lambda v: setattr(self.state.settings, 'visual_theme', v),
                    'get_text': lambda: f"Visual Theme: {self.state.settings.visual_theme}",
                    'get_explanation': lambda: menu_handler.get_theme_explanation(self.state.settings.visual_theme),
                    'cycle': menu_handler.cycle_theme
                },
                {
                    'name': 'sentence_language',
                    'get_value': lambda: self.state.settings.sentence_language,
                    'set_value': lambda v: setattr(self.state.settings, 'sentence_language', v),
                    'get_text': lambda: f"Practice Topic: {self.state.settings.sentence_language}",
                    'get_explanation': lambda: menu_handler.get_language_explanation(self.state.settings.sentence_language),
                    'cycle': menu_handler.cycle_language
                },
                {
                    'name': 'font_scale',
                    'get_value': lambda: self.state.settings.font_scale,
                    'set_value': lambda v: setattr(self.state.settings, 'font_scale', v),
                    'get_text': lambda: f"Font Size: {self.state.settings.font_scale}",
                    'get_explanation': lambda: menu_handler.get_font_scale_explanation(self.state.settings.font_scale),
                    'cycle': menu_handler.cycle_font_scale
                }
            ],
            speech_system=self.speech,
            on_change_callback=self._handle_option_change,
            initial_announcement=lambda: self._get_options_menu_announcement(),
            on_escape_callback=self._return_to_main_menu_and_save
        )

    def _handle_main_menu_select(self, choice):
        """Handle main menu item selection."""
        # Strip the hotkey suffix (e.g., ": T") from the choice
        if ": " in choice:
            choice = choice.rsplit(": ", 1)[0]

        if choice == "Tutorial":
            self.start_tutorial()
        elif choice == "Keyboard Explorer":
            self.start_keyboard_explorer()
        elif choice == "Lessons":
            self.show_lesson_menu()
        elif choice == "Free Practice":
            self.start_free_practice_setup()
        elif choice == "Speed Test":
            self.start_test()
        elif choice == "Sentence Practice":
            self.start_practice()
        elif choice == "Games":
            self.show_games_menu()
        elif choice == "Pet Shop":
            self.show_shop()
        elif choice == "Pets":
            self.show_pet()
        elif choice in ("Badges", "View Badges"):
            self.show_badge_viewer()
        elif choice in ("Quests", "View Quests"):
            self.show_quest_viewer()
        elif choice == "Progress Dashboard":
            self.show_progress_dashboard()
        elif choice == "Daily Challenge":
            self.show_daily_challenge()
        elif choice == "Key Performance":
            self.show_key_performance_report()
        elif choice == "Options":
            self.show_options_menu()
        elif choice == "Learn Sounds":
            self.show_learn_sounds_menu()
        elif choice == "About":
            self.show_about_menu()
        elif choice == "Quit":
            self._quit_app()

    def _get_about_menu_announcement(self) -> str:
        return (
            f"About menu. KeyQuest version {__version__}. Name: Casey Mathews. Company: Web Friendly Help. "
            "Use Up and Down to choose. Press Enter or Space to select. "
            "Press Escape to return to main menu."
        )

    def _handle_about_select(self, item):
        item_id = item.get("id", "")
        if item_id == "website":
            self.speech.say("Opening webfriendlyhelp dot com.", priority=True)
            try:
                webbrowser.open("https://webfriendlyhelp.com", new=2)
            except Exception:
                self.speech.say("Unable to open website.", priority=True)
            return
        if item_id == "back":
            self._return_to_main_menu()
            return
        self.speech.say(item.get("speak", item.get("display", "")), priority=True)

    def _handle_option_change(self, option_index, old_value, new_value):
        """Handle option value change."""
        option_name = self.options_menu.options[option_index]["name"]

        if option_name == "speech_mode":
            self.apply_speech_mode()
            # Apply TTS settings when switching to TTS mode
            if new_value == 'tts':
                self.apply_tts_settings()
        elif option_name == "typing_sound_intensity":
            self.apply_typing_sound_intensity()
        elif option_name == "tts_rate":
            self.apply_tts_settings()
        elif option_name == "tts_volume":
            self.apply_tts_settings()
        elif option_name == "tts_voice":
            self.apply_tts_settings()
        elif option_name == "visual_theme":
            self.apply_visual_theme()
        elif option_name == "sentence_language":
            print(f"Language changed from {old_value} to {new_value}")
            self.practice_sentences = sentences_manager.load_practice_sentences(new_value)
            print(f"Reloaded {len(self.practice_sentences)} practice sentences in {new_value}")
            if self.practice_sentences:
                print(f"First sentence: {self.practice_sentences[0]}")
                print(f"Last sentence: {self.practice_sentences[-1]}")
        elif option_name == "font_scale":
            self._rebuild_fonts()

    def _quit_app(self):
        """Quit the application."""
        try:
            self.screen.fill(BG)
            goodbye_font = pygame.font.SysFont(FONT_NAME, 56)
            goodbye_surface = goodbye_font.render("Goodbye!", True, FG)
            goodbye_rect = goodbye_surface.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2))
            self.screen.blit(goodbye_surface, goodbye_rect)
            pygame.display.flip()
        except Exception:
            pass

        self.speech.say("Goodbye.", priority=True, protect_seconds=1.2, interrupt=False)
        pygame.time.wait(900)
        pygame.quit()
        import sys
        sys.exit(0)

    def _return_to_main_menu(self):
        """Return to main menu (preserves last position)."""
        self.state.mode = "MENU"
        # Don't reset index - preserve user's last position
        # Wrap announce in try/except in case called immediately after wx dialog
        # (pygame/wx event loop conflict can cause issues)
        try:
            self.main_menu.announce_current()
        except Exception as e:
            # If announcement fails (e.g., after wx dialog), log but don't crash
            print(f"Warning: Menu announcement failed: {e}")
            # Will be announced on next user interaction anyway

    def _return_to_main_menu_and_save(self):
        """Return to main menu and save progress."""
        self.save_progress()
        self._return_to_main_menu()

    def _get_lesson_item_text(self, lesson_num: int) -> str:
        """Get display text for a lesson menu item with star rating.

        Args:
            lesson_num: Lesson number

        Returns:
            Formatted lesson text with stars if earned
        """
        lesson_name = lesson_manager.LESSON_NAMES[lesson_num]
        stars = self.state.settings.lesson_stars.get(lesson_num, 0)

        if stars > 0:
            star_display = "*" * stars
            return f"Lesson {lesson_num}: {lesson_name} {star_display}"
        else:
            return f"Lesson {lesson_num}: {lesson_name}"

    def _get_lesson_menu_announcement(self):
        """Get lesson menu initial announcement."""
        unlocked = sorted(list(self.state.settings.unlocked_lessons))
        if unlocked:
            first_lesson = unlocked[0]
            lesson_name = lesson_manager.LESSON_NAMES[first_lesson]
            return menu_handler.build_lesson_menu_announcement(lesson_name)
        return "Lesson menu. No lessons available."

    def _get_games_menu_announcement(self):
        """Get games menu initial announcement."""
        if self.games:
            first_game = self.games[0]
            return menu_handler.build_games_menu_announcement(first_game.NAME, first_game.DESCRIPTION)
        return "Games menu. No games available."

    def _get_options_menu_announcement(self):
        """Get options menu initial announcement."""
        options = menu_handler.get_options_items(self.state.settings)
        explanation = menu_handler.get_speech_mode_explanation(self.state.settings.speech_mode)
        return menu_handler.build_options_menu_announcement(options[0], explanation)

    def load_progress(self):
        """Load progress from file using ProgressManager."""
        self.progress_manager.load(self.state, len(lesson_manager.STAGE_LETTERS))
        # Apply loaded settings
        self.apply_speech_mode()
        self.apply_typing_sound_intensity()
        self.apply_tts_settings()
        self.apply_visual_theme()

    def save_progress(self):
        """Save progress to file using ProgressManager."""
        self.progress_manager.save(self.state)

    def check_and_update_streak(self):
        """Check and update the daily practice streak."""
        prev_streak = self.state.settings.current_streak
        prev_date = self.state.settings.last_practice_date

        milestone = streak_manager.check_and_update_streak(self.state.settings)

        if milestone is not None:
            self.audio.play_success()
            self.speech.say(
                f"Streak milestone! Day {milestone} of your typing streak! Keep it up!",
                priority=True,
                protect_seconds=3.0,
            )

        if (
            self.state.settings.current_streak != prev_streak
            or self.state.settings.last_practice_date != prev_date
        ):
            self.save_progress()

    def get_streak_announcement(self):
        """Get the current streak announcement for the menu."""
        return streak_manager.get_streak_announcement(self.state.settings)

    def _backend_label(self) -> str:
        if self.speech.backend == "tolk":
            return "Screen Reader"
        if self.speech.backend == "tts":
            return "TTS"
        return "No Speech"


    def show_results_dialog(self, results_text: str):
        """Show results in an accessible dialog (uses universal dialog system)."""
        dialog_manager.show_results_dialog("Speed Test Results", results_text)

    def show_info_dialog(self, title: str, content: str):
        """Show informational content in an accessible dialog (uses universal dialog system)."""
        dialog_manager.show_info_dialog(title, content)

    def show_badge_notifications(self):
        """Show any pending badge unlock notifications."""
        notifications.show_badge_notifications(self)

    def show_level_up_notification(self, xp_result: dict):
        """Show level-up notification.

        Args:
            xp_result: Result from xp_manager.award_xp with level info
        """
        notifications.show_level_up_notification(self, xp_result)

    def show_quest_notifications(self):
        """Show any pending quest completion notifications."""
        notifications.show_quest_notifications(self)

    def apply_pet_session_progress(self, recent_performance: dict, xp_amount: int) -> dict:
        """Update pet mood/xp from session performance and announce key changes."""
        result = pet_manager.apply_session_pet_progress(
            self.state.settings,
            recent_performance=recent_performance,
            xp_amount=xp_amount,
        )
        if not result.get("has_pet"):
            return result

        pet_status = pet_manager.get_pet_status(self.state.settings)
        pet_name = pet_status.get("pet_name", "Your pet")

        if result.get("evolved"):
            self.audio.play_pet_evolve()
            self.speech.say(
                f"{pet_name} evolved to stage {result['new_stage']}!",
                priority=True,
                protect_seconds=2.0,
            )
        elif result.get("mood_changed"):
            self.audio.play_pet_sound(self.state.settings.pet_type)
            self.speech.say(
                f"{pet_name} is feeling {result['mood']}. {result['mood_message']}",
                priority=True,
                protect_seconds=2.0,
            )

        return result

    def handle_game_session_complete(self, game, session_stats: Optional[dict] = None) -> None:
        """Apply cross-system updates when any game session ends.

        Games report their metrics through BaseGame.show_game_results(). Future games
        only need to call that method with optional session_stats.
        """
        stats = session_stats or {}
        accuracy = float(stats.get("accuracy", 80.0))
        if accuracy < 0:
            accuracy = 0.0
        if accuracy > 100:
            accuracy = 100.0

        duration_minutes = float(stats.get("session_duration_minutes", 1.0))
        if duration_minutes < 0:
            duration_minutes = 0.0

        game_xp = int(stats.get("pet_xp", 12))
        if game_xp <= 0:
            game_xp = 12

        self.apply_pet_session_progress(
            recent_performance={
                "new_best_wpm": False,
                "new_best_accuracy": False,
                "accuracy": accuracy,
                "session_duration": duration_minutes,
                "streak_broken": False,
            },
            xp_amount=game_xp,
        )
        self.save_progress()

    def show_badge_viewer(self):
        """Show all earned and locked badges."""
        progress_views.show_badge_viewer(self)

    def show_quest_viewer(self):
        """Show active and completed quests."""
        progress_views.show_quest_viewer(self)

    def show_progress_dashboard(self):
        """Show comprehensive progress dashboard."""
        progress_views.show_progress_dashboard(self)

    def show_daily_challenge(self):
        """Show today's daily challenge."""
        progress_views.show_daily_challenge(self)

    def show_key_performance_report(self):
        """Show keyboard performance analytics."""
        progress_views.show_key_performance_report(self)

    # ==================== SHOP ====================

    def show_shop(self):
        """Show shop interface for purchasing items."""
        shop_mode.show_shop(self)

    def handle_shop_input(self, event, mods):
        """Handle shop navigation and purchases."""
        shop_mode.handle_shop_input(self, event, mods)

    def _announce_shop_item(self, item_id: str):
        """Announce a shop item with details."""
        shop_mode.announce_shop_item(self, item_id)

    def _purchase_shop_item(self, item_id: str):
        """Attempt to purchase a shop item."""
        shop_mode.purchase_shop_item(self, item_id)

    # ==================== PET ====================

    def show_pet(self):
        """Show pet interface."""
        pet_mode.show_pet(self)

    def handle_pet_input(self, event, mods):
        """Handle pet navigation and interactions."""
        pet_mode.handle_pet_input(self, event, mods)

    def _announce_pet_type(self, pet_type: str):
        """Announce a pet type with description."""
        pet_mode.announce_pet_type(self, pet_type)

    def _handle_pet_action(self, action: str):
        """Handle pet actions."""
        pet_mode.handle_pet_action(self, action)

    # ==================== FREE PRACTICE MODE ====================

    def start_free_practice_setup(self):
        """Start Free Practice mode setup - allows practice without affecting progress."""
        # Collect all learned keys from unlocked lessons
        learned_keys = set()
        for lesson_num in sorted(self.state.settings.unlocked_lessons):
            if lesson_num < len(lesson_manager.STAGE_LETTERS):
                learned_keys.update(lesson_manager.STAGE_LETTERS[lesson_num])

        if not learned_keys:
            self.speech.say("No keys learned yet. Complete the tutorial first.", priority=True, protect_seconds=2.0)
            self._return_to_main_menu()
            return

        # Store available keys
        self.state.free_practice.available_keys = learned_keys
        self.state.free_practice.selected_keys = learned_keys.copy()  # Practice all keys by default

        # Announce and start
        announcement = (
            f"Free Practice Mode. Practice without affecting your progress. "
            f"You can practice with {len(learned_keys)} learned keys. "
            f"Press Enter to begin, or Escape to return to menu."
        )
        self.speech.say(announcement, priority=True, protect_seconds=3.0)

        # Go directly to practice
        self.state.mode = "FREE_PRACTICE_READY"

    def start_free_practice(self):
        """Start the free practice session."""
        self.state.mode = "FREE_PRACTICE"
        self.state.free_practice.in_session = True

        # Initialize lesson state for practice (reuse lesson mechanics)
        l = self.state.lesson
        l.stage = -1  # Flag for free practice (negative means no progress saving)
        l.tracker = state_manager.AdaptiveTracker()
        l.index = 0
        l.typed = ""
        l.use_words = True
        l.review_mode = False
        l.start_time = time.time()

        # Build batch with selected keys
        self.build_free_practice_batch()

        # Announce first word with instructions (like lessons do)
        target = l.batch_words[l.index]
        speakable = self._make_speakable(target)
        self.speech.say(
            f"Free practice. Control Space repeats. Type {speakable}",
            priority=True,
            protect_seconds=3.0,
        )

    def build_free_practice_batch(self):
        """Build a practice batch using selected keys."""
        l = self.state.lesson
        keys = list(self.state.free_practice.selected_keys)

        if not keys:
            keys = ['a', 's', 'd', 'f']  # Fallback to home row

        # Use lesson manager's word building logic
        l.batch_words = lesson_manager.generate_words_from_keys(keys, count=15, use_real_words=True)
        l.batch_instructions = []

    def handle_free_practice_ready_input(self, event, mods):
        """Handle input in Free Practice ready state."""
        if event.key == pygame.K_RETURN:
            self.start_free_practice()
        elif event.key == pygame.K_ESCAPE:
            self.state.free_practice.in_session = False
            self._return_to_main_menu()

    def end_free_practice(self):
        """End free practice session and show results."""
        l = self.state.lesson
        l.end_time = time.time()

        # Calculate statistics (but don't save to progress)
        duration = l.end_time - l.start_time
        accuracy = l.tracker.overall_accuracy() * 100
        wpm = l.tracker.calculate_wpm(duration)
        total_correct = l.tracker.total_correct
        total_attempts = l.tracker.total_attempts
        total_errors = total_attempts - total_correct
        minutes = duration / 60.0 if duration > 0 else 0.0
        gross_wpm = ((total_attempts / 5.0) / minutes) if minutes > 0 else 0.0

        # Format results
        results_text = (
            f"Free Practice Complete!\n\n"
            f"Accuracy: {accuracy:.0f}%\n"
            f"Corrected Words Per Minute: {wpm:.1f}\n"
            f"Total Words Per Minute: {gross_wpm:.1f}\n"
            f"Correct: {total_correct}\n"
            f"Errors: {total_errors}\n"
            f"Time: {duration:.1f} seconds\n\n"
            f"Results not saved (practice mode).\n\n"
            f"Press OK to return to menu."
        )

        # Show results
        self.audio.play_victory()
        self.show_results_dialog(results_text)

        # Clean up and return to menu
        self.state.free_practice.in_session = False
        self.state.free_practice.selected_keys = set()
        self._return_to_main_menu()

    # =========================================================

    def _make_speakable(self, text: str) -> str:
        """Convert text to speakable form for screen readers."""
        return speech_format.spell_text_for_typing_instruction(text)

    def run(self):
        # Draw first frame before speaking (helps with initialization)
        self.draw()
        pygame.display.flip()

        # Arm a delayed startup menu announcement so screen reader title
        # announcement can finish first.
        pygame.time.set_timer(self._startup_menu_event, 1800)
        self._startup_menu_armed = True

        while True:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            self._refresh_auto_speech_backend()
            for event in pygame.event.get():
                try:
                    self.handle_event(event)
                except Exception as e:
                    error_logging.log_exception(e)
                    raise

            # Update game logic
            if self.state.mode == "GAME" and self.current_game:
                self.current_game.update(dt)

            self.draw()
            pygame.display.flip()

    def _refresh_auto_speech_backend(self):
        """Auto mode: keep backend in sync with screen reader runtime state."""
        now = time.time()
        if now - self._last_speech_backend_check < 1.0:
            return
        self._last_speech_backend_check = now

        if self.state.settings.speech_mode != "auto":
            return

        previous_backend = self.speech.backend
        if not self.speech.refresh_backend(self.state.settings.speech_mode):
            return

        self.state.backend_label = self._backend_label()

        if self.speech.backend == "tts":
            self.speech.say(
                "Screen reader not detected. Switched to text to speech.",
                priority=True,
                protect_seconds=1.5,
                interrupt=True,
            )
        elif self.speech.backend == "tolk" and previous_backend != "tolk":
            self.speech.say(
                "Screen reader detected. Switched to screen reader.",
                priority=True,
                protect_seconds=1.5,
                interrupt=True,
            )

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self._quit_app()
        if event.type == self._startup_menu_event:
            pygame.time.set_timer(self._startup_menu_event, 0)
            self._startup_menu_armed = False
            if self.state.mode == "MENU":
                self.say_menu(on_startup=True)
            return
        if event.type == pygame.KEYDOWN:
            if self._startup_menu_armed:
                pygame.time.set_timer(self._startup_menu_event, 0)
                self._startup_menu_armed = False
            mods = pygame.key.get_mods()
            if event.key == pygame.K_ESCAPE and self._handle_escape_shortcut():
                return
            if event.key != pygame.K_ESCAPE:
                self.escape_guard.reset()
                self._escape_remaining = 0
            if self.state.mode == "MENU":
                self.handle_menu_input(event, mods)
            elif self.state.mode == "KEYBOARD_EXPLORER":
                self.handle_keyboard_explorer_input(event, mods)
            elif self.state.mode == "LESSON_MENU":
                self.handle_lesson_menu_input(event)
            elif self.state.mode == "OPTIONS":
                self.handle_options_input(event)
            elif self.state.mode == "LESSON_INTRO":
                self.handle_lesson_intro_input(event, mods)
            elif self.state.mode == "TUTORIAL":
                self.handle_tutorial_input(event, mods)
            elif self.state.mode == "LESSON":
                self.handle_lesson_input(event, mods)
            elif self.state.mode == "TEST_SETUP":
                self.handle_test_setup_input(event)
            elif self.state.mode == "TEST":
                self.handle_test_input(event, mods)
            elif self.state.mode == "PRACTICE_SETUP":
                self.handle_practice_setup_input(event, mods)
            elif self.state.mode == "PRACTICE":
                self.handle_practice_input(event, mods)
            elif self.state.mode == "RESULTS":
                self.handle_results_input(event, mods)
            elif self.state.mode == "GAMES_MENU":
                self.handle_games_menu_input(event, mods)
            elif self.state.mode == "SHOP":
                self.handle_shop_input(event, mods)
            elif self.state.mode == "PET":
                self.handle_pet_input(event, mods)
            elif self.state.mode == "LEARN_SOUNDS_MENU":
                self.handle_learn_sounds_menu_input(event, mods)
            elif self.state.mode == "ABOUT":
                self.handle_about_input(event, mods)
            elif self.state.mode == "GAME":
                self.handle_game_input(event, mods)
            elif self.state.mode == "FREE_PRACTICE_READY":
                self.handle_free_practice_ready_input(event, mods)
            elif self.state.mode == "FREE_PRACTICE":
                self.handle_lesson_input(event, mods)  # Reuse lesson input handling

    def _escape_policy(self):
        """Return escape handling policy for current mode, or None."""
        mode = self.state.mode
        if mode == "KEYBOARD_EXPLORER":
            return {
                "context": "KEYBOARD_EXPLORER",
                "required_presses": 3,
                "action": "menu",
                "noun": "exit",
            }

        if mode == "PRACTICE":
            return {
                "context": "PRACTICE",
                "required_presses": 3,
                "action": "finish_practice",
                "noun": "finish",
            }

        active_modes = {
            "LESSON_INTRO",
            "TUTORIAL",
            "LESSON",
            "TEST",
            "FREE_PRACTICE",
            "FREE_PRACTICE_READY",
        }
        if mode in active_modes:
            return {
                "context": mode,
                "required_presses": 3,
                "action": "menu",
                "noun": "exit",
            }
        if mode == "GAME" and self.current_game:
            game_mode = getattr(self.current_game, "mode", "")
            if game_mode not in ("MENU", "RESULTS"):
                game_name = getattr(self.current_game, "NAME", "Game")
                return {
                    "context": f"{mode}:{game_name}:{game_mode}",
                    "required_presses": 3,
                    "action": "menu",
                    "noun": "exit",
                }
        return None

    def _handle_escape_shortcut(self) -> bool:
        """Handle configured Escape shortcuts; return True when consumed."""
        policy = self._escape_policy()
        if not policy:
            self.escape_guard.reset()
            self._escape_remaining = 0
            return False

        completed, remaining = self.escape_guard.register_escape(
            context=policy["context"],
            required_presses=policy["required_presses"],
        )
        if not completed:
            self._escape_remaining = remaining
            self._escape_noun = policy["noun"]
            self.speech.say(
                f"Escape. Press {remaining} more time{'s' if remaining != 1 else ''} to {policy['noun']}.",
                priority=True,
            )
            return True

        # Sequence complete — clear the visual counter.
        self._escape_remaining = 0
        self._escape_noun = ""

        if policy["action"] == "finish_practice":
            self.finish_practice()
            return True

        self.current_game = None
        self.state.mode = "MENU"
        self.speech.say("Exiting to main menu.", priority=True)
        self.say_menu()
        return True

    # ==================== MENU ====================
    def say_menu(self, on_startup: bool = False):
        """Announce the main menu."""
        if on_startup:
            item = self.main_menu.get_current_item()
            if item is not None:
                self.speech.say(
                    self.main_menu.get_item_text(item),
                    priority=False,
                    interrupt=False,
                )
            return
        self.main_menu.announce_menu()

    def handle_menu_input(self, event, mods):
        """Handle main menu input."""
        if event.key == pygame.K_SPACE and input_utils.mod_ctrl(mods):
            self.say_menu()
        else:
            self.main_menu.handle_input(event, mods)

    # ==================== LESSON MENU ====================
    def show_lesson_menu(self):
        """Show lesson selection menu."""
        self.state.mode = "LESSON_MENU"
        self.lesson_menu.reset_index()
        self.lesson_menu.announce_menu()

    def handle_lesson_menu_input(self, event):
        """Handle lesson menu navigation."""
        self.lesson_menu.handle_input(event)

    # ==================== GAMES MENU ====================
    def show_games_menu(self):
        """Show games selection menu."""
        self.state.mode = "GAMES_MENU"
        self.games_menu.reset_index()
        self.games_menu.announce_menu()

    def handle_games_menu_input(self, event, mods):
        """Handle games menu navigation."""
        if event.key == pygame.K_h:
            # Announce hotkeys (special case)
            game = self.games_menu.get_current_item()
            if game:
                self.speech.say(game.HOTKEYS, priority=True)
        else:
            self.games_menu.handle_input(event, mods)

    # ==================== LEARN SOUNDS MENU ====================
    def show_learn_sounds_menu(self):
        """Show learn sounds menu."""
        learn_sounds_mode.show_learn_sounds_menu(self)

    def handle_learn_sounds_menu_input(self, event, mods):
        """Handle learn sounds menu navigation."""
        learn_sounds_mode.handle_learn_sounds_menu_input(self, event, mods)

    def _play_sound_demo(self, sound_item):
        """Play a sound demonstration."""
        sound_demo.play_sound_demo(self.audio, sound_item["sound"])

    # ==================== ABOUT MENU ====================
    def show_about_menu(self):
        self.state.mode = "ABOUT"
        self.about_menu.reset_index()
        self.about_menu.announce_menu()

    def handle_about_input(self, event, mods):
        self.about_menu.handle_input(event, mods)

    def start_game(self, game_index):
        """Start a game."""
        self.current_game = self.games[game_index]
        self.state.mode = "GAME"
        self.game_time = time.time()
        self.current_game.start()

    def handle_game_input(self, event, mods):
        """Handle game input."""
        if self.current_game:
            result = self.current_game.handle_input(event, mods)
            if result == "GAMES_MENU":
                self.current_game = None
                self.show_games_menu()

    # ==================== OPTIONS MENU ====================
    def show_options_menu(self):
        """Show options menu."""
        self.state.mode = "OPTIONS"
        self.options_menu.reset_index()
        self.options_menu.announce_menu()

    def handle_options_input(self, event):
        """Handle options menu navigation and changes."""
        self.options_menu.handle_input(event)

    def apply_speech_mode(self):
        """Apply the selected speech mode and switch backends accordingly."""
        self.speech.apply_mode(self.state.settings.speech_mode)
        self.state.backend_label = self._backend_label()

    def apply_typing_sound_intensity(self):
        """Apply typing sound intensity from settings to audio manager."""
        self.audio.set_typing_sound_intensity(self.state.settings.typing_sound_intensity)

    def apply_tts_settings(self):
        """Apply TTS settings from state to speech engine."""
        self.speech.apply_tts_settings(
            rate=self.state.settings.tts_rate,
            volume=self.state.settings.tts_volume,
            voice_id=self.state.settings.tts_voice
        )

    def apply_visual_theme(self):
        """Apply the selected visual theme."""
        global BG, FG, ACCENT, HILITE
        theme = self.state.settings.visual_theme

        BG, FG, ACCENT, HILITE = theme_manager.get_theme_colors(theme)

    def _rebuild_fonts(self):
        """Recreate fonts at the user-selected (or DPI-auto) scale factor.

        Called once at startup (after load_progress) and whenever the
        Font Size option is changed.  Updates self.*_font and pushes the
        new font objects into every game object so they don't keep stale
        references.
        """
        scale_str = self.state.settings.font_scale
        if scale_str == "auto":
            scale = _detect_dpi_scale()
        else:
            try:
                scale = float(scale_str.rstrip("%")) / 100.0
            except Exception:
                scale = 1.0
        scale = max(1.0, min(scale, 2.0))  # clamp to sane range

        title_sz = max(24, round(TITLE_SIZE * scale))
        text_sz = max(18, round(TEXT_SIZE * scale))
        small_sz = max(14, round(SMALL_SIZE * scale))

        self.title_font = pygame.freetype.SysFont(FONT_NAME, title_sz)
        self.text_font = pygame.freetype.SysFont(FONT_NAME, text_sz)
        self.small_font = pygame.freetype.SysFont(FONT_NAME, small_sz)

        # Propagate to game objects that cache fonts at construction time.
        for game in self.games:
            game.title_font = self.title_font
            game.text_font = self.text_font
            game.small_font = self.small_font

    # ==================== TUTORIAL (IMPROVED) ====================
    def start_tutorial(self):
        self.state.mode = "TUTORIAL"
        t = self.state.tutorial
        t.phase = 1
        t.sequence = []
        t.counts_done = Counter()
        t.target_counts = {}
        t.key_errors = Counter()
        t.total_attempts = 0
        t.total_correct = 0
        t.phase_attempts = 0
        t.phase_correct = 0
        t.phase_mistakes = 0
        t.adaptive_mode = "normal"
        t.in_intro = False
        t.intro_items = []
        t.intro_index = 0
        t.guidance_message = ""
        t.hint_message = ""

        self._enter_tutorial_intro(1)

    def _start_tutorial_phase(self, phase: int):
        """Initialize a tutorial phase using adaptive pacing."""
        t = self.state.tutorial
        t.phase = phase
        t.phase_attempts = 0
        t.phase_correct = 0
        t.phase_mistakes = 0
        t.sequence, t.target_counts = tutorial_data.build_phase_sequence(
            phase=phase,
            mode=t.adaptive_mode,
            key_errors=t.key_errors,
        )
        random.shuffle(t.sequence)
        t.index = 0
        t.in_intro = False
        t.intro_items = []
        t.intro_index = 0

    def _finish_tutorial_phase(self):
        """Record phase performance and update adaptive mode for the next phase."""
        t = self.state.tutorial
        if t.phase_attempts <= 0:
            accuracy = 1.0
        else:
            accuracy = t.phase_correct / t.phase_attempts
        t.adaptive_mode = tutorial_data.next_mode_from_performance(accuracy, t.phase_mistakes)

    def _enter_tutorial_intro(self, phase: int):
        """Enter phase intro where user can review key locations before starting."""
        t = self.state.tutorial
        t.phase = phase
        t.in_intro = True
        t.intro_items = tutorial_data.get_intro_items_for_phase(phase)
        t.intro_index = 0

        phase_names = {
            1: "Space bar",
            2: "Arrow keys",
            3: "Enter",
            4: "Control",
            5: "Mixed review",
        }
        phase_title = phase_names.get(phase, "Next keys")
        if t.intro_items:
            key_name, desc = t.intro_items[t.intro_index]
            key_friendly = tutorial_data.FRIENDLY.get(key_name, key_name)
            self.speech.say(
                f"{phase_title} intro. {key_friendly}. {desc} "
                f"Use Up and Down arrows to review. Press Enter or Space to start practice.",
                priority=True,
                protect_seconds=4.0,
            )

    def load_tutorial_prompt(self):
        t = self.state.tutorial

        if t.index >= len(t.sequence):
            self._finish_tutorial_phase()
            if t.phase == 1:
                self._enter_tutorial_intro(2)
                return
            elif t.phase == 2:
                self._enter_tutorial_intro(3)
                return
            elif t.phase == 3:
                self._enter_tutorial_intro(4)
                return
            elif t.phase == 4:
                self._enter_tutorial_intro(5)
                return
            else:
                # Tutorial complete - play victory sound and show results
                self.audio.play_victory()

                # Create results summary
                t = self.state.tutorial
                results_text = results_formatter.ResultsFormatter.format_tutorial_results(
                    counts_done=t.counts_done,
                    friendly_names=tutorial_data.FRIENDLY
                )

                # Show results dialog (blocks until OK is pressed)
                self.show_results_dialog(results_text)

                # Return to menu after dialog closes
                self.state.mode = "MENU"
                self.say_menu()
                return

        name, key = t.sequence[t.index]
        t.required_name = name
        t.required_key = key
        self.speech.say(f"Press {tutorial_data.FRIENDLY[name]}", priority=True, protect_seconds=2.0)

    def handle_tutorial_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
            return

        t = self.state.tutorial
        if event.key == pygame.K_SPACE and input_utils.mod_ctrl(mods):
            if t.in_intro and t.intro_items:
                name, desc = t.intro_items[t.intro_index]
                key_friendly = tutorial_data.FRIENDLY.get(name, name)
                self.speech.say(
                    f"{key_friendly}. {desc}. Press Enter or Space to start practice.",
                    priority=True,
                    protect_seconds=3.0,
                )
            else:
                self.speech.say(f"Press {tutorial_data.FRIENDLY[self.state.tutorial.required_name]}", priority=True, protect_seconds=2.0)
            return

        if t.in_intro:
            if event.key == pygame.K_UP and t.intro_items:
                t.intro_index = (t.intro_index - 1) % len(t.intro_items)
                name, desc = t.intro_items[t.intro_index]
                key_friendly = tutorial_data.FRIENDLY.get(name, name)
                self.speech.say(f"{key_friendly}. {desc}")
                return
            if event.key == pygame.K_DOWN and t.intro_items:
                t.intro_index = (t.intro_index + 1) % len(t.intro_items)
                name, desc = t.intro_items[t.intro_index]
                key_friendly = tutorial_data.FRIENDLY.get(name, name)
                self.speech.say(f"{key_friendly}. {desc}")
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._start_tutorial_phase(t.phase)
                self.load_tutorial_prompt()
                return
            return

        # Detect Shift, Alt, or Windows keys and provide guidance
        if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            if t.phase in (4, 5):
                self.speech.say("That's Shift. Control is below Shift in the bottom left corner.", priority=True)
            else:
                self.speech.say("That's Shift. Not needed for this tutorial.", priority=True)
            return

        if event.key in (pygame.K_LALT, pygame.K_RALT):
            if t.phase in (4, 5):
                self.speech.say("That's Alt. Control is to the left of Alt in the bottom left corner.", priority=True)
            else:
                self.speech.say("That's Alt. Not needed for this tutorial.", priority=True)
            return

        if event.key in (pygame.K_LMETA, pygame.K_RMETA, pygame.K_LSUPER, pygame.K_RSUPER):
            if t.phase in (4, 5):
                self.speech.say("That's the Windows key. Control is to the left of the Windows key in the bottom left corner.", priority=True)
            else:
                self.speech.say("That's the Windows key. Not needed for this tutorial.", priority=True)
            return
        # Determine keyset based on phase
        keyset = tutorial_data.input_keyset_for_phase(t.phase)

        pressed_name = None
        for name, key in keyset:
            # Check both left and right control keys
            if name == "control" and (event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL):
                pressed_name = name
                break
            elif event.key == key:
                pressed_name = name
                break

        if pressed_name is None:
            if t.phase == 1:
                self.speech.say("Use Space bar")
            elif t.phase == 2:
                self.speech.say("Use the arrow keys")
            elif t.phase == 3:
                self.speech.say("Use Enter")
            elif t.phase == 4:
                self.speech.say("Use Control")
            else:
                self.speech.say("Use arrows, space, Enter, or Control")
            return

        t.total_attempts += 1
        t.phase_attempts += 1

        # Check if correct key was pressed (handle both left/right control)
        correct_key = False
        if t.required_name == "control" and (event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL):
            correct_key = True
        elif event.key == t.required_key:
            correct_key = True

        if correct_key:
            self.audio.beep_ok()
            self.trigger_flash((0, 80, 0), 0.12)
            t.total_correct += 1
            t.phase_correct += 1
            t.counts_done[t.required_name] += 1
            t.index += 1
            # Clear guidance on correct key
            t.guidance_message = ""
            t.hint_message = ""
            self.speech.say(random.choice(tutorial_data.ENCOURAGEMENT["correct"]))
            self.load_tutorial_prompt()
        else:
            self.audio.beep_bad()
            self.trigger_flash((100, 0, 0), 0.12)
            target = t.required_name
            pressed = pressed_name
            t.phase_mistakes += 1
            t.key_errors[target] += 1
            guidance = tutorial_data.RELATION.get((pressed, target), f"Try {tutorial_data.FRIENDLY[target]}")
            hint = tutorial_data.HINTS[target]
            # Store guidance for visual display
            t.guidance_message = f"{tutorial_data.FRIENDLY[pressed]} {guidance}"
            t.hint_message = hint
            self.speech.say(f"{tutorial_data.FRIENDLY[pressed]} {guidance} {hint}")

    # ==================== KEYBOARD EXPLORER ====================
    def start_keyboard_explorer(self):
        """Start keyboard explorer mode - pressure-free key exploration."""
        self.state.mode = "KEYBOARD_EXPLORER"
        self.keyboard_explorer_first_key = True  # Flag to skip the menu selection key
        self.speech.say(
            "Keyboard Explorer. Press any key to hear its name and location. No timing, no scoring, no pressure. Press Escape three times to return to the menu.",
            priority=True, protect_seconds=3.0
        )

    def handle_keyboard_explorer_input(self, event, mods):
        """Handle input in keyboard explorer mode."""
        # Escape returns to menu
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
            return

        # Skip the first Enter/Space keypress (it's from menu selection), then allow them
        if self.keyboard_explorer_first_key and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.keyboard_explorer_first_key = False
            return

        # After first key, allow all keys including Enter and Space
        self.keyboard_explorer_first_key = False

        # Get key name and description
        key_name = keyboard_explorer.get_key_name(event)
        description = keyboard_explorer.get_key_description(key_name, event=event)

        # Announce the key description
        self.speech.say(description, priority=True, protect_seconds=2.5)

        # Play a pleasant tone for feedback
        self.audio.beep_ok()

    # ==================== LESSON INTRO ====================
    def start_lesson(self, lesson_num=None):
        """Begin lesson - show intro screen first if lesson has key locations."""
        # Use provided lesson number or current lesson from settings
        if lesson_num is None:
            lesson_num = self.state.settings.current_lesson

        stage = max(0, min(lesson_num, len(lesson_manager.STAGE_LETTERS) - 1))
        self.state.settings.current_lesson = stage

        # Check if this lesson has an intro (key location descriptions)
        if stage in lesson_manager.KEY_LOCATIONS:
            self.show_lesson_intro(stage)
        else:
            self.begin_lesson_practice(stage)

    def show_lesson_intro(self, lesson_num):
        """Show lesson intro screen with key location and finding instructions."""
        lesson_intro_mode.show_lesson_intro(self, lesson_num)

    def repeat_lesson_intro(self):
        """Repeat the lesson intro information."""
        lesson_intro_mode.repeat_lesson_intro(self)

    def handle_lesson_intro_input(self, event, mods):
        """Handle key presses during lesson intro - looking for new keys."""
        lesson_intro_mode.handle_lesson_intro_input(self, event, mods)

    # ==================== LESSON (ADAPTIVE) ====================
    def begin_lesson_practice(self, lesson_num):
        """Begin the actual lesson practice after intro."""
        self.state.mode = "LESSON"

        stage = max(0, min(lesson_num, len(lesson_manager.STAGE_LETTERS) - 1))
        self.state.lesson = state_manager.LessonState(stage=stage)
        self.state.settings.current_lesson = stage

        # Use words from the start - we have content for all lessons now
        self.state.lesson.use_words = True

        self.build_lesson_batch()

        l = self.state.lesson
        target = l.batch_words[l.index]

        lesson_name = lesson_manager.LESSON_NAMES[stage]

        # Check if this is a special key lesson
        if l.batch_instructions:
            # Special key lesson - use the instruction
            instruction = l.batch_instructions[l.index]
            self.speech.say(
                f"Lesson practice. Control Space repeats. {instruction}",
                priority=True,
                protect_seconds=3.0,
            )
        else:
            # Regular lesson - build character-by-character description for first prompt
            speakable = self._make_speakable(target)

            self.speech.say(
                f"Lesson practice. Control Space repeats. Type {speakable}",
                priority=True,
                protect_seconds=3.0,
            )

    def build_lesson_batch(self):
        lesson_mode.build_lesson_batch(self)

    def lesson_prompt(self):
        lesson_mode.lesson_prompt(self)

    def next_lesson_item(self):
        lesson_mode.next_lesson_item(self)

    def extend_lesson_practice(self):
        lesson_mode.extend_lesson_practice(self)

    def check_and_inject_adaptive_content(self):
        lesson_mode.check_and_inject_adaptive_content(self)

    def calculate_lesson_stars(self, lesson_num: int, accuracy: float, wpm: float) -> int:
        return lesson_mode.calculate_lesson_stars(lesson_num, accuracy, wpm)

    def evaluate_lesson_performance(self):
        lesson_mode.evaluate_lesson_performance(self)
        return
        '''
        """Evaluate performance and decide next action - now with victory sound and results dialog!"""
        l = self.state.lesson
        l.end_time = time.time()

        # Play victory sound for completing the batch
        self.audio.play_victory()

        # Calculate statistics
        duration = l.end_time - l.start_time
        accuracy = l.tracker.overall_accuracy() * 100
        total_attempts = l.tracker.total_attempts
        total_correct = l.tracker.total_correct
        total_errors = total_attempts - total_correct
        wpm = l.tracker.calculate_wpm(duration)

        # Phase 1: Calculate star rating for this lesson
        stars = self.calculate_lesson_stars(l.stage, accuracy, wpm)

        # Update best scores for this lesson
        prev_stars = self.state.settings.lesson_stars.get(l.stage, 0)
        if stars > prev_stars:
            self.state.settings.lesson_stars[l.stage] = stars

        # Track best performance metrics
        prev_wpm = self.state.settings.lesson_best_wpm.get(l.stage, 0.0)
        if wpm > prev_wpm:
            self.state.settings.lesson_best_wpm[l.stage] = wpm

        prev_accuracy = self.state.settings.lesson_best_accuracy.get(l.stage, 0.0)
        if accuracy > prev_accuracy:
            self.state.settings.lesson_best_accuracy[l.stage] = accuracy

        # Update global statistics
        self.state.settings.total_lessons_completed += 1
        self.state.settings.total_practice_time += duration
        if wpm > self.state.settings.highest_wpm:
            self.state.settings.highest_wpm = wpm

        # Phase 1: Check for newly earned badges
        lesson_stats = {
            'accuracy': accuracy,
            'wpm': wpm,
            'duration': duration
        }
        new_badges = badge_manager.check_badges(self.state.settings, lesson_stats)

        # Add newly earned badges and queue for notification
        for badge_id in new_badges:
            self.state.settings.earned_badges.add(badge_id)
            self.state.settings.badge_notifications.append(badge_id)

        # Phase 2: Award XP for completing lesson
        xp_earned = xp_manager.XP_AWARDS["lesson"]
        xp_earned += total_correct * xp_manager.XP_AWARDS["keystroke"]

        # Bonus XP for perfect accuracy
        if accuracy >= 100:
            xp_earned += xp_manager.XP_AWARDS["perfect_accuracy"]

        # Bonus XP for new best WPM
        if wpm > prev_wpm and wpm >= 20:
            xp_earned += xp_manager.XP_AWARDS["new_best_wpm"]

        # Bonus XP for new best accuracy
        if accuracy > prev_accuracy:
            xp_earned += xp_manager.XP_AWARDS["new_best_accuracy"]

        # Award XP and check for level-up
        xp_result = xp_manager.award_xp(self.state.settings, xp_earned, f"Lesson {l.stage} completed")

        # Phase 2: Update quest progress
        quest_progress_data = {
            "lesson_num": l.stage,
            "accuracy": accuracy,
            "wpm": wpm,
            "duration": duration
        }
        newly_completed_quests = quest_manager.check_all_active_quests(self.state.settings, quest_progress_data)

        # Award XP for completed quests
        for quest_id in newly_completed_quests:
            quest = quest_manager.get_quest_info(quest_id)
            if quest:
                quest_xp_result = xp_manager.award_xp(self.state.settings, quest["xp_reward"], f"Quest: {quest['name']}")

        # Phase 2: Check daily challenge
        challenge = challenge_manager.get_today_challenge()
        if not self.state.settings.daily_challenge_completed:
            if challenge["type"] == "lesson_accuracy":
                progress = challenge_manager.check_challenge_progress("lesson_accuracy", challenge["target"], {"accuracy": accuracy})
                if progress["completed"]:
                    challenge_result = challenge_manager.complete_daily_challenge(self.state.settings)
                    challenge_xp_result = xp_manager.award_xp(self.state.settings, challenge_result["xp_earned"], "Daily Challenge")

        # Phase 2: Record session for dashboard
        session_data = {
            "type": "lesson",
            "lesson_num": l.stage,
            "wpm": wpm,
            "accuracy": accuracy,
            "duration": duration,
            "stars": stars,
            "xp_earned": xp_earned
        }
        dashboard_manager.record_session(self.state.settings, session_data)

        # Prepare key performance data for formatter
        key_perf_dict = None
        if l.tracker.key_performance:
            key_perf_dict = {}
            for key, perf in l.tracker.key_performance.items():
                key_perf_dict[key] = {
                    'recent_accuracy': perf.recent_accuracy(),
                    'correct': perf.correct,
                    'attempts': perf.attempts
                }

        # Determine next action and prepare unlock info
        unlocked_new = False
        unlocked_lesson_info = None
        should_advance = l.tracker.should_advance(
            lesson_num=l.stage,
            duration_seconds=duration,
            wpm_required_from_lesson=lesson_manager.WPM_REQUIRED_FROM_LESSON,
            min_wpm=lesson_manager.MIN_WPM
        )
        should_review = l.tracker.should_slow_down()
        needs_wpm = (l.stage >= lesson_manager.WPM_REQUIRED_FROM_LESSON and wpm < lesson_manager.MIN_WPM and accuracy >= 80)

        if should_advance:
            # Unlock next lesson
            next_lesson = min(l.stage + 1, len(lesson_manager.STAGE_LETTERS) - 1)
            if next_lesson not in self.state.settings.unlocked_lessons:
                self.state.settings.unlocked_lessons.add(next_lesson)
                unlocked_new = True
                next_name = lesson_manager.LESSON_NAMES[next_lesson] if next_lesson < len(lesson_manager.LESSON_NAMES) else f"Lesson {next_lesson}"
                new_keys = lesson_manager.STAGE_LETTERS[next_lesson] if next_lesson < len(lesson_manager.STAGE_LETTERS) else set()
                unlocked_lesson_info = {
                    'name': next_name,
                    'keys': new_keys
                }

            self.state.settings.current_lesson = next_lesson
            l.stage = next_lesson
            self.save_progress()

        elif should_review:
            l.review_mode = True

        # Format results using results_formatter
        results_text, action = results_formatter.ResultsFormatter.format_lesson_results(
            accuracy=accuracy,
            wpm=wpm,
            total_correct=total_correct,
            total_errors=total_errors,
            duration=duration,
            key_performance=key_perf_dict,
            unlocked_lesson=unlocked_lesson_info,
            should_advance=should_advance,
            should_review=should_review,
            needs_wpm=needs_wpm,
            min_wpm=lesson_manager.MIN_WPM,
            stars=stars,
            prev_stars=prev_stars
        )

        # Show results dialog (blocks until OK is pressed)
        self.show_results_dialog(results_text)

        # Play unlock sound if new lesson was unlocked
        if unlocked_new:
            self.audio.play_unlock()
            pygame.time.wait(500)  # Brief pause after unlock sound

        # Phase 1: Show badge notifications if any were earned
        self.show_badge_notifications()

        # Phase 2: Show level-up notification if leveled up
        self.show_level_up_notification(xp_result)

        # Phase 2: Show quest completion notifications
        self.show_quest_notifications()

        # After dialog closes, execute the action
        if action == "advance":
            next_lesson = self.state.settings.current_lesson
            next_name = lesson_manager.LESSON_NAMES[next_lesson] if next_lesson < len(lesson_manager.LESSON_NAMES) else f"Lesson {next_lesson}"
            if unlocked_new:
                self.speech.say(f"Starting {next_name}", priority=True, protect_seconds=2.0)
            pygame.time.wait(500)
            self.start_lesson(next_lesson)
        elif action == "review":
            self.state.mode = "RESULTS"
            self.state.results_text = "Press Space for focused review, Enter to try again, or Escape for menu."
            self.speech.say(self.state.results_text, priority=True, protect_seconds=3.0)
        else:
            self.state.mode = "RESULTS"
            self.state.results_text = "Press Space to continue, Enter to practice more, or Escape for menu."
            self.speech.say(self.state.results_text, priority=True, protect_seconds=3.0)
        '''

    def current_word(self):
        return self.state.lesson.batch_words[self.state.lesson.index]

    def handle_lesson_input(self, event, mods):
        lesson_mode.handle_lesson_input(self, event, mods)

    def process_lesson_typing(self, event):
        lesson_mode.process_lesson_typing(self, event)

    def provide_key_guidance(self, pressed, target_text):
        """Provide short, directional guidance based on spatial position."""
        l = self.state.lesson

        if not target_text:
            target_text = ""
        target_key = target_text[0] if target_text else ""

        # Get directional hint based on key positions
        hint = lesson_manager.get_directional_hint(pressed, target_key) if target_key else "Try again."
        speakable_target = self._make_speakable(target_text)

        # Store for visual display - short and helpful
        l.guidance_message = f"Type {speakable_target}"
        l.hint_message = hint

        # Say target and directional hint
        self.speech.say(f"Type {speakable_target}, {hint}", priority=True, protect_seconds=2.0)

    # ==================== SPEED TEST ====================
    def start_test(self):
        """Start speed test - ask for duration first."""
        test_modes.start_test(self)

    def handle_test_setup_input(self, event):
        """Handle duration input for speed test - user types any number."""
        test_modes.handle_test_setup_input(self, event)

    def begin_test_typing(self):
        """Start the actual typing test after duration is selected."""
        test_modes.begin_test_typing(self)

    def load_next_sentence(self):
        test_modes.load_next_sentence(self)

    def finish_test(self):
        test_modes.finish_test(self)

    def handle_test_input(self, event, mods):
        test_modes.handle_test_input(self, event, mods)

    def process_test_typing(self, event):
        test_modes.process_test_typing(self, event)

    def speak_test_remaining(self):
        test_modes.speak_test_remaining(self)

    # ==================== SENTENCE PRACTICE ====================
    def start_practice(self):
        """Open sentence practice setup."""
        test_modes.start_practice(self)

    def handle_practice_setup_input(self, event, mods):
        """Handle sentence practice setup mode input."""
        test_modes.handle_practice_setup_input(self, event, mods)

    def load_next_practice_sentence(self):
        """Load next sentence for practice mode."""
        test_modes.load_next_practice_sentence(self)

    def finish_practice(self):
        """Finish sentence practice and show results."""
        test_modes.finish_practice(self)

    def handle_practice_input(self, event, mods):
        """Handle input during sentence practice mode."""
        test_modes.handle_practice_input(self, event, mods)

    def process_practice_typing(self, event):
        """Process typing for sentence practice - same as speed test."""
        test_modes.process_practice_typing(self, event)

    def speak_practice_remaining(self):
        """Speak remaining text for sentence practice."""
        test_modes.speak_practice_remaining(self)

    # ==================== RESULTS ====================
    def handle_results_input(self, event, mods):
        if event.key == pygame.K_ESCAPE:
            self.state.mode = "MENU"
            self.say_menu()
        elif event.key == pygame.K_SPACE:
            if "Unlocked" in self.state.results_text:
                # New lesson unlocked - go to lesson menu
                self.save_progress()
                self.show_lesson_menu()
            elif "stage" in self.state.results_text.lower() or "continue" in self.state.results_text.lower():
                # Reset review mode if exiting it
                self.state.lesson.review_mode = False
                # Continue current lesson
                self.save_progress()
                self.start_lesson()
        elif event.key == pygame.K_RETURN:
            if "Speed Test" in self.state.results_text:
                self.start_test()
            elif "Sentence Practice" in self.state.results_text:
                self.start_practice()
            else:
                self.save_progress()
                self.start_lesson()

    # ==================== DRAWING ====================
    def trigger_flash(self, color: tuple, duration: float = 0.12) -> None:
        """Schedule a brief color overlay for visual keystroke feedback.

        Provides a visual equivalent of beep_ok (green) and beep_bad (red)
        for deaf or hard-of-hearing users. Safe to call every keystroke —
        the overlay lasts only ~120 ms and is drawn at low opacity.
        """
        self._flash_color = color
        self._flash_until = time.time() + duration

    def draw(self):
        self.screen.fill(BG)
        if self.state.mode == "MENU":
            self.draw_menu()
        elif self.state.mode == "KEYBOARD_EXPLORER":
            self.draw_keyboard_explorer()
        elif self.state.mode == "LESSON_MENU":
            self.draw_lesson_menu()
        elif self.state.mode == "OPTIONS":
            self.draw_options()
        elif self.state.mode == "LESSON_INTRO":
            self.draw_lesson_intro()
        elif self.state.mode == "TUTORIAL":
            self.draw_tutorial()
        elif self.state.mode == "LESSON":
            self.draw_lesson()
        elif self.state.mode == "TEST_SETUP":
            self.draw_test_setup()
        elif self.state.mode == "TEST":
            self.draw_test()
        elif self.state.mode == "PRACTICE_SETUP":
            self.draw_practice_setup()
        elif self.state.mode == "PRACTICE":
            self.draw_practice()
        elif self.state.mode == "RESULTS":
            self.draw_results()
        elif self.state.mode == "GAMES_MENU":
            self.draw_games_menu()
        elif self.state.mode == "SHOP":
            self.draw_shop()
        elif self.state.mode == "PET":
            self.draw_pet()
        elif self.state.mode == "LEARN_SOUNDS_MENU":
            self.draw_learn_sounds_menu()
        elif self.state.mode == "ABOUT":
            self.draw_about()
        elif self.state.mode == "GAME":
            self.draw_game()
        elif self.state.mode == "FREE_PRACTICE_READY":
            self.draw_free_practice_ready()
        elif self.state.mode == "FREE_PRACTICE":
            self.draw_lesson()  # Reuse lesson drawing

        # Escape press counter — shown while user is mid-sequence (visual complement to speech).
        if self._escape_remaining > 0:
            presses = self._escape_remaining
            noun = self._escape_noun
            msg = (
                f"Escape: {presses} more press{'es' if presses != 1 else ''} to {noun}"
            )
            esc_surf, _ = self.small_font.render(msg, ACCENT)
            self.screen.blit(esc_surf, (SCREEN_W // 2 - esc_surf.get_width() // 2, 6))

        # Render keystroke flash overlay last so it appears above all content.
        if self._flash_until > time.time():
            from ui.a11y import draw_keystroke_flash
            elapsed = self._flash_until - time.time()
            alpha = int(min(60, elapsed * 500))
            draw_keystroke_flash(self.screen, self._flash_color, alpha, SCREEN_W, SCREEN_H)

    def draw_menu(self):
        streak_text = ""
        if self.state.settings.current_streak > 0:
            streak_text = self.get_streak_announcement()

        draw_main_menu(
            screen=self.screen,
            title_font=self.title_font,
            small_font=self.small_font,
            menu_items=self.state.menu_items,
            current_index=self.main_menu.current_index,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            unlocked_count=len(self.state.settings.unlocked_lessons),
            total_count=len(lesson_manager.STAGE_LETTERS),
            streak_text=streak_text,
        )

    def draw_lesson_menu(self):
        """Draw the lesson selection menu."""
        draw_lesson_menu(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            unlocked_lessons=sorted(list(self.state.settings.unlocked_lessons)),
            lesson_names=lesson_manager.LESSON_NAMES,
            current_index=self.lesson_menu.current_index,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
        )

    def draw_games_menu(self):
        """Draw the games selection menu."""
        draw_games_menu(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            games=self.games,
            current_index=self.games_menu.current_index,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
        )

    def draw_learn_sounds_menu(self):
        draw_learn_sounds_menu(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            sound_items=self.sound_items,
            current_index=self.sounds_menu.current_index,
        )

    def draw_about(self):
        title_surf, _ = self.title_font.render("About", ACCENT)
        self.screen.blit(title_surf, (SCREEN_W // 2 - title_surf.get_width() // 2, 40))

        version_surf, _ = self.small_font.render(f"KeyQuest {__version__}", ACCENT)
        self.screen.blit(version_surf, (SCREEN_W // 2 - version_surf.get_width() // 2, 84))

        subtitle = "Web Friendly Help"
        subtitle_surf, _ = self.text_font.render(subtitle, FG)
        self.screen.blit(subtitle_surf, (SCREEN_W // 2 - subtitle_surf.get_width() // 2, 116))

        y = 180
        for idx, item in enumerate(self.about_items):
            selected = idx == self.about_menu.current_index
            prefix = "> " if selected else "  "
            text = f"{prefix}{item['display']}"
            color = HILITE if selected else FG
            surf, _ = self.text_font.render(text, color)
            self.screen.blit(surf, (80, y))
            y += 52

        hint, _ = self.small_font.render("Enter select; Escape back", ACCENT)
        self.screen.blit(hint, (80, SCREEN_H - 60))

    def draw_shop(self):
        """Draw the shop interface."""
        draw_shop(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            settings=self.state.settings,
            shop_view=self.shop_view,
            shop_categories=self.shop_categories,
            shop_category_index=self.shop_category_index,
            shop_item_index=self.shop_item_index,
        )

    def draw_pet(self):
        """Draw the pet interface."""
        draw_pet(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            settings=self.state.settings,
            pet_view=self.pet_view,
            pet_types=self.pet_types,
            pet_choose_index=self.pet_choose_index,
            pet_options=self.pet_options,
            pet_menu_index=self.pet_menu_index,
        )

    def draw_game(self):
        """Draw the active game."""
        if self.current_game:
            self.current_game.draw()

    def draw_options(self):
        """Draw the options menu."""
        options = [opt["get_text"]() for opt in self.options_menu.options]
        draw_options(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            options=options,
            current_index=self.options_menu.current_index,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
        )

    def draw_lesson_intro(self):
        intro = self.state.lesson_intro
        lesson_num = intro.lesson_num

        lesson_name = (
            lesson_manager.LESSON_NAMES[lesson_num]
            if lesson_num < len(lesson_manager.LESSON_NAMES)
            else f"Lesson {lesson_num}"
        )

        info = lesson_manager.KEY_LOCATIONS.get(lesson_num)

        needed_keys = sorted(list(intro.required_keys - intro.keys_found))
        keys_to_find_display = phonetics.format_needed_keys_for_display(needed_keys) if needed_keys else ""
        keys_found_display = ", ".join(sorted([k.upper() for k in intro.keys_found])) if intro.keys_found else ""

        draw_lesson_intro_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            lesson_num=lesson_num,
            lesson_name=lesson_name,
            lesson_info=info,
            keys_to_find_display=keys_to_find_display,
            keys_found_display=keys_found_display,
        )

    def _wrap_text(self, text, max_width):
        return wrap_text(self.small_font, text, max_width, FG)

    def draw_keyboard_explorer(self):
        draw_keyboard_explorer_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
        )

    def draw_tutorial(self):
        draw_tutorial_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            wrap_text=self._wrap_text,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            tutorial_state=self.state.tutorial,
            tutorial_data=tutorial_data,
        )

    def draw_lesson(self):
        l = self.state.lesson
        draw_lesson_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            wrap_text=self._wrap_text,
            lesson_state=l,
            target=self.current_word(),
            typed=l.typed,
        )

    def draw_free_practice_ready(self):
        draw_free_practice_ready_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            screen_w=SCREEN_W,
            fg=FG,
            hilite=HILITE,
            available_keys_count=len(self.state.free_practice.available_keys),
        )

    def draw_test_setup(self):
        """Draw the test duration selection screen."""
        draw_test_setup_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            duration_input=self.state.test.duration_input,
        )

    def draw_practice_setup(self):
        """Draw sentence practice setup screen."""
        draw_practice_setup_screen(
            screen=self.screen,
            title_font=self.title_font,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            fg=FG,
            accent=ACCENT,
            hilite=HILITE,
            view=self.practice_setup_view,
            menu_options=self.practice_setup_options,
            menu_index=self.practice_setup_index,
            topic_options=self.practice_topic_options,
            topic_index=self.practice_topic_index,
        )

    def draw_test(self):
        t = self.state.test
        if t.running and t.start_time > 0:
            elapsed = time.time() - t.start_time
            remaining = max(0, t.duration_seconds - elapsed)

            # Auto-end test when time expires
            if elapsed >= t.duration_seconds:
                self.finish_test()
                return
        else:
            remaining = t.duration_seconds

        draw_test_screen(
            screen=self.screen,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            fg=FG,
            accent=ACCENT,
            current_text=t.current,
            typed_text=t.typed,
            remaining_seconds=int(remaining),
        )

    def draw_practice(self):
        """Draw sentence practice screen."""
        t = self.state.test

        elapsed_seconds = (time.time() - t.start_time) if t.start_time > 0 else 0.0
        draw_practice_screen(
            screen=self.screen,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            fg=FG,
            accent=ACCENT,
            current_text=t.current,
            typed_text=t.typed,
            elapsed_seconds=elapsed_seconds,
            sentences_completed=t.sentences_completed,
        )

    def draw_results(self):
        draw_results_screen(
            screen=self.screen,
            text_font=self.text_font,
            small_font=self.small_font,
            screen_w=SCREEN_W,
            screen_h=SCREEN_H,
            fg=FG,
            accent=ACCENT,
            results_text=self.state.results_text,
        )


def main():
    print("KeyQuest main() starting...")
    try:
        print("Creating KeyQuestApp...")
        app = KeyQuestApp()
        print("Starting app.run()...")
        app.run()
        print("app.run() completed")
    except Exception as e:
        print(f"ERROR in main(): {e}")
        import traceback
        traceback.print_exc()
        error_logging.log_exception(e)
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()







