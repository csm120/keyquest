"""Speed test and sentence practice mode implementations.

These routines are extracted from `keyquest.pyw` to keep the main file focused on
app wiring + event loop, while preserving behavior.
"""

import random
import time

import pygame

from modules import error_logging
from modules import input_utils
from modules import results_formatter
from modules import sentences_manager
from modules import speech_format
from modules import state_manager


def _is_spanish_topic(topic: str) -> bool:
    """Return True when a practice topic represents Spanish content."""
    return topic.strip().lower().startswith("spanish")


def _get_random_topic_pool(topics):
    """Random-topic pool excludes Spanish, with safe fallback."""
    non_spanish = [topic for topic in topics if not _is_spanish_topic(topic)]
    return non_spanish if non_spanish else list(topics)


def start_test(app) -> None:
    """Start speed test - ask for duration first."""
    app.state.mode = "TEST_SETUP"
    app.state.test = state_manager.TestState(
        running=False,
        start_time=0.0,
        duration_seconds=60,  # Default
        duration_input="",
        remaining=[],
        current="",
        typed="",
        correct_chars=0,
        total_chars=0,
        sentences_completed=0,
        sentences_started=0,
    )
    app.speech.say(
        "Speed test. How many minutes? Type a number and press Enter.",
        priority=True,
        protect_seconds=3.0,
    )


def handle_test_setup_input(app, event) -> None:
    """Handle duration input for speed test - user types any number."""
    if event.key == pygame.K_ESCAPE:
        app.state.mode = "MENU"
        app.say_menu()
        return

    t = app.state.test

    if event.key == pygame.K_BACKSPACE:
        if t.duration_input:
            t.duration_input = t.duration_input[:-1]
            app.speech.say(t.duration_input if t.duration_input else "Empty", priority=True)
        return

    if event.key == pygame.K_RETURN:
        if t.duration_input and t.duration_input.isdigit():
            minutes = int(t.duration_input)
            if 1 <= minutes <= 60:
                t.duration_seconds = minutes * 60
                begin_test_typing(app)
            else:
                app.speech.say("Please enter a number between 1 and 60 minutes", priority=True)
        else:
            app.speech.say("Please enter a valid number", priority=True)
        return

    if event.unicode and event.unicode.isdigit():
        t.duration_input += event.unicode
        app.speech.say(event.unicode, priority=True)


def begin_test_typing(app) -> None:
    """Start the actual typing test after duration is selected."""
    app.state.mode = "TEST"
    t = app.state.test
    t.remaining = random.sample(app.speed_test_sentences, k=len(app.speed_test_sentences))
    minutes = t.duration_seconds // 60
    plural = "minute" if minutes == 1 else "minutes"
    app.speech.say(
        f"Speed test. {minutes} {plural}. Control Space repeats the remaining text.",
        priority=True,
        protect_seconds=3.0,
    )
    load_next_sentence(app)


def load_next_sentence(app) -> None:
    if not app.state.test.remaining:
        finish_test(app)
        return
    app.state.test.current = app.state.test.remaining.pop(0)
    app.state.test.typed = ""
    app.state.test.sentences_started += 1
    app.speech.say(app.state.test.current, priority=True, protect_seconds=2.0)


def finish_test(app) -> None:
    app.state.test.running = False
    t = app.state.test
    prev_highest_wpm = app.state.settings.highest_wpm

    acc = 0.0
    if t.total_chars:
        acc = (t.correct_chars / t.total_chars) * 100.0

    if t.start_time > 0.0:
        elapsed = max(1e-3, time.time() - t.start_time)
    else:
        elapsed = t.duration_seconds

    words_typed = t.correct_chars / 5.0
    minutes = elapsed / 60.0
    wpm = words_typed / minutes if minutes > 0 else 0.0
    gross_words_typed = t.total_chars / 5.0
    gross_wpm = gross_words_typed / minutes if minutes > 0 else 0.0

    time_minutes = elapsed / 60.0

    app.audio.play_victory()

    errors = t.total_chars - t.correct_chars
    partial_sentences = t.sentences_started - t.sentences_completed

    results_for_dialog = results_formatter.ResultsFormatter.format_speed_test_results(
        wpm=wpm,
        gross_wpm=gross_wpm,
        accuracy=acc,
        time_minutes=time_minutes,
        sentences_completed=t.sentences_completed,
        partial_sentences=partial_sentences,
        words_typed=words_typed,
        correct_chars=t.correct_chars,
        errors=errors,
        total_chars=t.total_chars,
    )

    try:
        pygame.scrap.init()
        pygame.scrap.put(pygame.SCRAP_TEXT, results_for_dialog.encode("utf-8"))
    except Exception as e:
        error_logging.log_exception(e)

    app.show_results_dialog(results_for_dialog)

    if wpm > app.state.settings.highest_wpm:
        app.state.settings.highest_wpm = wpm

    if hasattr(app, "apply_pet_session_progress"):
        app.apply_pet_session_progress(
            recent_performance={
                "new_best_wpm": wpm > prev_highest_wpm,
                "new_best_accuracy": False,
                "accuracy": acc,
                "session_duration": time_minutes,
                "streak_broken": False,
            },
            xp_amount=max(8, int(words_typed) + int(t.sentences_completed * 2)),
        )

    app.save_progress()

    app.state.mode = "MENU"
    app.speech.say(
        f"Speed test complete! Corrected words per minute {wpm:.1f}. Total words per minute {gross_wpm:.1f}. Accuracy {acc:.1f} percent.",
        priority=True,
        protect_seconds=3.0,
    )
    app.say_menu()


def handle_test_input(app, event, mods: int) -> None:
    if event.key == pygame.K_ESCAPE:
        app.state.mode = "MENU"
        app.say_menu()
    elif event.key == pygame.K_SPACE and input_utils.mod_ctrl(mods):
        speak_test_remaining(app)
    else:
        process_test_typing(app, event)


def process_test_typing(app, event) -> None:
    ch = None
    if event.unicode and event.unicode.isprintable():
        ch = event.unicode
    elif event.key == pygame.K_BACKSPACE:
        _record_typing_error(app, app.state.test)
        return
    else:
        return

    if ch is not None:
        t = app.state.test
        if not t.running:
            t.start_time = time.time()
            t.running = True
        pos = len(t.typed)

        if pos < len(t.current) and ch == t.current[pos]:
            t.typed += ch
            t.correct_chars += 1
            t.total_chars += 1

            if t.typed == t.current:
                app.audio.play_success()
                t.sentences_completed += 1
                load_next_sentence(app)
        else:
            _record_typing_error(app, t)


def speak_test_remaining(app) -> None:
    current = app.state.test.current
    typed = app.state.test.typed
    remaining = current[len(typed) :] if current.startswith(typed) else current
    app.speech.say(
        speech_format.build_remaining_text_feedback(remaining),
        priority=True,
        protect_seconds=2.0,
    )


def start_practice(app) -> None:
    """Show sentence practice setup with random/select topic options."""
    app.state.mode = "PRACTICE_SETUP"
    app.practice_topic_options = sentences_manager.get_sentence_topics_from_folder()
    if not app.practice_topic_options:
        app.practice_topic_options = sentences_manager.get_practice_topics()
    app.practice_setup_options = ["Random Topic", "Choose Topic"]
    app.practice_setup_index = 0
    app.practice_topic_index = 0
    app.practice_setup_view = "menu"
    app.speech.say(
        "Sentence practice setup. Random Topic. Use Up and Down arrows. Press Enter to select. Escape returns to menu.",
        priority=True,
        protect_seconds=3.0,
    )


def handle_practice_setup_input(app, event, mods: int) -> None:
    """Handle sentence practice setup input."""
    if app.practice_setup_view == "menu":
        if event.key == pygame.K_ESCAPE:
            app.state.mode = "MENU"
            app.say_menu()
            return
        if event.key == pygame.K_UP:
            app.practice_setup_index = (app.practice_setup_index - 1) % len(app.practice_setup_options)
            app.speech.say(app.practice_setup_options[app.practice_setup_index])
            return
        if event.key == pygame.K_DOWN:
            app.practice_setup_index = (app.practice_setup_index + 1) % len(app.practice_setup_options)
            app.speech.say(app.practice_setup_options[app.practice_setup_index])
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            choice = app.practice_setup_options[app.practice_setup_index]
            if choice == "Random Topic":
                pool = _get_random_topic_pool(app.practice_topic_options)
                topic = random.choice(pool)
                _begin_practice_session(app, topic)
            else:
                app.practice_setup_view = "topics"
                app.practice_topic_index = 0
                current = app.practice_topic_options[app.practice_topic_index]
                app.speech.say(
                    f"Choose topic. {current}. Use Up and Down arrows. Press Enter to start. Escape returns.",
                    priority=True,
                    protect_seconds=3.0,
                )
            return
        return

    if event.key == pygame.K_ESCAPE:
        app.practice_setup_view = "menu"
        app.speech.say(app.practice_setup_options[app.practice_setup_index], priority=True)
        return
    if event.key == pygame.K_UP:
        app.practice_topic_index = (app.practice_topic_index - 1) % len(app.practice_topic_options)
        app.speech.say(app.practice_topic_options[app.practice_topic_index])
        return
    if event.key == pygame.K_DOWN:
        app.practice_topic_index = (app.practice_topic_index + 1) % len(app.practice_topic_options)
        app.speech.say(app.practice_topic_options[app.practice_topic_index])
        return
    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
        topic = app.practice_topic_options[app.practice_topic_index]
        _begin_practice_session(app, topic)


def _begin_practice_session(app, topic: str) -> None:
    """Start sentence practice mode - type sentences until pressing Escape 3 times."""
    app.state.settings.sentence_language = topic
    app.practice_sentences = sentences_manager.load_practice_sentences(topic)
    app.state.mode = "PRACTICE"
    app.state.test = state_manager.TestState(
        running=True,
        start_time=time.time(),
        duration_seconds=0,  # No time limit
        duration_input="",
        remaining=[],
        current="",
        typed="",
        correct_chars=0,
        total_chars=0,
        sentences_completed=0,
        sentences_started=0,
    )

    if app.practice_sentences:
        app.state.test.remaining = random.sample(
            app.practice_sentences,
            k=min(len(app.practice_sentences), 500),
        )
    else:
        app.state.test.remaining = random.sample(app.speed_test_sentences, k=len(app.speed_test_sentences))

    app.speech.say(
        f"Sentence practice. Topic {topic}. Control Space repeats. Escape, press 3 times to finish.",
        priority=True,
        protect_seconds=3.0,
    )
    load_next_practice_sentence(app)


def load_next_practice_sentence(app) -> None:
    """Load next sentence for practice mode."""
    if not app.state.test.remaining:
        if app.practice_sentences:
            app.state.test.remaining = random.sample(
                app.practice_sentences,
                k=min(len(app.practice_sentences), 500),
            )
        else:
            app.state.test.remaining = random.sample(app.speed_test_sentences, k=len(app.speed_test_sentences))

    app.state.test.current = app.state.test.remaining.pop(0)
    app.state.test.typed = ""
    app.state.test.sentences_started += 1
    app.speech.say(app.state.test.current, priority=True, protect_seconds=2.0)


def finish_practice(app) -> None:
    """Finish sentence practice and show results."""
    app.state.test.running = False
    t = app.state.test
    prev_highest_wpm = app.state.settings.highest_wpm

    acc = 0.0
    if t.total_chars:
        acc = (t.correct_chars / t.total_chars) * 100.0

    if t.start_time > 0.0:
        elapsed = max(1e-3, time.time() - t.start_time)
    else:
        elapsed = 1.0

    words_typed = t.correct_chars / 5.0
    minutes = elapsed / 60.0
    wpm = words_typed / minutes if minutes > 0 else 0.0
    gross_words_typed = t.total_chars / 5.0
    gross_wpm = gross_words_typed / minutes if minutes > 0 else 0.0
    time_minutes = elapsed / 60.0

    app.audio.play_victory()

    errors = t.total_chars - t.correct_chars
    partial_sentences = t.sentences_started - t.sentences_completed

    results_for_dialog = results_formatter.ResultsFormatter.format_sentence_practice_results(
        wpm=wpm,
        gross_wpm=gross_wpm,
        accuracy=acc,
        time_minutes=time_minutes,
        sentences_completed=t.sentences_completed,
        partial_sentences=partial_sentences,
        words_typed=words_typed,
        correct_chars=t.correct_chars,
        errors=errors,
        total_chars=t.total_chars,
    )

    try:
        pygame.scrap.init()
        pygame.scrap.put(pygame.SCRAP_TEXT, results_for_dialog.encode("utf-8"))
    except Exception as e:
        error_logging.log_exception(e)

    app.show_results_dialog(results_for_dialog)

    if wpm > app.state.settings.highest_wpm:
        app.state.settings.highest_wpm = wpm

    if hasattr(app, "apply_pet_session_progress"):
        app.apply_pet_session_progress(
            recent_performance={
                "new_best_wpm": wpm > prev_highest_wpm,
                "new_best_accuracy": False,
                "accuracy": acc,
                "session_duration": time_minutes,
                "streak_broken": False,
            },
            xp_amount=max(8, int(words_typed) + int(t.sentences_completed * 2)),
        )

    app.save_progress()

    app.state.mode = "MENU"
    app.speech.say(
        f"Sentence practice complete! Corrected words per minute {wpm:.1f}. Total words per minute {gross_wpm:.1f}. Accuracy {acc:.1f} percent.",
        priority=True,
        protect_seconds=3.0,
    )
    app.say_menu()


def handle_practice_input(app, event, mods: int) -> None:
    """Handle input during sentence practice mode."""
    if event.key == pygame.K_SPACE and input_utils.mod_ctrl(mods):
        speak_practice_remaining(app)
        return

    process_practice_typing(app, event)


def process_practice_typing(app, event) -> None:
    """Process typing for sentence practice - same as speed test."""
    ch = None
    if event.unicode and event.unicode.isprintable():
        ch = event.unicode
    elif event.key == pygame.K_BACKSPACE:
        _record_typing_error(app, app.state.test)
        return
    if not ch:
        return

    t = app.state.test
    pos = len(t.typed)

    if pos < len(t.current) and ch == t.current[pos]:
        t.typed += ch
        t.correct_chars += 1
        t.total_chars += 1

        if t.typed == t.current:
            app.audio.play_success()
            t.sentences_completed += 1
            load_next_practice_sentence(app)
    else:
        _record_typing_error(app, t)


def speak_practice_remaining(app) -> None:
    """Speak remaining text for sentence practice."""
    current = app.state.test.current
    typed = app.state.test.typed
    remaining = current[len(typed) :] if current.startswith(typed) else current
    app.speech.say(
        speech_format.build_remaining_text_feedback(remaining),
        priority=True,
        protect_seconds=2.0,
    )


def _record_typing_error(app, test_state) -> None:
    """Handle a typing error without modifying already typed text."""
    pos = len(test_state.typed)
    remaining = test_state.current[pos:]
    app.audio.beep_bad()
    app.speech.say(
        speech_format.build_remaining_text_feedback(remaining),
        priority=True,
        protect_seconds=1.5,
    )
    test_state.total_chars += 1
