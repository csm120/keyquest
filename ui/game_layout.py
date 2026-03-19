from ui.layout import draw_centered_text


def draw_game_title(*, screen, title_font, text: str, color, screen_w: int, y: int = 18):
    """Draw a centered game title."""
    return draw_centered_text(
        screen=screen,
        font=title_font,
        text=text,
        color=color,
        screen_w=screen_w,
        y=y,
    )


def draw_centered_status_lines(
    *,
    screen,
    font,
    entries,
    screen_w: int,
    start_y: int,
    line_gap: int = 4,
):
    """Draw a centered stack of status lines and return the bounding rect."""
    rect = None
    current_y = start_y
    for text, color in entries:
        line_rect = draw_centered_text(
            screen=screen,
            font=font,
            text=text,
            color=color,
            screen_w=screen_w,
            y=current_y,
        )
        rect = line_rect if rect is None else rect.union(line_rect)
        current_y += line_rect.height + line_gap
    return rect
