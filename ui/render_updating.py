"""Render the in-app update progress screen."""

from ui.a11y import draw_active_panel, draw_controls_hint, draw_secondary_panel


def _format_size(byte_count: int) -> str:
    if byte_count <= 0:
        return "0 KB"
    units = ["B", "KB", "MB", "GB"]
    size = float(byte_count)
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.1f} {units[unit_index]}"


def draw_updating_screen(
    *,
    screen,
    title_font,
    text_font,
    small_font,
    wrap_text,
    screen_w: int,
    screen_h: int,
    fg,
    accent,
    hilite,
    status_text: str,
    downloaded_bytes: int,
    total_bytes: int,
):
    title_surf, _ = title_font.render("Updating KeyQuest", hilite)
    screen.blit(title_surf, (screen_w // 2 - title_surf.get_width() // 2, 90))

    subtitle_surf, _ = text_font.render("Please wait", accent)
    screen.blit(subtitle_surf, (screen_w // 2 - subtitle_surf.get_width() // 2, 150))

    y = 240
    for line in wrap_text(status_text, screen_w - 140):
        line_surf, _ = small_font.render(line, fg)
        line_rect = line_surf.get_rect(topleft=(screen_w // 2 - line_surf.get_width() // 2, y))
        if y == 240:
            draw_active_panel(screen, line_rect, accent, fg)
        screen.blit(line_surf, line_rect)
        y += 34

    if total_bytes > 0:
        progress_text = f"Downloaded {_format_size(downloaded_bytes)} of {_format_size(total_bytes)}"
        progress_surf, _ = small_font.render(progress_text, accent)
        progress_rect = progress_surf.get_rect(topleft=(screen_w // 2 - progress_surf.get_width() // 2, y + 20))
        draw_secondary_panel(screen, progress_rect, accent, fg)
        screen.blit(progress_surf, progress_rect)

    note_lines = [
        "Do not close KeyQuest.",
        "The installer will run silently and restart the program when it finishes.",
    ]
    y = screen_h - 110
    for line in note_lines:
        line_surf, _ = small_font.render(line, accent)
        screen.blit(line_surf, (screen_w // 2 - line_surf.get_width() // 2, y))
        y += 28

    draw_controls_hint(
        screen=screen,
        small_font=small_font,
        text="Update in progress. Please wait",
        screen_w=screen_w,
        y=screen_h - 50,
        accent=accent,
    )
