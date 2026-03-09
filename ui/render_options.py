from ui.a11y import draw_action_emphasis, draw_active_panel, draw_controls_hint, draw_focus_frame, get_visible_window


def draw_options(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    options,
    current_index: int,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
):
    title = "Options"
    title_surf, _ = title_font.render(title, hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    visible_count = max(6, min(8, (screen_h - 220) // 50))
    start, end = get_visible_window(len(options), current_index, visible_count)

    y = 120
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 90))

    for idx in range(start, end):
        option = options[idx]
        selected = idx == current_index
        color = hilite if selected else fg
        option_text = f"> {option}" if selected else f"  {option}"
        text_surf, _ = text_font.render(option_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        option_rect = text_surf.get_rect(topleft=(x, y))
        if selected:
            draw_active_panel(screen, option_rect, accent, fg)
        screen.blit(text_surf, option_rect)
        if selected:
            draw_focus_frame(screen, option_rect, hilite, accent)
            draw_action_emphasis(screen, option_rect, hilite)
        y += 50

    if end < len(options):
        more_below_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_below_surf, (screen_w // 2 - more_below_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down navigate; Left/Right change; Esc save and exit",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
