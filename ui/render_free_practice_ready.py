from ui.a11y import (
    draw_action_emphasis,
    draw_active_panel,
    draw_controls_hint,
    draw_focus_frame,
    get_visible_window,
)


def draw_free_practice_ready_screen(
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
    unlocked_lessons,
    lesson_names,
    current_index: int,
    available_keys_count: int,
):
    title_surf, _ = title_font.render("Free Practice Mode", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 40))

    subtitle = f"Choose an unlocked lesson. Keys available: {available_keys_count}"
    subtitle_surf, _ = small_font.render(subtitle, accent)
    screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, 90))

    visible_count = max(5, min(8, (screen_h - 240) // 44))
    start, end = get_visible_window(len(unlocked_lessons), current_index, visible_count)

    y = 145
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 120))

    for idx in range(start, end):
        lesson_num = unlocked_lessons[idx]
        lesson_name = lesson_names[lesson_num] if lesson_num < len(lesson_names) else f"Lesson {lesson_num}"
        line = f"Lesson {lesson_num}: {lesson_name}"
        selected = idx == current_index
        color = hilite if selected else fg
        item_text = f"> {line}" if selected else f"  {line}"
        line_surf, _ = text_font.render(item_text, color)
        line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, y))
        if selected:
            draw_active_panel(screen, line_rect, accent, fg)
            draw_focus_frame(screen, line_rect, hilite, accent)
            draw_action_emphasis(screen, line_rect, hilite)
        screen.blit(line_surf, line_rect)
        y += 44

    if end < len(unlocked_lessons):
        more_below_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_below_surf, (screen_w // 2 - more_below_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose lesson; Enter start; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
