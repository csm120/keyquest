from ui.a11y import draw_controls_hint, draw_focus_frame


def draw_learn_sounds_menu(
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
    sound_items: list,
    current_index: int,
):
    title_surf, _ = title_font.render("Learn Sounds", fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    y = 120
    for idx, sound_item in enumerate(sound_items):
        text = sound_item["name"]
        selected = idx == current_index
        color = hilite if selected else fg
        item_text = f"> {text}" if selected else f"  {text}"
        text_surf, _ = text_font.render(item_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        item_rect = text_surf.get_rect(topleft=(x, y))
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
        y += 40

        if selected:
            desc = sound_item.get("description", "")
            desc_surf, _ = small_font.render(desc, accent)
            screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
            y += 30

        if y > screen_h - 150:
            break

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter/Space play sound; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
