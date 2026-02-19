from ui.a11y import draw_controls_hint, draw_focus_frame


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
    y = 120
    for idx, item in enumerate(menu_items):
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

    info = f"Unlocked Lessons: {unlocked_count} / {total_count}"
    info_surf, _ = small_font.render(info, accent)
    screen.blit(info_surf, (screen_w // 2 - info_surf.get_width() // 2, y + 20))

    if streak_text:
        streak_surf, _ = small_font.render(streak_text, hilite)
        screen.blit(streak_surf, (screen_w // 2 - streak_surf.get_width() // 2, y + 50))

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

    y = 120
    for idx, lesson_num in enumerate(unlocked_lessons):
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

        if y > screen_h - 100:
            break

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
