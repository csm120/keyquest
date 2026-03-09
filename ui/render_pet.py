from modules import pet_manager
from modules import shop_manager
from ui.a11y import draw_action_emphasis, draw_active_panel, draw_controls_hint, draw_focus_frame, get_visible_window
from ui.pet_visuals import draw_pet_avatar
from ui.text_wrap import wrap_text


def draw_pet(
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
    pet_view: str,
    pet_types,
    pet_choose_index: int,
    pet_options,
    pet_menu_index: int,
):
    title = "Pets"
    title_surf, _ = title_font.render(title, hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))
    is_dark_fg = sum(fg) > 380
    panel_color = (22, 22, 22) if is_dark_fg else (238, 238, 238)
    owned_items = getattr(settings, "owned_items", set())
    item_state = {
        "hat": "pet_accessory_hat" in owned_items,
        "bowtie": "pet_accessory_bowtie" in owned_items,
        "wings": "pet_accessory_wings" in owned_items,
        "ball": "pet_toy_ball" in owned_items,
        "laser": "pet_toy_laser" in owned_items,
        "food_basic": shop_manager.get_inventory_count(settings, "pet_food_basic"),
        "food_premium": shop_manager.get_inventory_count(settings, "pet_food_premium"),
    }
    equipped_parts = []
    if item_state["hat"]:
        equipped_parts.append("Hat")
    if item_state["bowtie"]:
        equipped_parts.append("Bowtie")
    if item_state["wings"]:
        equipped_parts.append("Wings")
    if item_state["ball"]:
        equipped_parts.append("Ball")
    if item_state["laser"]:
        equipped_parts.append("Laser")
    if item_state["food_basic"] > 0 or item_state["food_premium"] > 0:
        equipped_parts.append(
            f"Food x{item_state['food_basic'] + item_state['food_premium']}"
        )
    equipped_text = ", ".join(equipped_parts) if equipped_parts else "None"

    y = 120
    if pet_view == "choose":
        if pet_types:
            selected_type = pet_types[pet_choose_index]
            draw_pet_avatar(
                screen=screen,
                pet_type=selected_type,
                stage=1,
                mood="happy",
                center_x=screen_w // 2,
                center_y=150,
                panel_color=panel_color,
                border_color=accent,
                item_state=item_state,
            )
            y = 250

        equip_surf, _ = small_font.render(f"Visual Items: {equipped_text}", fg)
        screen.blit(equip_surf, (screen_w // 2 - equip_surf.get_width() // 2, y))
        y += 28

        subtitle = "Choose Your Pet"
        subtitle_surf, _ = text_font.render(subtitle, accent)
        screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, y))
        y += 60

        visible_count = max(3, min(5, (screen_h - 360) // 70))
        start, end = get_visible_window(len(pet_types), pet_choose_index, visible_count)
        if start > 0:
            more_above_surf, _ = small_font.render("^  more above  ^", accent)
            screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, y - 28))

        for idx in range(start, end):
            pet_type = pet_types[idx]
            pet_info = pet_manager.get_pet_info(pet_type)
            if not pet_info:
                continue

            selected = idx == pet_choose_index
            color = hilite if selected else fg
            item_text = f"> {pet_info['name']}" if selected else f"  {pet_info['name']}"
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
                for line in wrap_text(small_font, pet_info["description"], screen_w - 120, accent):
                    desc_surf, _ = small_font.render(line, accent)
                    screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                    y += 22
                y += 6

        if end < len(pet_types):
            more_surf, _ = small_font.render("v  more below  v", accent)
            screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

        draw_controls_hint(
            screen=screen,
            small_font=small_font,
            text="Up/Down browse; Enter select; Esc menu",
            screen_w=screen_w,
            y=screen_h - 50,
            accent=accent,
        )
        return

    pet_status = pet_manager.get_pet_status(settings)
    draw_pet_avatar(
        screen=screen,
        pet_type=pet_status["pet_type"],
        stage=pet_status["stage"],
        mood=pet_status["mood"],
        center_x=screen_w // 2,
        center_y=150,
        panel_color=panel_color,
        border_color=accent,
        item_state=item_state,
    )
    y = 260

    equip_surf, _ = small_font.render(f"Visual Items: {equipped_text}", fg)
    screen.blit(equip_surf, (screen_w // 2 - equip_surf.get_width() // 2, y))
    y += 32

    info_lines = [
        f"Name: {pet_status['pet_name']}",
        f"Stage: {pet_status['stage_name']}",
        f"XP: {pet_status['xp']} (Next: {pet_status['xp_to_next']})",
        f"Happiness: {pet_status['happiness']}%",
        f"Mood: {pet_status['mood'].title()}",
    ]

    for line in info_lines:
        line_surf, _ = small_font.render(line, fg)
        screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
        y += 30

    y += 20
    visible_count = max(3, min(5, (screen_h - y - 90) // 40))
    start, end = get_visible_window(len(pet_options), pet_menu_index, visible_count)
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, y - 28))

    for idx in range(start, end):
        option = pet_options[idx]
        selected = idx == pet_menu_index
        color = hilite if selected else fg
        item_text = f"> {option}" if selected else f"  {option}"
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

    if end < len(pet_options):
        more_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose action; Enter select; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
