from ui.a11y import draw_controls_hint, draw_focus_frame


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
    title_surf, _ = title_font.render(title, fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    y = 120
    for idx, option in enumerate(options):
        selected = idx == current_index
        color = hilite if selected else fg
        option_text = f"> {option}" if selected else f"  {option}"
        text_surf, _ = text_font.render(option_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        option_rect = text_surf.get_rect(topleft=(x, y))
        screen.blit(text_surf, option_rect)
        if selected:
            draw_focus_frame(screen, option_rect, hilite, accent)
        y += 50

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down navigate; Left/Right change; Esc save and exit",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
