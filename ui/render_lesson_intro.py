from __future__ import annotations

from ui.text_wrap import wrap_text
from ui.a11y import draw_controls_hint, draw_focus_frame


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
    keys_to_find_display: str,
    keys_found_display: str,
):
    title = f"Lesson {lesson_num}: {lesson_name}"
    title_surf, _ = title_font.render(title, fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 40))

    if lesson_info:
        y = 120

        desc_surf, _ = text_font.render(lesson_info.get("description", ""), accent)
        screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
        y += 50

        for line in wrap_text(small_font, lesson_info.get("location", ""), screen_w - 100, fg):
            line_surf, _ = small_font.render(line, fg)
            screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
            y += 30

        y += 10

        for line in wrap_text(small_font, lesson_info.get("finding", ""), screen_w - 100, fg):
            line_surf, _ = small_font.render(line, fg)
            screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
            y += 30

        y += 20

        if keys_to_find_display:
            find_label_surf, _ = text_font.render("Find these keys:", hilite)
            screen.blit(find_label_surf, (screen_w // 2 - find_label_surf.get_width() // 2, y))
            y += 35

            for line in wrap_text(small_font, keys_to_find_display, screen_w - 100, fg):
                keys_surf, _ = small_font.render(line, fg)
                keys_rect = keys_surf.get_rect(topleft=(screen_w // 2 - keys_surf.get_width() // 2, y))
                screen.blit(keys_surf, keys_rect)
                draw_focus_frame(screen, keys_rect, hilite, accent)
                y += 30

        if keys_found_display:
            found_surf, _ = small_font.render(f"Found: {keys_found_display}", accent)
            screen.blit(found_surf, (screen_w // 2 - found_surf.get_width() // 2, y))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Press new keys to continue; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
