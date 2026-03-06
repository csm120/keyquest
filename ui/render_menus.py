from ui.a11y import draw_controls_hint, draw_focus_frame, get_visible_window


def draw_main_menu(
    *,
    screen,
    title_font,
    small_font,
    menu_items,
    current_index: int,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
    unlocked_count: int,
    total_count: int,
    streak_text: str = "",
):
    visible_count = max(6, min(9, (screen_h - 240) // 50))
    start, end = get_visible_window(len(menu_items), current_index, visible_count)

    y = 120
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 90))

    for idx in range(start, end):
        item = menu_items[idx]
        selected = idx == current_index
        color = hilite if selected else fg
        item_text = f"> {item}" if selected else f"  {item}"
        text_surf, _ = title_font.render(item_text, color)
        x = screen_w // 2 - text_surf.get_width() // 2
        item_rect = text_surf.get_rect(topleft=(x, y))
        screen.blit(text_surf, item_rect)
        if selected:
            draw_focus_frame(screen, item_rect, hilite, accent)
        y += 50

    if end < len(menu_items):
        more_below_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_below_surf, (screen_w // 2 - more_below_surf.get_width() // 2, y - 8))

    info = f"Unlocked Lessons: {unlocked_count} / {total_count}"
    info_surf, _ = small_font.render(info, accent)
    info_y = min(screen_h - 110, y + 20)
    screen.blit(info_surf, (screen_w // 2 - info_surf.get_width() // 2, info_y))

    if streak_text:
        streak_surf, _ = small_font.render(streak_text, hilite)
        streak_y = min(screen_h - 80, info_y + 30)
        screen.blit(streak_surf, (screen_w // 2 - streak_surf.get_width() // 2, streak_y))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter/Space select; Ctrl+Space repeat; Esc quit",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )


def draw_lesson_menu(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    unlocked_lessons,
    lesson_names,
    current_index: int,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
):
    title = "Select a Lesson"
    title_surf, _ = title_font.render(title, fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    visible_count = max(6, min(9, (screen_h - 240) // 40))
    start, end = get_visible_window(len(unlocked_lessons), current_index, visible_count)

    y = 120
    if start > 0:
        more_above_surf, _ = small_font.render("^  more above  ^", accent)
        screen.blit(more_above_surf, (screen_w // 2 - more_above_surf.get_width() // 2, 90))

    for idx in range(start, end):
        lesson_num = unlocked_lessons[idx]
        if lesson_num < len(lesson_names):
            lesson_name = lesson_names[lesson_num]
        else:
            lesson_name = f"Lesson {lesson_num}"
        text = f"Lesson {lesson_num}: {lesson_name}"

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

    if end < len(unlocked_lessons):
        more_surf, _ = small_font.render("v  more below  v", accent)
        screen.blit(more_surf, (screen_w // 2 - more_surf.get_width() // 2, min(screen_h - 95, y - 8)))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter select; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )


def draw_games_menu(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    games,
    current_index: int,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
):
    title = "Select a Game"
    title_surf, _ = title_font.render(title, fg)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 50))

    y = 120
    for idx, game in enumerate(games):
        text = f"{game.NAME}"

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
            desc_surf, _ = small_font.render(game.DESCRIPTION, accent)
            screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width() // 2, y))
            y += 30

        if y > screen_h - 150:
            break

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Up/Down choose; Enter select; H hotkeys; Esc menu",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
