from ui.a11y import draw_action_emphasis, draw_active_panel, draw_controls_hint, draw_focus_frame, get_visible_window
from ui.text_wrap import wrap_text


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
    title_surf, _ = title_font.render("Learn Sounds", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    visible_count = max(4, min(6, (screen_h - 250) // 70))
    start, end = get_visible_window(len(sound_items), current_index, visible_count)

    y = 120
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 90))

    for idx in range(start, end):
        sound_item = sound_items[idx]
        text = sound_item["name"]
        selected = idx == current_index
        color = hilite if selected else fg
        item_text = f"> {text}" if selected else f"  {text}"
        text_surf, _ = text_font.render(item_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        item_rect = text_surf.get_rect(topleft=(x, y))
        if selected:
            draw_active_panel(screen, item_rect, accent, fg)
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
            draw_action_emphasis(screen, item_rect, hilite)
        y += 40

        if selected:
            desc = sound_item.get("description", "")
            for line in wrap_text(small_font, desc, screen_w - 120, accent):
                desc_surf, _ = small_font.render(line, accent)
                screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                y += 22
            y += 6

    if end < len(sound_items):
        more_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter/Space play sound; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
