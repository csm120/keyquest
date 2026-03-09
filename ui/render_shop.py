from modules import currency_manager
from modules import shop_manager
from ui.a11y import draw_action_emphasis, draw_active_panel, draw_controls_hint, draw_focus_frame, get_visible_window
from ui.text_wrap import wrap_text


def draw_shop(
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
    settings,
    shop_title: str,
    shop_view: str,
    shop_categories,
    shop_category_index: int,
    shop_item_index: int,
):
    title_surf, _ = title_font.render(shop_title, hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    balance = currency_manager.get_balance(settings)
    balance_text = f"Balance: {currency_manager.format_balance(balance)}"
    balance_surf, _ = text_font.render(balance_text, accent)
    screen.blit(balance_surf, (screen_w // 2 - balance_surf.get_width() // 2, 100))

    y = 150
    if shop_view == "categories":
        visible_count = max(4, min(6, (screen_h - 260) // 70))
        start, end = get_visible_window(len(shop_categories), shop_category_index, visible_count)
        if start > 0:
            more_above_surf, _ = small_font.render("^  more above  ^", accent)
            screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 126))

        for idx in range(start, end):
            cat_id = shop_categories[idx]
            cat_info = shop_manager.SHOP_CATEGORIES[cat_id]
            selected = idx == shop_category_index
            color = hilite if selected else fg
            item_text = f"> {cat_info['name']}" if selected else f"  {cat_info['name']}"
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
                for line in wrap_text(small_font, cat_info["description"], screen_w - 120, accent):
                    desc_surf, _ = small_font.render(line, accent)
                    screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                    y += 24
                y += 6

        if end < len(shop_categories):
            more_surf, _ = small_font.render("v  more below  v", accent)
            screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

        draw_controls_hint(
            screen=screen,
            small_font=small_font,
            text="Up/Down browse; Enter select category; Esc menu",
            screen_w=screen_w,
            y=screen_h - 50,
            accent=accent,
        )
        return

    cat_id = shop_categories[shop_category_index]
    cat_info = shop_manager.SHOP_CATEGORIES[cat_id]
    items = shop_manager.get_category_items(cat_id)

    subtitle_surf, _ = text_font.render(cat_info["name"], accent)
    screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, 150))

    visible_count = max(4, min(6, (screen_h - 300) // 55))
    start, end = get_visible_window(len(items), shop_item_index, visible_count)
    y = 200
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 176))

    for idx in range(start, end):
        item_id = items[idx]
        item = shop_manager.get_item_info(item_id)
        if not item:
            continue

        owned = shop_manager.is_owned(settings, item_id)
        quantity = shop_manager.get_inventory_count(settings, item_id)
        display_text = shop_manager.format_item_display(item_id, owned, quantity)

        selected = idx == shop_item_index
        color = hilite if selected else fg
        item_text = f"> {display_text}" if selected else f"  {display_text}"
        text_surf, _ = small_font.render(item_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        item_rect = text_surf.get_rect(topleft=(x, y))
        if selected:
            draw_active_panel(screen, item_rect, accent, fg)
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
            draw_action_emphasis(screen, item_rect, hilite)
        y += 35

        if selected:
            for line in wrap_text(small_font, item["description"], screen_w - 120, accent):
                desc_surf, _ = small_font.render(line, accent)
                screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                y += 22
            y += 4

    if end < len(items):
        more_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down browse; Enter purchase; Esc back",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
