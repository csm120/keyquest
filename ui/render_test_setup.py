from ui.a11y import draw_focus_frame


def draw_test_setup_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    screen_w: int,
    fg,
    accent,
    hilite,
    duration_input: str,
):
    title_surf, _ = title_font.render("Speed Test Setup", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 100))

    question_surf, _ = text_font.render("How many minutes for the test?", fg)
    screen.blit(question_surf, (screen_w // 2 - question_surf.get_width() // 2, 200))

    input_label_surf, _ = text_font.render("Type minutes:", accent)
    screen.blit(input_label_surf, (screen_w // 2 - input_label_surf.get_width() // 2, 245))

    input_text = duration_input if duration_input else "_"
    input_surf, _ = title_font.render(input_text, hilite)
    input_rect = input_surf.get_rect(topleft=(screen_w // 2 - input_surf.get_width() // 2, 280))
    screen.blit(input_surf, input_rect)
    draw_focus_frame(screen, input_rect, hilite, accent)

    instructions = [
        "",
        "Type a number (1-60 minutes)",
        "Press Enter to start",
        "Press Backspace to correct",
        "Press Escape for menu",
    ]

    y = 380
    for line in instructions:
        if line:
            text_surf, _ = small_font.render(line, accent)
            screen.blit(text_surf, (screen_w // 2 - text_surf.get_width() // 2, y))
        y += 35


def draw_practice_setup_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    screen_w: int,
    fg,
    accent,
    hilite,
    view: str,
    menu_options,
    menu_index: int,
    topic_options,
    topic_index: int,
):
    title_surf, _ = title_font.render("Sentence Practice Setup", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 80))

    if view == "menu":
        subtitle_surf, _ = text_font.render("Choose how to start", fg)
        screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, 165))

        y = 250
        for idx, option in enumerate(menu_options):
            selected = idx == menu_index
            color = hilite if selected else fg
            line_text = f"> {option}" if selected else f"  {option}"
            line_surf, _ = text_font.render(line_text, color)
            line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, y))
            screen.blit(line_surf, line_rect)
            if selected:
                draw_focus_frame(screen, line_rect, hilite, accent)
            y += 55

        instructions = [
            "Up/Down: Change option",
            "Enter/Space: Select",
            "Escape: Return to menu",
        ]
    else:
        subtitle_surf, _ = text_font.render("Select a sentence file", fg)
        screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, 165))

        visible = list(topic_options[:8])
        start = 0
        if topic_index >= 8:
            start = topic_index - 7
            visible = list(topic_options[start:start + 8])

        y = 235
        for i, topic in enumerate(visible):
            absolute_idx = start + i
            selected = absolute_idx == topic_index
            color = hilite if selected else fg
            line_text = f"> {topic}" if selected else f"  {topic}"
            line_surf, _ = small_font.render(line_text, color)
            line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, y))
            screen.blit(line_surf, line_rect)
            if selected:
                draw_focus_frame(screen, line_rect, hilite, accent)
            y += 38

        instructions = [
            "Up/Down: Browse files",
            "Enter/Space: Start with selected file",
            "Escape: Back to previous menu",
        ]

    y = 520
    for line in instructions:
        text_surf, _ = small_font.render(line, accent)
        screen.blit(text_surf, (screen_w // 2 - text_surf.get_width() // 2, y))
        y += 30
