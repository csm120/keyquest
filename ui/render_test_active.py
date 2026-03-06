import pygame

from ui.a11y import (
    draw_action_emphasis,
    draw_active_panel,
    draw_controls_hint,
    draw_focus_frame,
    draw_secondary_panel,
)
from ui.text_wrap import wrap_text


def _build_wrapped_lines(font, text: str, max_width: int, color, empty_fallback: str = "_"):
    display_text = text if text else empty_fallback
    lines = wrap_text(font, display_text, max_width, color)
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
        return pygame.Rect(screen_w // 2, start_y, 0, 0), y

    block_rect = rects[0].copy()
    for rect in rects[1:]:
        block_rect.union_ip(rect)
    return block_rect, y


def draw_test_screen(
    *,
    screen,
    text_font,
    small_font,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    current_text: str,
    typed_text: str,
    remaining_seconds: int,
    focus_assist: bool = False,
):
    max_text_width = screen_w - 140

    current_label_surf, _ = small_font.render("Type now:", accent)
    current_label_y = 130
    screen.blit(current_label_surf, (screen_w // 2 - current_label_surf.get_width() // 2, current_label_y))

    current_lines = _build_wrapped_lines(text_font, current_text, max_text_width, accent, empty_fallback="")
    cur_rect, next_y = _draw_centered_lines(
        screen, text_font, current_lines, accent, screen_w, current_label_y + 30
    )
    draw_active_panel(screen, cur_rect, accent, fg, strong=focus_assist)
    draw_focus_frame(screen, cur_rect, accent, fg)
    draw_action_emphasis(screen, cur_rect, accent, strong=focus_assist)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    typed_label_y = next_y + 14
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, typed_label_y))

    typed_lines = _build_wrapped_lines(text_font, typed_text, max_text_width, fg)
    typed_rect, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )
    draw_secondary_panel(screen, typed_rect, accent, fg, strong=focus_assist)
    _, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )

    time_msg = f"{int(remaining_seconds):>2}s left"
    time_surf, _ = small_font.render(time_msg, accent)
    time_y = typed_bottom_y + 14
    time_rect = time_surf.get_rect(topleft=(screen_w // 2 - time_surf.get_width() // 2, time_y))
    draw_secondary_panel(screen, time_rect, accent, fg, strong=focus_assist)
    screen.blit(time_surf, time_rect)

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Match capitals and punctuation exactly. Ctrl+Space repeat; Esc menu",
        screen_w=screen_w,
        y=min(screen_h - 50, time_y + 36),
        accent=accent,
    )


def draw_practice_screen(
    *,
    screen,
    text_font,
    small_font,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    current_text: str,
    typed_text: str,
    elapsed_seconds: float,
    sentences_completed: int,
    focus_assist: bool = False,
):
    max_text_width = screen_w - 140

    current_label_surf, _ = small_font.render("Type now:", accent)
    current_label_y = 120
    screen.blit(current_label_surf, (screen_w // 2 - current_label_surf.get_width() // 2, current_label_y))

    current_lines = _build_wrapped_lines(text_font, current_text, max_text_width, accent, empty_fallback="")
    cur_rect, next_y = _draw_centered_lines(
        screen, text_font, current_lines, accent, screen_w, current_label_y + 30
    )
    draw_active_panel(screen, cur_rect, accent, fg, strong=focus_assist)
    draw_focus_frame(screen, cur_rect, accent, fg)
    draw_action_emphasis(screen, cur_rect, accent, strong=focus_assist)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    typed_label_y = next_y + 14
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, typed_label_y))

    typed_lines = _build_wrapped_lines(text_font, typed_text, max_text_width, fg)
    typed_rect, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )
    draw_secondary_panel(screen, typed_rect, accent, fg, strong=focus_assist)
    _, typed_bottom_y = _draw_centered_lines(
        screen, text_font, typed_lines, fg, screen_w, typed_label_y + 28
    )

    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)
    time_msg = f"Time: {minutes}:{seconds:02d}"
    time_surf, _ = small_font.render(time_msg, accent)
    time_y = typed_bottom_y + 14
    time_rect = time_surf.get_rect(topleft=(screen_w // 2 - time_surf.get_width() // 2, time_y))
    screen.blit(time_surf, time_rect)

    sentence_msg = f"Sentences completed: {sentences_completed}"
    sentence_surf, _ = small_font.render(sentence_msg, accent)
    sentence_y = time_y + 34
    sentence_rect = sentence_surf.get_rect(topleft=(screen_w // 2 - sentence_surf.get_width() // 2, sentence_y))
    group_rect = time_rect.union(sentence_rect)
    draw_secondary_panel(screen, group_rect, accent, fg, strong=focus_assist)
    screen.blit(time_surf, time_rect)
    screen.blit(sentence_surf, sentence_rect)

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Match capitals and punctuation exactly. Ctrl+Space repeat; Esc x3 finish",
        screen_w=screen_w,
        y=min(screen_h - 50, sentence_y + 36),
        accent=accent,
    )
