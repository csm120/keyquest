from modules import currency_manager
from modules import shop_manager
from ui.a11y import draw_controls_hint, draw_focus_frame


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
    shop_view: str,
    shop_categories,
    shop_category_index: int,
    shop_item_index: int,
):
    title = "Shop"
    title_surf, _ = title_font.render(title, fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    balance = currency_manager.get_balance(settings)
    balance_text = f"Balance: {currency_manager.format_balance(balance)}"
    balance_surf, _ = text_font.render(balance_text, accent)
    screen.blit(balance_surf, (screen_w // 2 - balance_surf.get_width() // 2, 100))

    y = 150
    if shop_view == "categories":
        for idx, cat_id in enumerate(shop_categories):
            cat_info = shop_manager.SHOP_CATEGORIES[cat_id]
            selected = idx == shop_category_index
            color = hilite if selected else fg
            item_text = f"> {cat_info['name']}" if selected else f"  {cat_info['name']}"
            text_surf, _ = text_font.render(item_text, color)
            x = screen_w // 2 - text_surf.get_width() // 2
            item_rect = text_surf.get_rect(topleft=(x, y))
            screen.blit(text_surf, item_rect)
            if selected:
                draw_focus_frame(screen, item_rect, hilite, accent)
            y += 40

            if selected:
                desc_surf, _ = small_font.render(cat_info["description"], accent)
                screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                y += 30

            if y > screen_h - 150:
                break

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

    y = 200
    for idx, item_id in enumerate(items):
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
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
        y += 35

        if selected:
            desc_surf, _ = small_font.render(item["description"], accent)
            screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
            y += 25

        if y > screen_h - 100:
            break

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down browse; Enter purchase; Esc back",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
