from ui.a11y import draw_controls_hint


def draw_free_practice_ready_screen(
    *,
    screen,
    title_font,
    text_font,
    screen_w: int,
    fg,
    hilite,
    available_keys_count: int,
):
    title_surf, _ = title_font.render("Free Practice Mode", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 100))

    y = 250
    instructions = [
        "Practice without affecting your progress!",
        "",
        f"Keys available: {available_keys_count}",
        "",
        "Press Enter to begin practice",
        "Press Escape to return to menu",
    ]

    for line in instructions:
        line_surf, _ = text_font.render(line, fg)
        screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
        y += 50

    draw_controls_hint(
        screen=screen,
        small_font=text_font,
        text="Enter begin practice; Esc return to menu",
        screen_w=screen_w,
        y=y + 20,
        accent=hilite,
    )
