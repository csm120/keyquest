from modules import lesson_manager
from ui.a11y import (
    draw_action_emphasis,
    draw_active_panel,
    draw_controls_hint,
    draw_focus_frame,
    draw_secondary_panel,
)
from ui.text_wrap import wrap_text as wrap_text_for_font


def _build_wrapped_lines(font, text: str, max_width: int, color, empty_fallback: str = "_"):
    display_text = text if text else empty_fallback
    lines = wrap_text_for_font(font, display_text, max_width, color)
    return lines or [display_text]


def _draw_centered_lines(screen, font, lines, color, screen_w: int, start_y: int, gap: int = 8):
    rects = []
    y = start_y

    for line in lines:
        surf, _ = font.render(line, color)
        rect = surf.get_rect(topleft=(screen_w // 2 - surf.get_width() // 2, y))
        screen.blit(surf, rect)
        rects.append(rect)
        y += surf.get_height() + gap

    if not rects:
        import pygame
        return pygame.Rect(screen_w // 2, start_y, 0, 0), y

    block_rect = rects[0].copy()
    for rect in rects[1:]:
        block_rect.union_ip(rect)
    return block_rect, y


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
    focus_assist: bool = False,
):
    max_text_width = screen_w - 140

    target_label_surf, _ = text_font.render("Type now:", accent)
    target_label_y = 95
    screen.blit(target_label_surf, (screen_w // 2 - target_label_surf.get_width() // 2, target_label_y))

    target_lines = _build_wrapped_lines(title_font, target, max_text_width, accent, empty_fallback="")
    target_rect, next_y = _draw_centered_lines(
        screen, title_font, target_lines, accent, screen_w, target_label_y + 32
    )
    draw_active_panel(screen, target_rect, accent, fg, strong=focus_assist)
    draw_focus_frame(screen, target_rect, hilite, accent)
    draw_action_emphasis(screen, target_rect, hilite, strong=focus_assist)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    typed_label_y = next_y + 16
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, typed_label_y))

    typed_lines = _build_wrapped_lines(text_font, typed, max_text_width, fg)
    typed_rect, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )
    draw_secondary_panel(screen, typed_rect, accent, fg, strong=focus_assist)
    _, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )

    y = typed_bottom_y + 12
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
        info_rect = info_surf.get_rect(topleft=(screen_w // 2 - info_surf.get_width() // 2, y))
        y += 30

        acc = lesson_state.tracker.overall_accuracy() * 100
        acc_text = f"Accuracy: {acc:.0f}%"
        acc_surf, _ = small_font.render(acc_text, accent)
        acc_rect = acc_surf.get_rect(topleft=(screen_w // 2 - acc_surf.get_width() // 2, y))
        draw_secondary_panel(screen, info_rect.union(acc_rect), accent, fg, strong=focus_assist)
        screen.blit(info_surf, info_rect)
        screen.blit(acc_surf, acc_rect)
        y += 50

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Ctrl+Space repeat prompt; Esc menu",
        screen_w=screen_w,
        y=y,
        accent=accent,
    )
