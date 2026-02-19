from modules import lesson_manager
from ui.a11y import draw_controls_hint, draw_focus_frame


def draw_lesson_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    screen_w: int,
    fg,
    accent,
    hilite,
    wrap_text,
    lesson_state,
    target: str,
    typed: str,
):
    target_label_surf, _ = text_font.render("Type now:", accent)
    screen.blit(target_label_surf, (screen_w // 2 - target_label_surf.get_width() // 2, 120))

    target_surf, _ = title_font.render(target, accent)
    target_rect = target_surf.get_rect(topleft=(screen_w // 2 - target_surf.get_width() // 2, 155))
    screen.blit(target_surf, target_rect)
    draw_focus_frame(screen, target_rect, hilite, accent)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, 225))

    typed_display = typed if typed else "_"
    typed_surf, _ = text_font.render(typed_display, fg)
    typed_rect = typed_surf.get_rect(topleft=(screen_w // 2 - typed_surf.get_width() // 2, 250))
    screen.blit(typed_surf, typed_rect)

    y = 280
    if lesson_state.show_guidance and lesson_state.guidance_message:
        guidance_lines = wrap_text(lesson_state.guidance_message, screen_w - 80)
        for line in guidance_lines:
            guide_surf, _ = text_font.render(line, hilite)
            screen.blit(guide_surf, (screen_w // 2 - guide_surf.get_width() // 2, y))
            y += 35

        if lesson_state.hint_message:
            y += 5
            hint_lines = wrap_text(lesson_state.hint_message, screen_w - 80)
            for line in hint_lines:
                hint_surf, _ = small_font.render(line, accent)
                screen.blit(hint_surf, (screen_w // 2 - hint_surf.get_width() // 2, y))
                y += 28

        y += 20
    else:
        stage = lesson_state.stage
        current_keys = set().union(*lesson_manager.STAGE_LETTERS[: stage + 1])
        info = f"Lesson {stage}: {', '.join(sorted(current_keys))}"
        info_surf, _ = small_font.render(info, accent)
        screen.blit(info_surf, (screen_w // 2 - info_surf.get_width() // 2, y))
        y += 30

        acc = lesson_state.tracker.overall_accuracy() * 100
        acc_text = f"Accuracy: {acc:.0f}%"
        acc_surf, _ = small_font.render(acc_text, accent)
        screen.blit(acc_surf, (screen_w // 2 - acc_surf.get_width() // 2, y))
        y += 50

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Ctrl+Space repeat prompt; Esc menu",
        screen_w=screen_w,
        y=y,
        accent=accent,
    )
