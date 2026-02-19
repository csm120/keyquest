from modules import pet_manager
from modules import shop_manager
from ui.a11y import draw_controls_hint, draw_focus_frame
from ui.pet_visuals import draw_pet_avatar


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
    title_surf, _ = title_font.render(title, fg)
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

        for idx, pet_type in enumerate(pet_types):
            pet_info = pet_manager.get_pet_info(pet_type)
            if not pet_info:
                continue

            selected = idx == pet_choose_index
            color = hilite if selected else fg
            item_text = f"> {pet_info['name']}" if selected else f"  {pet_info['name']}"
            text_surf, _ = text_font.render(item_text, color)
            x = screen_w // 2 - text_surf.get_width() // 2
            item_rect = text_surf.get_rect(topleft=(x, y))
            screen.blit(text_surf, item_rect)
            if selected:
                draw_focus_frame(screen, item_rect, hilite, accent)
            y += 40

            if selected:
                desc_surf, _ = small_font.render(pet_info["description"], accent)
                screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
                y += 30

            if y > screen_h - 150:
                break

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
    for idx, option in enumerate(pet_options):
        selected = idx == pet_menu_index
        color = hilite if selected else fg
        item_text = f"> {option}" if selected else f"  {option}"
        text_surf, _ = text_font.render(item_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        item_rect = text_surf.get_rect(topleft=(x, y))
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
        y += 40

        if y > screen_h - 100:
            break

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose action; Enter select; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
