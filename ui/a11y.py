import pygame


def draw_focus_frame(screen, target_rect, hilite, accent):
    """Draw a high-visibility focus frame that does not rely on color only."""
    outer = target_rect.inflate(28, 14)
    inner = target_rect.inflate(14, 8)
    pygame.draw.rect(screen, accent, outer, width=1, border_radius=8)
    pygame.draw.rect(screen, hilite, inner, width=3, border_radius=8)


def draw_controls_hint(*, screen, small_font, text, screen_w: int, y: int, accent):
    """Draw a consistent controls row across screens."""
    message = f"Controls: {text}"
    surf, _ = small_font.render(message, accent)
    x = screen_w // 2 - surf.get_width() // 2
    screen.blit(surf, (x, y))

