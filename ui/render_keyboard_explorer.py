from ui.a11y import draw_controls_hint


def draw_keyboard_explorer_screen(
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
):
    title_surf, _ = title_font.render("Keyboard Explorer", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 80))

    instructions = [
        "Press any key to hear its name and location",
        "No timing, no scoring, no pressure",
        "Explore the keyboard at your own pace",
    ]

    y = 200
    for instruction in instructions:
        inst_surf, _ = text_font.render(instruction, fg)
        screen.blit(inst_surf, (screen_w // 2 - inst_surf.get_width() // 2, y))
        y += 50

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Esc return to menu",
        screen_w=screen_w,
        y=screen_h - 60,
        accent=accent,
    )
