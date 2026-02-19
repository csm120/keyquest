from ui.a11y import draw_controls_hint, draw_focus_frame


def draw_test_screen(
    *,
    screen,
    text_font,
    small_font,
    screen_w: int,
    fg,
    accent,
    current_text: str,
    typed_text: str,
    remaining_seconds: int,
):
    current_label_surf, _ = small_font.render("Type now:", accent)
    screen.blit(current_label_surf, (screen_w // 2 - current_label_surf.get_width() // 2, 170))

    cur_surf, _ = text_font.render(current_text, accent)
    cur_rect = cur_surf.get_rect(topleft=(screen_w // 2 - cur_surf.get_width() // 2, 200))
    screen.blit(cur_surf, cur_rect)
    draw_focus_frame(screen, cur_rect, accent, fg)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, 245))

    typed_display = typed_text if typed_text else "_"
    typed_surf, _ = text_font.render(typed_display, fg)
    screen.blit(typed_surf, (screen_w // 2 - typed_surf.get_width() // 2, 270))

    time_msg = f"{int(remaining_seconds):>2}s left"
    time_surf, _ = small_font.render(time_msg, accent)
    screen.blit(time_surf, (screen_w // 2 - time_surf.get_width() // 2, 320))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Ctrl+Space repeat; Esc menu",
        screen_w=screen_w,
        y=350,
        accent=accent,
    )


def draw_practice_screen(
    *,
    screen,
    text_font,
    small_font,
    screen_w: int,
    fg,
    accent,
    current_text: str,
    typed_text: str,
    elapsed_seconds: float,
    sentences_completed: int,
):
    current_label_surf, _ = small_font.render("Type now:", accent)
    screen.blit(current_label_surf, (screen_w // 2 - current_label_surf.get_width() // 2, 170))

    cur_surf, _ = text_font.render(current_text, accent)
    cur_rect = cur_surf.get_rect(topleft=(screen_w // 2 - cur_surf.get_width() // 2, 200))
    screen.blit(cur_surf, cur_rect)
    draw_focus_frame(screen, cur_rect, accent, fg)

    typed_label_surf, _ = small_font.render("You typed:", accent)
    screen.blit(typed_label_surf, (screen_w // 2 - typed_label_surf.get_width() // 2, 245))

    typed_display = typed_text if typed_text else "_"
    typed_surf, _ = text_font.render(typed_display, fg)
    screen.blit(typed_surf, (screen_w // 2 - typed_surf.get_width() // 2, 270))

    minutes = int(elapsed_seconds // 60)
    seconds = int(elapsed_seconds % 60)
    time_msg = f"Time: {minutes}:{seconds:02d}"
    time_surf, _ = small_font.render(time_msg, accent)
    screen.blit(time_surf, (screen_w // 2 - time_surf.get_width() // 2, 320))

    sentence_msg = f"Sentences completed: {sentences_completed}"
    sentence_surf, _ = small_font.render(sentence_msg, accent)
    screen.blit(sentence_surf, (screen_w // 2 - sentence_surf.get_width() // 2, 360))

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Ctrl+Space repeat; Esc x3 finish",
        screen_w=screen_w,
        y=400,
        accent=accent,
    )
