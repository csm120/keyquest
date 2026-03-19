from __future__ import annotations

from ui.text_wrap import wrap_text
from ui.a11y import draw_action_emphasis, draw_active_panel, draw_controls_hint, draw_focus_frame


def draw_lesson_intro_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
    lesson_num: int,
    lesson_name: str,
    lesson_info: dict | None,
    current_intro_heading: str,
    current_intro_text: str,
    intro_index: int,
    intro_count: int,
    keys_to_find_display: str,
    keys_found_display: str,
):
    title = f"Lesson {lesson_num}: {lesson_name}"
    title_surf, _ = title_font.render(title, hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 40))

    if lesson_info:
        y = 120

        if current_intro_text:
            text_lines = wrap_text(small_font, current_intro_text, screen_w - 100, fg)
            block_top = y
            block_bottom = y
            widest = 0
            rendered = []
            for line in text_lines:
                line_surf, _ = small_font.render(line, fg)
                widest = max(widest, line_surf.get_width())
                rendered.append(line_surf)
            block_x = screen_w // 2 - widest // 2
            block_rect = None
            for line_surf in rendered:
                line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, block_bottom))
                block_rect = line_rect if block_rect is None else block_rect.union(line_rect)
                screen.blit(line_surf, line_rect)
                block_bottom += 30
            if block_rect is not None:
                draw_active_panel(screen, block_rect, accent, fg)
                for line_surf, line in zip(rendered, text_lines):
                    line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, block_top))
                    screen.blit(line_surf, line_rect)
                    block_top += 30
                draw_focus_frame(screen, block_rect, hilite, accent)
                draw_action_emphasis(screen, block_rect, hilite)
            y = block_bottom + 20

        if keys_to_find_display:
            find_label_surf, _ = text_font.render("Find these keys:", hilite)
            screen.blit(find_label_surf, (screen_w // 2 - find_label_surf.get_width() // 2, y))
            y += 35

            for line in wrap_text(small_font, keys_to_find_display, screen_w - 100, fg):
                keys_surf, _ = small_font.render(line, fg)
                keys_rect = keys_surf.get_rect(topleft=(screen_w // 2 - keys_surf.get_width() // 2, y))
                draw_active_panel(screen, keys_rect, accent, fg)
                screen.blit(keys_surf, keys_rect)
                draw_focus_frame(screen, keys_rect, hilite, accent)
                draw_action_emphasis(screen, keys_rect, hilite)
                y += 30

        if keys_found_display:
            found_surf, _ = small_font.render(f"Found: {keys_found_display}", accent)
            screen.blit(found_surf, (screen_w // 2 - found_surf.get_width() // 2, y))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down review; Ctrl+Space repeat; Press new keys to continue; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
