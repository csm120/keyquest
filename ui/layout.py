import pygame
from typing import Optional

from ui.text_wrap import wrap_text


DEFAULT_SCREEN_SIZE = (900, 600)


def get_screen_size(screen, fallback=DEFAULT_SCREEN_SIZE):
    """Return the live screen size, or a legacy fallback when unavailable."""
    if screen is None or not hasattr(screen, "get_size"):
        return fallback
    return screen.get_size()


def center_x(screen_w: int, width: int) -> int:
    """Return the left x coordinate for centered content."""
    return screen_w // 2 - width // 2


def get_content_width(
    screen_w: int,
    *,
    side_margin: int = 70,
    min_width: int = 240,
    max_width: Optional[int] = None,
) -> int:
    """Return a safe text/content width for the current screen."""
    available = max(min_width, screen_w - (side_margin * 2))
    if max_width is None:
        return available
    return min(max_width, available)


def get_footer_y(screen_h: int, *, padding: int = 30) -> int:
    """Return a consistent footer row position."""
    return max(0, screen_h - padding)


def draw_centered_text(*, screen, font, text: str, color, screen_w: int, y: int):
    """Draw a single centered line and return its rect."""
    surf, _ = font.render(text, color)
    rect = surf.get_rect(topleft=(center_x(screen_w, surf.get_width()), y))
    screen.blit(surf, rect)
    return rect


def draw_centered_wrapped_text(
    *,
    screen,
    font,
    text: str,
    color,
    screen_w: int,
    y: int,
    max_width: Optional[int] = None,
    side_margin: int = 70,
    line_gap: int = 6,
):
    """Draw wrapped centered text and return its bounding rect."""
    content_width = get_content_width(screen_w, side_margin=side_margin, max_width=max_width)
    lines = wrap_text(font, text, content_width, color) or [text]
    rect = None
    current_y = y
    for line in lines:
        line_rect = draw_centered_text(
            screen=screen,
            font=font,
            text=line,
            color=color,
            screen_w=screen_w,
            y=current_y,
        )
        rect = line_rect if rect is None else rect.union(line_rect)
        current_y += line_rect.height + line_gap
    return rect or pygame.Rect(center_x(screen_w, 0), y, 0, 0)


def draw_left_wrapped_text(
    *,
    screen,
    font,
    text: str,
    color,
    x: int,
    y: int,
    max_width: int,
    line_gap: int = 6,
):
    """Draw wrapped left-aligned text and return its bounding rect."""
    lines = wrap_text(font, text, max_width, color) or [text]
    rect = None
    current_y = y
    for line in lines:
        surf, _ = font.render(line, color)
        line_rect = surf.get_rect(topleft=(x, current_y))
        screen.blit(surf, line_rect)
        rect = line_rect if rect is None else rect.union(line_rect)
        current_y += line_rect.height + line_gap
    return rect or pygame.Rect(x, y, 0, 0)
