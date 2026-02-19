import pygame

from modules import input_utils
from modules import lesson_manager
from modules import phonetics
from modules import state_manager


def show_lesson_intro(app, lesson_num: int) -> None:
    """Show lesson intro screen with key location and finding instructions."""
    app.state.mode = "LESSON_INTRO"
    intro_info = lesson_manager.KEY_LOCATIONS[lesson_num]

    required_keys_str = intro_info["keys"]
    app.state.lesson_intro = state_manager.LessonIntroState(
        lesson_num=lesson_num,
        required_keys=set(required_keys_str.lower()),
        keys_found=set(),
    )

    repeat_lesson_intro(app)


def repeat_lesson_intro(app) -> None:
    """Repeat the lesson intro information."""
    intro = app.state.lesson_intro
    lesson_num = intro.lesson_num
    intro_info = lesson_manager.KEY_LOCATIONS[lesson_num]

    lesson_name = lesson_manager.LESSON_NAMES[lesson_num]
    desc = intro_info["description"]
    location = intro_info["location"]
    finding = intro_info["finding"]

    needed_keys = sorted(list(intro.required_keys - intro.keys_found))
    if needed_keys:
        keys_str = phonetics.format_needed_keys_for_speech(needed_keys)
        app.speech.say(
            f"Lesson {lesson_num}, {lesson_name}. {desc} {location} {finding} Find and press these keys, {keys_str}.",
            priority=True,
            protect_seconds=5.0,
        )
    else:
        app.speech.say("All keys found! Press them to continue.", priority=True)


def handle_lesson_intro_input(app, event, mods: int) -> None:
    """Handle key presses during lesson intro - looking for new keys."""
    if event.key == pygame.K_ESCAPE:
        app.state.mode = "MENU"
        app.say_menu()
        return

    if event.key == pygame.K_SPACE and input_utils.mod_ctrl(mods):
        repeat_lesson_intro(app)
        return

    if event.unicode and event.unicode.isprintable():
        pressed = event.unicode.lower()
        intro = app.state.lesson_intro

        if pressed in intro.required_keys and pressed not in intro.keys_found:
            intro.keys_found.add(pressed)
            app.audio.beep_ok()

            remaining = len(intro.required_keys) - len(intro.keys_found)
            if remaining > 0:
                app.speech.say(f"Found {pressed.upper()}! {remaining} more to go.", priority=True)
            else:
                app.speech.say(f"Found {pressed.upper()}!")

            if intro.keys_found == intro.required_keys:
                app.speech.say("All keys found! Starting lesson.")
                app.begin_lesson_practice(intro.lesson_num)

